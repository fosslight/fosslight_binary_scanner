#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

import logging
import json
import os
import sys
import fosslight_util.constant as constant
from ._binary import BinaryItem, OssItem, VulnerabilityItem
from dependency_check import run as dependency_check_run


logger = logging.getLogger(constant.LOGGER_NAME)


def run_analysis(params, func):
    try:
        sys.argv = params
        func()
    except SystemExit:
        pass
    except Exception as ex:
        logger.error(f"Run Analysis : {ex}")


def get_oss_ver(version):
    oss_version = ""

    if version['source'] == 'pom':
        if version['name'] == 'version':
            oss_version = version['value']

    return oss_version


def get_oss_lic_in_jar(data):
    license = ""
    license_raw = str(data.get("license"))
    split_lic = license_raw.split(':')[0]

    # Not NoneType but string 'None'
    if license_raw == "None":
        license = ""
    else:
        if not split_lic.startswith('http'):
            license = split_lic.replace(',', '')
        else:
            license = license_raw

    return license


def merge_binary_list(owasp_items, vulnerability_items, bin_list):
    not_found_bin = []

    # key : file_path / value : oss_list for one binary
    for key, value in owasp_items.items():
        found = False
        for bin in bin_list:
            if bin.binary_strip_root == key:
                bin.set_oss_items(value, False)
                if vulnerability_items is not None:
                    bin.set_vulnerability_items(vulnerability_items.get(key))
                found = True
                break

        if not found:
            bin_item = BinaryItem(os.path.abspath(key))
            bin_item.binary_name_without_path = os.path.basename(key)
            bin_item.binary_strip_root = key
            bin_item.set_oss_items(value)
            not_found_bin.append(bin_item)

    bin_list += not_found_bin
    return bin_list


def get_vulnerability_info(file_with_path, vulnerability, vulnerability_items, remove_vulnerability_items):
    if vulnerability is not None:
        try:
            for vul_info in vulnerability:
                vul_id = ""
                nvd_url = ""
                for key, val in vul_info.items():
                    if key == 'id':
                        vul_id = val
                    elif key == 'url':
                        nvd_url = val

                vul_item = VulnerabilityItem(file_with_path, vul_id, nvd_url)

                remove_vulnerability_items = vulnerability_items.get(file_with_path)
                if remove_vulnerability_items:
                    remove_vulnerability_items.append(vul_item)
                else:
                    vulnerability_items[file_with_path] = [vul_item]
        except Exception as ex:
            logger.info(f"Error to get vul_id and nvd_url: {ex}")

    return vulnerability_items


def analyze_jar_file(path_to_find_bin):
    remove_owasp_item = []
    owasp_items = {}
    remove_vulnerability_items = []
    vulnerability_items = {}
    success = True

    command = ['dependency-check', '--scan', f'{path_to_find_bin}', '--out', f'{path_to_find_bin}',
               '--disableArchive', '--disableAssembly', '--disableRetireJS', '--disableNodeJS',
               '--disableNodeAudit', '--disableNugetconf', '--disableNuspec', '--disableOpenSSL',
               '--disableOssIndex', '--disableBundleAudit', '--cveValidForHours', '24', '-f', 'ALL']
    run_analysis(command, dependency_check_run)

    try:
        json_file = os.path.join(path_to_find_bin, 'dependency-check-report.json')
        with open(json_file, 'r') as f:
            jar_contents = json.load(f)
    except Exception as ex:
        logger.debug(f"Error to read dependency-check-report.json file : {ex}")
        success = False
        return owasp_items, vulnerability_items, success

    dependencies = jar_contents.get("dependencies")
    try:
        for val in dependencies:
            bin_with_path = ""
            oss_name = ""
            oss_ver = ""
            oss_artifactid = ""
            oss_groupid = ""
            oss_dl_url = ""
            oss_license = get_oss_lic_in_jar(val)
            get_oss_info = False

            all_evidence = val.get("evidenceCollected")
            vulnerability = val.get("vulnerabilityIds")
            vendor_evidences = all_evidence.get('vendorEvidence')
            product_evidences = all_evidence.get('productEvidence')
            version_evidences = all_evidence.get('versionEvidence')

            # Check if the file is .jar file
            # Even if the oss info is from pom.xml in jar file, the file name will be .jar file.
            # But the oss info from pom.xml could be different from .jar file.
            bin_with_path = val.get("filePath")
            if not bin_with_path.endswith('.jar'):
                bin_with_path = bin_with_path.split('.jar')[0] + '.jar'

            file_with_path = os.path.relpath(bin_with_path, path_to_find_bin)
            # Get Version info from versionEvidence
            for version_info in version_evidences:
                oss_ver = get_oss_ver(version_info)

            # Get Artifact ID, Group ID, OSS Name from vendorEvidence
            for vendor_info in vendor_evidences:
                # Get OSS Info from POM
                if vendor_info['source'] == 'pom':
                    if vendor_info['name'] == 'artifactid':
                        oss_artifactid = vendor_info['value']
                    if vendor_info['name'] == 'groupid':
                        oss_groupid = vendor_info['value']
                    if vendor_info['name'] == 'url':
                        oss_dl_url = vendor_info['value']
                    if oss_artifactid != "" and oss_groupid != "":
                        oss_name = f"{oss_groupid}:{oss_artifactid}"

            # Check if get oss_name and version from pom
            if oss_name != "" and oss_ver != "":
                get_oss_info = True

            # If there is no pom.mxl in .jar file, get oss info from MANIFEST.MF file
            if get_oss_info is False:
                for product_info in product_evidences:
                    if product_info['source'] == 'Manifest':
                        if oss_name == "" and (product_info['name'] == 'Implementation-Title' or product_info['name'] == 'specification-title'):
                            oss_name = product_info['value']
                        if oss_ver == "" and (product_info['name'] == 'Implementation-Version' or product_info['name'] == 'Bundle-Version'):
                            oss_ver = product_info['value']

            # Get Vulnerability Info.
            vulnerability_items = get_vulnerability_info(file_with_path, vulnerability, vulnerability_items, remove_vulnerability_items)

            if oss_name != "" or oss_ver != "" or oss_license != "" or oss_dl_url != "":
                oss = OssItem(oss_name, oss_ver, oss_license, oss_dl_url)
                oss.set_comment("OWASP Result. ")

                remove_owasp_item = owasp_items.get(file_with_path)
                if remove_owasp_item:
                    remove_owasp_item.append(oss)
                else:
                    owasp_items[file_with_path] = [oss]
    except Exception as ex:
        logger.debug(f"Error to get depency Info in jar_contets: {ex}")
        success = False

    return owasp_items, vulnerability_items, success
