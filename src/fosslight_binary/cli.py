#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import argparse
import sys
import os
from fosslight_util.help import print_package_version
from fosslight_binary._help import print_help_msg
from fosslight_binary.binary_analysis import find_binaries
from fosslight_util.timer_thread import TimerThread

_PKG_NAME = "fosslight_binary"


def main():
    global windows
    path_to_find_bin = ""
    output_dir = ""
    format = ""
    db_url = ""

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true', required=False)
    parser.add_argument('-v', '--version', action='store_true', required=False)
    parser.add_argument('-p', '--path', type=str, required=False)
    parser.add_argument('-o', '--output', type=str, required=False)
    parser.add_argument('-d', '--dburl', type=str, default='', required=False)
    parser.add_argument('-f', '--format', type=str, required=False)
    parser.add_argument('--notice', action='store_true', required=False)

    try:
        args = parser.parse_args()
    except Exception as ex:
        print(ex)
        sys.exit(1)

    if args.help:  # -h option
        print_help_msg()

    if args.version:    # -v option
        print_package_version(_PKG_NAME, "FOSSLight Binary Scanner Version:")
        sys.exit(0)

    if args.path:   # -p option
        path_to_find_bin = args.path
    else:
        path_to_find_bin = os.getcwd()

    if args.output:  # -o option
        output_dir = args.output

    if args.dburl:  # -d option
        db_url = args.dburl

    if args.format:  # -f option
        format = args.format

    if args.notice:  # --notice option
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(__file__)

        data_path = os.path.join(base_path, 'LICENSES')
        print(f"*** {_PKG_NAME} open source license notice ***")
        for ff in os.listdir(data_path):
            f = open(os.path.join(data_path, ff), 'r', encoding='utf8')
            print(f.read())
        sys.exit(0)

    timer = TimerThread()
    timer.setDaemon(True)
    timer.start()

    find_binaries(path_to_find_bin, output_dir, format, db_url)


if __name__ == '__main__':
    main()
