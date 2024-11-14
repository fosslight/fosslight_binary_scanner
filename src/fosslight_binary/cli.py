#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import argparse
import sys
import os
import shutil
from fosslight_util.help import print_package_version
from fosslight_binary._help import print_help_msg
from fosslight_binary.binary_analysis import find_binaries
from fosslight_util.timer_thread import TimerThread

_PKG_NAME = "fosslight_binary"


def get_terminal_size():
    size = shutil.get_terminal_size()
    return size.lines


def paginate_file(file_path):
    lines_per_page = get_terminal_size() - 1
    with open(file_path, 'r', encoding='utf8') as file:
        lines = file.readlines()

    for i in range(0, len(lines), lines_per_page):
        os.system('clear' if os.name == 'posix' else 'cls')
        print(''.join(lines[i: i + lines_per_page]))
        if i + lines_per_page < len(lines):
            input("Press Enter to see the next page...")


def main():
    global windows
    path_to_find_bin = ""
    path_to_exclude = []
    output_dir = ""
    format = []
    db_url = ""
    simple_mode = False
    correct_mode = True

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true', required=False)
    parser.add_argument('-v', '--version', action='store_true', required=False)
    parser.add_argument('-s', '--simple', action='store_true', required=False)
    parser.add_argument('-p', '--path', type=str, required=False)
    parser.add_argument('-o', '--output', type=str, required=False)
    parser.add_argument('-d', '--dburl', type=str, default='', required=False)
    parser.add_argument('-f', '--formats', type=str, required=False, nargs="*")
    parser.add_argument('-e', '--exclude', nargs="*", required=False, default=[])
    parser.add_argument('--notice', action='store_true', required=False)
    parser.add_argument('--no_correction', action='store_true', required=False)
    parser.add_argument('--correct_fpath', nargs=1, type=str, required=False)

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

    if args.simple:  # -s option
        simple_mode = True

    if args.path:   # -p option
        path_to_find_bin = args.path
    else:
        path_to_find_bin = os.getcwd()

    if args.exclude:  # -e option
        path_to_exclude = args.exclude

    if args.output:  # -o option
        output_dir = args.output

    if args.dburl:  # -d option
        db_url = args.dburl

    if args.formats:  # -f option
        format = list(args.formats)

    if args.no_correction:
        correct_mode = False

    correct_filepath = path_to_find_bin
    if args.correct_fpath:
        correct_filepath = ''.join(args.correct_fpath)

    if args.notice:  # --notice option
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(__file__)

        data_path = os.path.join(base_path, 'LICENSES')
        print(f"*** {_PKG_NAME} open source license notice ***")
        for ff in os.listdir(data_path):
            source_file = os.path.join(data_path, ff)
            destination_file = os.path.join(base_path, ff)
            paginate_file(source_file)
            shutil.copyfile(source_file, destination_file)
        sys.exit(0)

    timer = TimerThread()
    timer.setDaemon(True)
    timer.start()

    find_binaries(path_to_find_bin, output_dir, format, db_url, simple_mode, correct_mode, correct_filepath, path_to_exclude)


if __name__ == '__main__':
    main()
