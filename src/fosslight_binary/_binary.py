#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
from fosslight_util.oss_item import FileItem
import Levenshtein

EXCLUDE_TRUE_VALUE = "Exclude"
TLSH_CHECKSUM_NULL = "0"


def find_most_similar_word(input_string, oss_name_list):
    most_similar_word = None
    min_distance = float('inf')

    for oss in oss_name_list:
        distance = Levenshtein.distance(input_string, oss.name)
        if distance < min_distance:
            min_distance = distance
            most_similar_word = oss.name
    return most_similar_word


class VulnerabilityItem:
    file_path = ""
    vul_id = ""
    nvd_url = ""
    oss_items = []

    def __init__(self, file_path, id, url, oss_items):
        self.file_path = file_path
        self.vul_id = id
        self.nvd_url = url
        self.oss_items = oss_items


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

    def get_vulnerability_items(self, oss_name):
        nvd_url = []
        nvd_urls = ""
        nvd_url_dict = {}

        for vul_item in self.vulnerability_items:
            found_oss_name = ""

            if vul_item.file_path == self.source_name_or_path:
                if len(self.oss_items) > 1:
                    if vul_item.nvd_url:
                        found_oss_name = find_most_similar_word(vul_item.nvd_url, vul_item.oss_items)
                        if oss_name == found_oss_name:
                            nvd_urls = f"{nvd_urls}\n{vul_item.nvd_url}"
                else:
                    nvd_url = nvd_url_dict.get(vul_item.file_path)
                    if nvd_url:
                        nvd_url.append(vul_item.nvd_url)
                        nvd_urls = "\n".join(nvd_url)
                    else:
                        nvd_url_dict[vul_item.file_path] = [vul_item.nvd_url]
                        nvd_urls = "\n".join(nvd_url_dict[vul_item.file_path])
        return nvd_urls.strip()

    def get_print_binary_only(self):
        return (self.source_name_or_path + "\t" + self.checksum + "\t" + self.tlsh)

    def get_print_array(self):
        items = []
        if self.oss_items:
            for oss in self.oss_items:
                lic = ",".join(oss.license)
                exclude = EXCLUDE_TRUE_VALUE if (self.exclude or oss.exclude) else ""
                nvd_url = self.get_vulnerability_items(oss.name)
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
