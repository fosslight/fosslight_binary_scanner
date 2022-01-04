#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FOSSLight Binary analysis script
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import getopt
import os
import sys
from datetime import datetime
from binaryornot.check import is_binary
import magic
import logging
import platform
import yaml
import stat
from fosslight_util.help import print_package_version
from fosslight_util.set_log import init_log
import fosslight_util.constant as constant
from fosslight_util.write_txt import write_txt_file
from fosslight_util.output_format import check_output_format, write_output_file
from ._binary_dao import get_oss_info_from_db
from ._binary import BinaryItem
from ._help import print_help_msg
from ._jar_analysis import ananlyze_jar_file, merge_binary_list

_PKG_NAME = "fosslight_binary"
logger = logging.getLogger(constant.LOGGER_NAME)

_REMOVE_FILE_EXTENSION = ['png', 'gif', 'jpg', 'bmp', 'jpeg', 'qm', 'xlsx', 'pdf', 'ico', 'pptx', 'jfif', 'docx',
                          'doc', 'whl', 'xls', 'xlsm', 'ppt', 'mp4', 'pyc', 'plist']
_REMOVE_FILE_COMMAND_RESULT = [
    'data', 'timezone data', 'apple binary property list']
_EXCLUDE_FILE = ['fosslight_bin', 'fosslight_bin.exe']
_EXCLUDE_DIR = ["test", "tests", "doc", "docs"]
_EXCLUDE_DIR = [os.path.sep + dir_name + os.path.sep for dir_name in _EXCLUDE_DIR]
_EXCLUDE_DIR.append("/.")
_REMOVE_DIR = ['.git']
_REMOVE_DIR = [os.path.sep + dir_name + os.path.sep for dir_name in _REMOVE_DIR]
_error_logs = []
_root_path = ""


def init(path_to_find_bin, output_file_name, format):
    global _root_path, logger

    _json_ext = ".json"
    _start_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    _result_log = {
        "Tool Info": _PKG_NAME
    }

    _root_path = path_to_find_bin
    if not path_to_find_bin.endswith(os.path.sep):
        _root_path += os.path.sep

    success, msg, output_path, output_file, output_extension = check_output_format(output_file_name, format)
    if success:
        if output_path == "":
            output_path = os.getcwd()
        else:
            output_path = os.path.abspath(output_path)

        if output_file != "":
            result_report = output_file
            bin_txt_file = output_file + ".txt"
        else:
            if output_extension == _json_ext:
                result_report = "Opossum_input_" + _start_time
            else:
                result_report = "FOSSLight-Report_" + _start_time
            bin_txt_file = "binary_" + _start_time + ".txt"

        result_report = os.path.join(output_path, result_report)
        binary_txt_file = os.path.join(output_path, bin_txt_file)
    else:
        output_path = os.getcwd()

    log_file = os.path.join(output_path, "fosslight_bin_log_" + _start_time + ".txt")
    logger, _result_log = init_log(log_file, True, logging.INFO, logging.DEBUG, _PKG_NAME, path_to_find_bin)

    if not success:
        error_occured(error_msg=msg,
                      result_log=_result_log,
                      exit=True)
    return _result_log, result_report, binary_txt_file, output_extension


def get_file_list(path_to_find):
    bin_list = []
    file_cnt = 0
    found_jar = False

    for root, dirs, files in os.walk(path_to_find):
        for file in files:
            file_lower_case = file.lower()
            extension = file_lower_case.split(".")[-1]

            if extension == 'jar':
                found_jar = True

            directory = root + os.path.sep
            dir_path = directory.replace(_root_path, '', 1).lower()
            dir_path = os.path.sep + dir_path + os.path.sep
            if any(dir_name in dir_path for dir_name in _REMOVE_DIR):
                continue

            bin_with_path = os.path.join(root, file)
            bin_item = BinaryItem(bin_with_path)
            bin_item.binary_name_without_path = file
            bin_item.binary_strip_root = bin_with_path.replace(
                _root_path, '', 1)

            if any(dir_name in dir_path for dir_name in _EXCLUDE_DIR):
                bin_item.set_exclude(True)
            elif file.lower() in _EXCLUDE_FILE:
                bin_item.set_exclude(True)
            bin_list.append(bin_item)
            file_cnt += 1

    return file_cnt, bin_list, found_jar


def find_binaries(path_to_find_bin, output_dir, format, dburl=""):

    _result_log, result_report, binary_txt_file, output_extension = init(
        path_to_find_bin, output_dir, format)

    total_bin_cnt = 0
    total_file_cnt = 0
    db_loaded_cnt = 0

    try:
        if not os.path.isdir(path_to_find_bin):
            error_occured(error_msg="Can't find the directory :" + path_to_find_bin,
                          result_log=_result_log,
                          exit=True)

        total_file_cnt, file_list, found_jar = get_file_list(path_to_find_bin)
        total_bin_cnt, return_list = return_bin_only(file_list)

        # Run OWASP Dependency-check
        if found_jar:
            logger.info("Run OWASP Dependency-check to analyze .jar file")
            owasp_items = ananlyze_jar_file(path_to_find_bin)
            if owasp_items:
                return_list = merge_binary_list(owasp_items, return_list)

        return_list, db_loaded_cnt = get_oss_info_from_db(return_list, dburl)
        return_list = sorted(return_list, key=lambda row: (row.bin_name))

        _str_files = [x.get_print_binary_only() for x in return_list]
        success, error = write_txt_file(binary_txt_file,
                                        "Binary\tsha1sum\ttlsh\n" + '\n'.join(_str_files))

        if success:
            _result_log["FOSSLight binary.txt"] = binary_txt_file
        else:
            error_occured(error_msg=error, exit=False)

        sheet_list = {}
        content_list = []
        for scan_item in return_list:
            content_list.extend(scan_item.get_oss_report())
        sheet_list["BIN_FL_Binary"] = content_list

        success_to_write, writing_msg = write_output_file(result_report, output_extension,
                                                          sheet_list)
        logger.info("Writing Output file(" + os.path.basename(result_report) + output_extension
                    + "):" + str(success_to_write) + " " + writing_msg)
        if success_to_write:
            _result_log["Output file"] = result_report + output_extension

    except Exception as ex:
        error_occured(error_msg=str(ex), exit=False)

    print_result_log(success=True, result_log=_result_log,
                     file_cnt=str(total_file_cnt), bin_file_cnt=str(total_bin_cnt),
                     auto_bin_cnt=str(db_loaded_cnt))


def return_bin_only(file_list):
    bin_cnt = 0
    bin_list = []
    for file_item in file_list:
        file_with_path = file_item.bin_name
        file = file_item.binary_name_without_path
        extension = os.path.splitext(file)[1][1:]

        if not os.path.islink(file_with_path) and extension.lower() not in _REMOVE_FILE_EXTENSION:
            if stat.S_ISFIFO(os.stat(file_with_path).st_mode):
                continue
            if is_binary(file_with_path):
                file_command_result = magic.from_file(file_with_path)
                if file_command_result != "":
                    file_command_result = file_command_result.lower()
                    removed_keyword = [x for x in _REMOVE_FILE_COMMAND_RESULT if
                                       file_command_result.startswith(x)]
                    if len(removed_keyword) > 0:
                        continue

                error, error_msg = file_item.set_checksum_tlsh()
                if error:
                    error_occured(error_msg=error_msg, exit=False)

                bin_list.append(file_item)
                bin_cnt += 1

    return bin_cnt, bin_list


def error_occured(error_msg, exit=False, result_log={}):
    global _error_logs
    _error_logs.append(error_msg)
    if exit:
        print_result_log(success=False, result_log=result_log)
        sys.exit()


def print_result_log(success=True, result_log={}, file_cnt="", bin_file_cnt="", auto_bin_cnt=""):

    if "Running time" in result_log:
        start_time = result_log["Running time"]
    else:
        start_time = ""
    result_log["Running time"] = start_time + " ~ " + \
        datetime.now().strftime('%Y%m%d_%H%M%S')
    result_log["Execution result"] = 'Success' if success else 'Error occurred'
    result_log["Binaries / Scanned files"] = bin_file_cnt + " / " + file_cnt
    result_log["Identified in Binary DB / Binaries"] = auto_bin_cnt + \
        " / " + bin_file_cnt
    if len(_error_logs) > 0:
        result_log["Error Log"] = _error_logs
        if success:
            result_log["Execution result"] += " but it has minor errors"
    try:
        _str_final_result_log = yaml.safe_dump(result_log, allow_unicode=True, sort_keys=True)
        logger.info(_str_final_result_log)
    except Exception as ex:
        logger.warning("Error to print final log:" + str(ex))


def main():
    argv = sys.argv[1:]
    output_dir = ""
    path_to_find_bin = ""
    format = ""
    db_url = ""

    opts, args = getopt.getopt(argv, 'hvp:a:o:f:d:')
    for opt, arg in opts:
        if opt == "-h":
            print_help_msg()
        elif opt == "-v":
            print_package_version(_PKG_NAME, "FOSSLight Binary Scanner Version:")
        elif opt == "-p":
            path_to_find_bin = arg
        elif opt == "-o":
            output_dir = arg
        elif opt == "-f":
            format = arg
        elif opt == "-d":
            db_url = arg

    _windows = platform.system() == "Windows"
    if path_to_find_bin == "":
        if _windows:
            path_to_find_bin = os.getcwd()
        else:
            print_help_msg()

    find_binaries(path_to_find_bin, output_dir, format, db_url)


if __name__ == '__main__':
    main()
