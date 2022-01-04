#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import pkg_resources
import sys
from fosslight_util.help import PrintHelpMsg

_HELP_MESSAGE_BINARY = """
    Usage: fosslight_bin [option1] <arg1> [option2] <arg2>...

    After extracting the binaries, the open source and license information of the saved binaries are retrieved by comparing the similarity
    with the binaries stored in the Binary DB (FOSSLight > Binary DB) with the Binary's TLSH (Trend micro Locality Sensitive Hash).

    Mandatory:
        -p <binary_path>\t\t    Path to analyze binaries

    Options:
        -h\t\t\t\t    Print help message
        -v\t\t\t\t    Print FOSSLight Binary Scanner version
        -a <target_architecture>\t    Target Architecture(x86-64, ARM, MIPS, Mach-O, and etc.)
        -o <output_path>\t\t    Output path
        \t\t\t\t    (If you want to generate the specific file name, add the output path with file name.)
        -f <format>\t\t\t    Output file format (excel, csv, opossum)
        -d <db_url>\t\t\t    DB Connection(format :'postgresql://username:password@host:port/database_name')"""


def print_help_msg():
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_BINARY)
    helpMsg.print_help_msg(True)

def print_package_version(pkg_name):
    cur_version = pkg_resources.get_distribution(pkg_name).version
    print(f'FOSSLight Binary Scanner Version : {cur_version}')
    sys.exit(0)