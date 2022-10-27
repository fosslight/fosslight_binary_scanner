#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
from fosslight_util.help import PrintHelpMsg

_HELP_MESSAGE_BINARY = """
    Usage: fosslight_bin [option1] <arg1> [option2] <arg2>...

    After extracting the binaries, the open source and license information of the saved binaries are retrieved by comparing the similarity
    with the binaries stored in the Binary DB (FOSSLight > Binary DB) with the Binary's TLSH (Trend micro Locality Sensitive Hash).

    Options:
        -p <binary_path>\t\t    Path to analyze binaries (Default: current directory)
        -h\t\t\t\t    Print help message
        -v\t\t\t\t    Print FOSSLight Binary Scanner version
        -o <output_path>\t\t    Output path
        \t\t\t\t    (If you want to generate the specific file name, add the output path with file name.)
        -f <format>\t\t\t    Output file format (excel, csv, opossum, yaml)
        -d <db_url>\t\t\t    DB Connection(format :'postgresql://username:password@host:port/database_name')
        --notice\t\t\t    Print the open source license notice text."""


def print_help_msg():
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_BINARY)
    helpMsg.print_help_msg(True)
