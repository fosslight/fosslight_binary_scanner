#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
from fosslight_util.oss_item import FileItem

EXCLUDE_TRUE_VALUE = "Exclude"
TLSH_CHECKSUM_NULL = "0"


class VulnerabilityItem:
    file_path = ""
    vul_id = ""
    nvd_url = ""

    def __init__(self, file_path, id, url):
        self.file_path = file_path
        self.vul_id = id
        self.nvd_url = url


class BinaryItem(FileItem):
    def __init__(self, value):
        super().__init__("")
        self.exclude = False
        self.source_name_or_path = ""
        self.tlsh = TLSH_CHECKSUM_NULL
        self.vulnerability_items = []
        self.binary_name_without_path = ""
        self.bin_name_with_path = value
        self.found_in_owasp = False
        self.is_binary = True

    def __del__(self):
        pass

    def set_oss_items(self, new_oss_list, exclude=False, exclude_msg=""):
        if exclude:
            for oss in new_oss_list:
                oss.exclude = True
                oss.comment = exclude_msg
        # Append New input OSS
        self.oss_items.extend(new_oss_list)

    def get_vulnerability_items(self):
        nvd_url = [vul_item.nvd_url for vul_item in self.vulnerability_items]
        return ", ".join(nvd_url)

    def get_print_binary_only(self):
        return (self.source_name_or_path + "\t" + self.checksum + "\t" + self.tlsh)

    def get_print_array(self):
        items = []
        if self.oss_items:
            for oss in self.oss_items:
                lic = ",".join(oss.license)
                exclude = EXCLUDE_TRUE_VALUE if (self.exclude or oss.exclude) else ""
                nvd_url = self.get_vulnerability_items()
                items.append([self.source_name_or_path, oss.name, oss.version,
                              lic, oss.download_location, oss.homepage,
                              oss.copyright, exclude, oss.comment,
                              nvd_url, self.tlsh, self.checksum])
        else:
            exclude = EXCLUDE_TRUE_VALUE if self.exclude else ""
            items.append([self.source_name_or_path, '',
                          '', '', '', '', '', exclude, self.comment, '',
                          self.tlsh, self.checksum])
        return items

    def get_print_json(self):
        items = []
        if self.oss_items:
            for oss in self.oss_items:
                json_item = {}
                json_item["name"] = oss.name
                json_item["version"] = oss.version

                if self.source_name_or_path:
                    json_item["source path"] = self.source_name_or_path
                if len(oss.license) > 0:
                    json_item["license"] = oss.license
                if oss.download_location:
                    json_item["download location"] = oss.download_location
                if oss.homepage:
                    json_item["homepage"] = oss.homepage
                if oss.copyright:
                    json_item["copyright text"] = oss.copyright
                if self.exclude or oss.exclude:
                    json_item["exclude"] = True
                if oss.comment:
                    json_item["comment"] = oss.comment
                items.append(json_item)
        else:
            json_item = {}
            if self.source_name_or_path:
                json_item["source path"] = self.source_name_or_path
            if self.exclude:
                json_item["exclude"] = True
            if self.comment:
                json_item["comment"] = self.comment
        return items
