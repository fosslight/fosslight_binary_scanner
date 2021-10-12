#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import hashlib
import tlsh
from io import open

_EXCLUDE_TRUE_VALUE = "Exclude"
_TLSH_CHECKSUM_NULL = "0"


class OssItem:
    name = ""
    version = ""
    license = ""

    def __init__(self, name, version, license):
        self.name = name
        self.version = version
        self.license = license


class BinaryItem:
    bin_name = ""
    binary_name_without_path = ""
    binary_strip_root = ""  # Value of binary name column
    tlsh = _TLSH_CHECKSUM_NULL
    checksum = _TLSH_CHECKSUM_NULL
    oss_items = []
    exclude = ""

    def __init__(self, value):
        self.exclude = ""
        self.binary_strip_root = ""
        self.checksum = _TLSH_CHECKSUM_NULL
        self.tlsh = _TLSH_CHECKSUM_NULL
        self.oss_items = []
        self.binary_name_without_path = ""
        self.set_bin_name(value)

    def __del__(self):
        pass

    def set_oss_items(self, value):
        self.oss_items.append(value)

    def set_bin_name(self, value):
        self.bin_name = value

    def set_exclude(self, value):
        self.exclude = _EXCLUDE_TRUE_VALUE if value else ""

    def set_checksum(self, value):
        self.checksum = value

    def set_tlsh(self, value):
        self.tlsh = value

    def get_print_binary_only(self):
        return (self.binary_strip_root + "\t" + self.checksum + "\t" + self.tlsh)

    def get_print_oss_report(self):
        print_rows = []
        if len(self.oss_items) > 0:
            for oss in self.oss_items:
                print_rows.append([self.binary_strip_root, oss.name, oss.version,
                                   oss.license, '', '', '', self.exclude, ''])
        else:
            print_rows.append([self.binary_strip_root, '',
                               '', '', '', '', '', self.exclude, ''])

        return print_rows

    def set_checksum_tlsh(self):
        self.checksum, self.tlsh, error, msg = get_checksum_and_tlsh(
            self.bin_name)
        return error, msg


def get_checksum_and_tlsh(bin_with_path):
    checksum_value = _TLSH_CHECKSUM_NULL
    tlsh_value = _TLSH_CHECKSUM_NULL
    error_msg = ""
    error = False
    try:
        f = open(bin_with_path, "rb")
        byte = f.read()
        sha1_hash = hashlib.sha1(byte)
        checksum_value = str(sha1_hash.hexdigest())
        try:
            tlsh_value = str(tlsh.hash(byte))
        except:
            tlsh_value = _TLSH_CHECKSUM_NULL
        f.close()
    except Exception as ex:
        error_msg = "(Error) Get_checksum, tlsh:" + str(ex)
        error = True
    return checksum_value, tlsh_value, error, error_msg
