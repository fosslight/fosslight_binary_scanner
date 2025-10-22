#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

import logging
import json
import os
import sys
import subprocess
import fosslight_util.constant as constant
from fosslight_binary._binary import BinaryItem, VulnerabilityItem, is_package_dir
from fosslight_util.oss_item import OssItem

logger = logging.getLogger(constant.LOGGER_NAME)


def run_analysis(command):
    try:
        result = subprocess.run(command, text=True, timeout=600)
        if result.returncode != 0:
            logger.error(f"dependency-check failed with return code {result.returncode}")
            raise Exception(f"dependency-check failed with return code {result.returncode}")
    except subprocess.TimeoutExpired:
        logger.error("dependency-check command timed out")
        raise
    except Exception as ex:
        logger.error(f"Run Analysis : {ex}")
        raise


def get_oss_ver(version_info):
    oss_version = ""
    if version_info.get('source') == 'central':
        if version_info.get('name') == 'version':
            oss_version = version_info.get('value')
    elif version_info.get('source') == 'pom':
        if version_info.get('name') == 'version':
            oss_version = version_info.get('value')
    elif version_info.get('source', "").lower() == 'manifest':
        if version_info.get('name') == 'Implementation-Version' or version_info.get('name') == 'Bundle-Version':
            oss_version = version_info.get('value')
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


def merge_oss_and_vul_items(bin, key, oss_list, vulnerability_items):
    bin.set_oss_items(oss_list)
    if vulnerability_items and vulnerability_items.get(key):
        bin.vulnerability_items.extend(vulnerability_items.get(key, []))


def merge_binary_list(owasp_items, vulnerability_items, bin_list):
    not_found_bin = []

    # key : file_path / value : {"oss_list": [oss], "sha1": sha1} for one binary
    for key, value in owasp_items.items():
        found = False
        oss_list = value["oss_list"]
        sha1 = value.get("sha1", "")
        for bin in bin_list:
            if bin.source_name_or_path == key:
                found = True
                for oss in oss_list:
                    if oss.name and oss.license:
                        bin.found_in_owasp = True
                        break
                merge_oss_and_vul_items(bin, key, oss_list, vulnerability_items)
            else:
                if bin.checksum == sha1:
                    merge_oss_and_vul_items(bin, key, oss_list, vulnerability_items)

        if not found:
            bin_item = BinaryItem(os.path.abspath(key))
            bin_item.binary_name_without_path = os.path.basename(key)
            bin_item.source_name_or_path = key

            is_pkg, _ = is_package_dir(bin_item.source_name_or_path, '')
            if is_pkg:
                continue

            bin_item.set_oss_items(oss_list)
            not_found_bin.append(bin_item)

    bin_list += not_found_bin
    return bin_list


def get_vulnerability_info(file_with_path, vulnerability, vulnerability_items, remove_vulnerability_items):
    if vulnerability:
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


def get_oss_groupid(evidence_info):
    oss_groupid = ""
    # First, Get groupid from Central, else get it from pom
    if evidence_info.get('source') == 'central':
        if evidence_info.get('name') == 'groupid':
            oss_groupid = evidence_info.get('value')
    elif evidence_info.get('source') == 'pom':
        if evidence_info.get('name') == 'groupid':
            oss_groupid = evidence_info.get('value')
    return oss_groupid


def get_oss_artifactid(evidence_info):
    oss_artifactid = ""
    # Get OSS Info from POM
    if evidence_info.get('source') == 'pom':
        if evidence_info.get('name') == 'artifactid':
            oss_artifactid = evidence_info.get('value')
    return oss_artifactid


def get_oss_dl_url(evidence_info):
    oss_dl_url = ""
    if evidence_info.get('name') == 'url':
        oss_dl_url = evidence_info.get('value')
    return oss_dl_url


def get_oss_info_from_pkg_info(pkg_info):
    oss_name = ""
    oss_version = ""

    try:
        if pkg_info.get('id') != "":
            # Get OSS Name
            if pkg_info.get('id').startswith('pkg:maven'):
                # ex, pkg:maven/com.hankcs/aho-corasick-double-array-trie@1.2.3
                oss_name = pkg_info.get('id').split('@')[0]
                oss_name = f"{oss_name.split('/')[-2]}:{oss_name.split('/')[-1]}"
            elif pkg_info.get('id').startswith('pkg:npm'):
                # ex, pkg:npm/cryptiles@0.2.2
                oss_name = pkg_info.get('id').split('@')[0]
                oss_name = oss_name.replace('pkg:npm', 'npm')
                oss_name = oss_name.replace('/', ':')
            else:
                oss_name = pkg_info.get('id').split('@')[0]
                oss_name = oss_name.split('/')[-1]
            # Get OSS Version
            oss_version = pkg_info.get('id').split('@')[1]
    except Exception as ex:
        logger.debug(f"Error to get value for oss name and version: {ex}")
    return oss_name, oss_version


def analyze_jar_file(path_to_find_bin, path_to_exclude):
    owasp_items = {}
    remove_vulnerability_items = []
    vulnerability_items = {}
    success = True
    json_file = ""

    # Use fixed install path: ./fosslight_dc_bin/dependency-check/bin/dependency-check.sh or .bat
    if sys.platform.startswith('win'):
        depcheck_path = os.path.abspath(os.path.join(os.getcwd(), 'fosslight_dc_bin', 'dependency-check', 'bin', 'dependency-check.bat'))
    elif sys.platform.startswith('linux'):
        depcheck_path = os.path.abspath(os.path.join(os.getcwd(), 'fosslight_dc_bin', 'dependency-check', 'bin', 'dependency-check.sh'))
    elif sys.platform.startswith('darwin'):
        depcheck_path = os.path.abspath(os.path.join(os.getcwd(), 'dependency-check'))

    if not (os.path.isfile(depcheck_path) and os.access(depcheck_path, os.X_OK)):
        logger.error(f'dependency-check script not found or not executable at {depcheck_path}')
        success = False
        return owasp_items, vulnerability_items, success

    command = [depcheck_path, '--scan', f'{path_to_find_bin}', '--out', f'{path_to_find_bin}',
               '--disableArchive', '--disableAssembly', '--disableRetireJS', '--disableNodeJS',
               '--disableNodeAudit', '--disableNugetconf', '--disableNuspec', '--disableOpenSSL',
               '--disableOssIndex', '--disableBundleAudit', '--disableOssIndex', '--nvdValidForHours', '168',
               '--nvdDatafeed', 'https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-{0}.json.gz', '-f', 'JSON']

    try:
        run_analysis(command)
    except Exception as ex:
        logger.info(f"Error to analyze .jar file - OSS information for .jar file isn't included in report.\n {ex}")
        success = False
        return owasp_items, vulnerability_items, success

    try:
        json_file = os.path.join(path_to_find_bin, 'dependency-check-report.json')
        with open(json_file, 'r') as f:
            jar_contents = json.load(f)
    except Exception as ex:
        logger.debug(f"Error to read dependency-check-report.json file : {ex}")
        success = False
        return owasp_items, vulnerability_items, success

    dependencies = jar_contents.get("dependencies", [])

    try:
        for val in dependencies:
            bin_with_path = ""
            oss_name = ""
            oss_ver = ""
            oss_artifactid = ""
            oss_groupid = ""
            oss_dl_url = ""
            oss_license = get_oss_lic_in_jar(val)
            oss_name_found = False

            sha1 = val.get("sha1", "")

            all_evidence = val.get("evidenceCollected", {})
            vulnerability = val.get("vulnerabilityIds", [])
            all_pkg_info = val.get("packages", [])

            vendor_evidences = all_evidence.get('vendorEvidence', [])
            version_evidences = all_evidence.get('versionEvidence', [])

            # Check if the file is .jar file
            # Even if the oss info is from pom.xml in jar file, the file name will be .jar file.
            # But the oss info from pom.xml could be different from .jar file.
            bin_with_path = val.get("filePath")

            if any(os.path.commonpath([bin_with_path, exclude_path]) == exclude_path
                   for exclude_path in path_to_exclude):
                continue

            if not bin_with_path.endswith('.jar'):
                bin_with_path = bin_with_path.split('.jar')[0] + '.jar'

            try:
                path_to_fild_bin_abs = os.path.abspath(path_to_find_bin)
                bin_with_path_abs = os.path.abspath(bin_with_path)
                if os.name == 'nt':  # Windows
                    drive_bin = os.path.splitdrive(bin_with_path_abs)[0].lower()
                    drive_root = os.path.splitdrive(path_to_fild_bin_abs)[0].lower()
                    # Different drive or UNC root -> fallback to basename
                    if drive_bin and drive_root and drive_bin != drive_root:
                        file_with_path = os.path.basename(bin_with_path_abs)
                    else:
                        file_with_path = os.path.relpath(bin_with_path_abs, path_to_fild_bin_abs)
                else:
                    file_with_path = os.path.relpath(bin_with_path_abs, path_to_fild_bin_abs)
            except Exception as e:
                file_with_path = os.path.basename(bin_with_path)
                logger.error(f"relpath error: {e}; fallback basename: {file_with_path}")

            # First, Get OSS Name and Version info from pkg_info
            for pkg_info in all_pkg_info:
                oss_name, oss_ver = get_oss_info_from_pkg_info(pkg_info)

            if oss_name == "" and oss_ver == "":
                # If can't find name and version, Find thoes in vendorEvidence and versionEvidence .
                # Get Version info from versionEvidence
                for version_info in version_evidences:
                    oss_ver = get_oss_ver(version_info)

                # Get Artifact ID, Group ID, OSS Name from vendorEvidence
                for vendor_info in vendor_evidences:
                    if oss_groupid == "":
                        oss_groupid = get_oss_groupid(vendor_info)
                    if oss_artifactid == "":
                        oss_artifactid = get_oss_artifactid(vendor_info)
                    if oss_dl_url == "":
                        oss_dl_url = get_oss_dl_url(vendor_info)
                    # Combine groupid and artifactid
                    if oss_artifactid != "" and oss_groupid != "":
                        oss_name = f"{oss_groupid}:{oss_artifactid}"
                        oss_name_found = True
                    # If oss_name is found, break
                    if oss_name_found:
                        break
            else:
                # Get only dl_url from vendorEvidence
                for vendor_info in vendor_evidences:
                    if oss_dl_url == "":
                        oss_dl_url = get_oss_dl_url(vendor_info)

            # Get Vulnerability Info.
            vulnerability_items = get_vulnerability_info(file_with_path, vulnerability, vulnerability_items, remove_vulnerability_items)

            if oss_name or oss_license or oss_dl_url:
                oss = OssItem(oss_name, oss_ver, oss_license, oss_dl_url)
                oss.comment = "OWASP result"

                if file_with_path in owasp_items:
                    owasp_items[file_with_path]["oss_list"].append(oss)
                    # Update sha1 if not already set or if current sha1 is empty
                    if not owasp_items[file_with_path]["sha1"] and sha1:
                        owasp_items[file_with_path]["sha1"] = sha1
                else:
                    owasp_items[file_with_path] = {
                        "oss_list": [oss],
                        "sha1": sha1
                    }
    except Exception as ex:
        logger.debug(f"Error to get dependency Info in jar_contents: {ex}")

    try:
        if os.path.isfile(json_file):
            os.remove(json_file)
    except Exception as ex:
        logger.debug(f"Error - There is no .json file : {ex}")
    return owasp_items, vulnerability_items, success
