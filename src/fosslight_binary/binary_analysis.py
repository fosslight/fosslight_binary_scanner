#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FOSSLight Binary analysis script
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import sys
import platform
from datetime import datetime
from binaryornot.check import is_binary
import magic
import logging
import yaml
import stat
from fosslight_util.set_log import init_log
import fosslight_util.constant as constant
from fosslight_util.output_format import check_output_formats_v2, write_output_file
from ._binary_dao import get_oss_info_from_db
from ._binary import BinaryItem, TLSH_CHECKSUM_NULL
from ._jar_analysis import analyze_jar_file, merge_binary_list
from ._simple_mode import print_simple_mode, filter_binary, init_simple
from fosslight_util.correct import correct_with_yaml
from fosslight_util.oss_item import ScannerItem
import hashlib
import tlsh
from io import open

PKG_NAME = "fosslight_binary"
logger = logging.getLogger(constant.LOGGER_NAME)

_REMOVE_FILE_EXTENSION = ['qm', 'xlsx', 'pdf', 'pptx', 'jfif', 'docx', 'doc', 'whl',
                          'xls', 'xlsm', 'ppt', 'mp4', 'pyc', 'plist', 'dat', 'json', 'js']
_REMOVE_FILE_COMMAND_RESULT = [
    'data', 'timezone data', 'apple binary property list']
INCLUDE_FILE_COMMAND_RESULT = ['current ar archive']
_EXCLUDE_FILE_EXTENSION = ['class']
_EXCLUDE_FILE = ['fosslight_bin', 'fosslight_bin.exe']
_EXCLUDE_DIR = ["test", "tests", "doc", "docs", "intermediates"]
_EXCLUDE_DIR = [os.path.sep + dir_name + os.path.sep for dir_name in _EXCLUDE_DIR]
_EXCLUDE_DIR.append("/.")
_REMOVE_DIR = ['.git']
_REMOVE_DIR = [os.path.sep + dir_name + os.path.sep for dir_name in _REMOVE_DIR]
_error_logs = []
_root_path = ""
start_time = ""
windows = False
BYTES = 2048
BIN_EXT_HEADER = {'BIN_FL_Binary': ['ID', 'Binary Path', 'OSS Name',
                                    'OSS Version', 'License', 'Download Location',
                                    'Homepage', 'Copyright Text', 'Exclude',
                                    'Comment', 'Vulnerability Link', 'TLSH', 'SHA1']}
HIDE_HEADER = {'TLSH', "SHA1"}


def get_checksum_and_tlsh(bin_with_path):
    checksum_value = TLSH_CHECKSUM_NULL
    tlsh_value = TLSH_CHECKSUM_NULL
    error_msg = ""
    try:
        f = open(bin_with_path, "rb")
        byte = f.read()
        sha1_hash = hashlib.sha1(byte)
        checksum_value = str(sha1_hash.hexdigest())
        try:
            tlsh_value = str(tlsh.hash(byte))
            if tlsh_value == "TNULL" or (not tlsh_value):
                tlsh_value = TLSH_CHECKSUM_NULL
        except:
            tlsh_value = TLSH_CHECKSUM_NULL
        f.close()
    except Exception as ex:
        error_msg = f"(Error) Get_checksum, tlsh: {ex}"

    return checksum_value, tlsh_value, error_msg


def init(path_to_find_bin, output_file_name, formats, path_to_exclude=[]):
    global logger, _result_log

    _json_ext = ".json"
    success, msg, output_path, output_files, output_extensions, formats = check_output_formats_v2(output_file_name, formats)

    if success:
        if output_path == "":
            output_path = os.getcwd()
        else:
            output_path = os.path.abspath(output_path)

        while len(output_files) < len(output_extensions):
            output_files.append(None)
        to_remove = []  # elements of spdx format on windows that should be removed
        for i, output_extension in enumerate(output_extensions):
            if output_files[i] is None or output_files[i] == "":
                if formats:
                    if formats[i].startswith('spdx') or formats[i].startswith('cyclonedx'):
                        if platform.system() == 'Windows':
                            logger.warning(f'{formats[i]} is not supported on Windows. Please remove {formats[i]} from format.')
                            to_remove.append(i)
                        else:
                            if formats[i].startswith('spdx'):
                                output_files[i] = f"fosslight_spdx_bin_{start_time}"
                            elif formats[i].startswith('cyclonedx'):
                                output_files[i] = f'fosslight_cyclonedx_bin_{start_time}'
                    else:
                        if output_extension == _json_ext:
                            output_files[i] = f"fosslight_opossum_bin_{start_time}"
                        else:
                            output_files[i] = f"fosslight_report_bin_{start_time}"
                else:
                    if output_extension == _json_ext:
                        output_files[i] = f"fosslight_opossum_bin_{start_time}"
                    else:
                        output_files[i] = f"fosslight_report_bin_{start_time}"
        for index in sorted(to_remove, reverse=True):
            # remove elements of spdx format on windows
            del output_files[index]
            del output_extensions[index]
            del formats[index]
        if len(output_extensions) < 1:
            sys.exit(0)

        combined_paths_and_files = [os.path.join(output_path, file) for file in output_files]
    else:
        logger.error(f"Format error - {msg}")
        sys.exit(1)

    log_file = os.path.join(output_path, f"fosslight_log_bin_{start_time}.txt")
    logger, _result_log = init_log(log_file, True, logging.INFO, logging.DEBUG,
                                   PKG_NAME, path_to_find_bin, path_to_exclude)

    if not success:
        error_occured(error_msg=msg,
                      result_log=_result_log,
                      exit=True)
    return _result_log, combined_paths_and_files, output_extensions


def get_file_list(path_to_find, abs_path_to_exclude):
    bin_list = []
    file_cnt = 0
    found_jar = False

    for root, dirs, files in os.walk(path_to_find):
        if os.path.abspath(root) in abs_path_to_exclude:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            file_abs_path = os.path.abspath(file_path)
            if any(os.path.commonpath([file_abs_path, exclude_path]) == exclude_path
                    for exclude_path in abs_path_to_exclude):
                continue
            file_lower_case = file.lower()
            extension = os.path.splitext(file_lower_case)[1][1:].strip()

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
            bin_item.source_name_or_path = bin_with_path.replace(
                _root_path, '', 1)

            if any(dir_name in dir_path for dir_name in _EXCLUDE_DIR):
                bin_item.exclude = True
            elif file.lower() in _EXCLUDE_FILE:
                bin_item.exclude = True
            elif extension in _EXCLUDE_FILE_EXTENSION:
                bin_item.exclude = True
            elif file.startswith('.'):
                bin_item.exclude = True
            bin_list.append(bin_item)
            file_cnt += 1
    return file_cnt, bin_list, found_jar


def find_binaries(path_to_find_bin, output_dir, formats, dburl="", simple_mode=False,
                  correct_mode=True, correct_filepath="", path_to_exclude=[]):
    global start_time, _root_path, _result_log

    mode = "Normal Mode"
    start_time = datetime.now().strftime('%y%m%d_%H%M')

    _root_path = path_to_find_bin
    if not path_to_find_bin.endswith(os.path.sep):
        _root_path += os.path.sep

    if simple_mode:
        mode = "Simple Mode"
        _result_log, compressed_list_txt, simple_bin_list_txt = init_simple(output_dir, PKG_NAME, start_time)
    else:
        _result_log, result_reports, output_extensions = init(
            path_to_find_bin, output_dir, formats, path_to_exclude)

    total_bin_cnt = 0
    total_file_cnt = 0
    db_loaded_cnt = 0
    success_to_write = False
    writing_msg = ""
    results = []
    bin_list = []
    scan_item = ScannerItem(PKG_NAME, "")
    abs_path_to_exclude = [os.path.abspath(path) for path in path_to_exclude if path.strip() != ""]

    if not os.path.isdir(path_to_find_bin):
        error_occured(error_msg=f"(-p option) Can't find the directory: {path_to_find_bin}",
                      result_log=_result_log,
                      exit=True,
                      mode=mode)
    if not correct_filepath:
        correct_filepath = path_to_find_bin
    try:
        total_file_cnt, file_list, found_jar = get_file_list(path_to_find_bin, abs_path_to_exclude)
        return_list = list(return_bin_only(file_list))
    except Exception as ex:
        error_occured(error_msg=f"Failed to check whether it is binary or not : {ex}",
                      result_log=_result_log,
                      exit=True,
                      mode=mode)
    if simple_mode:
        try:
            compressed_list, filtered_bin_list = filter_binary(return_list)
            results = print_simple_mode(compressed_list_txt, simple_bin_list_txt, compressed_list, filtered_bin_list)
            total_bin_cnt = len(filtered_bin_list)
        except Exception as ex:
            error_occured(error_msg=f"Failed to run simple mode: {ex}",
                          result_log=_result_log,
                          exit=True,
                          mode="Simple mode")
    else:
        total_bin_cnt = len(return_list)
        scan_item = ScannerItem(PKG_NAME, start_time)
        scan_item.set_cover_pathinfo(path_to_find_bin, path_to_exclude)
        try:
            # Run OWASP Dependency-check
            if found_jar:
                logger.info("Run OWASP Dependency-check to analyze .jar file")
                owasp_items, vulnerability_items, success = analyze_jar_file(path_to_find_bin, abs_path_to_exclude)
                if success:
                    return_list = merge_binary_list(owasp_items, vulnerability_items, return_list)
                else:
                    logger.warning("Could not find OSS information for some jar files.")

            return_list, db_loaded_cnt = get_oss_info_from_db(return_list, dburl)
            return_list = sorted(return_list, key=lambda row: (row.bin_name_with_path))
            scan_item.append_file_items(return_list, PKG_NAME)
            if correct_mode:
                success, msg_correct, correct_list = correct_with_yaml(correct_filepath, path_to_find_bin, scan_item)
                if not success:
                    logger.info(f"No correction with yaml: {msg_correct}")
                else:
                    return_list = correct_list
                    logger.info("Success to correct with yaml.")

            scan_item.set_cover_comment(f"Total number of binaries: {total_bin_cnt}")
            if total_bin_cnt == 0:
                scan_item.set_cover_comment("(No binary detected.) ")
            scan_item.set_cover_comment(f"Total number of files: {total_file_cnt}")

            for combined_path_and_file, output_extension, output_format in zip(result_reports, output_extensions, formats):
                results.append(write_output_file(combined_path_and_file, output_extension, scan_item,
                                                 BIN_EXT_HEADER, HIDE_HEADER, output_format))

        except Exception as ex:
            error_occured(error_msg=str(ex), exit=False)

        for success_to_write, writing_msg, result_file in results:
            if success_to_write:
                if result_file:
                    logger.info(f"Output file :{result_file}")
                else:
                    logger.warning(f"{writing_msg}")
                for row in scan_item.get_cover_comment():
                    logger.info(row)
            else:
                logger.error(f"Fail to generate result file.:{writing_msg}")

    try:
        print_result_log(mode=mode, success=True, result_log=_result_log,
                         file_cnt=str(total_file_cnt),
                         bin_file_cnt=str(total_bin_cnt),
                         auto_bin_cnt=str(db_loaded_cnt), bin_list=bin_list)
    except Exception as ex:
        error_occured(error_msg=f"Print log : {ex}", exit=False)

    return success_to_write, scan_item


def return_bin_only(file_list, need_checksum_tlsh=True):
    for file_item in file_list:
        try:
            if check_binary(file_item.bin_name_with_path):
                if need_checksum_tlsh:
                    file_item.checksum, file_item.tlsh, error_msg = get_checksum_and_tlsh(file_item.bin_name_with_path)
                    if error_msg:
                        error_occured(modeerror_msg=error_msg, exit=False)
                yield file_item
        except Exception as ex:
            logger.debug(f"Exception in get_file_list: {ex}")
            file_item.comment = "Exclude or delete if it is not binary."
            yield file_item


def check_binary(file_with_path):
    is_bin_confirmed = False
    file = os.path.basename(file_with_path)
    extension = os.path.splitext(file)[1][1:]
    if not os.path.islink(file_with_path) and extension.lower() not in _REMOVE_FILE_EXTENSION:
        if stat.S_ISFIFO(os.stat(file_with_path).st_mode):
            return False
        file_command_result = ""
        file_command_failed = False
        try:
            file_command_result = magic.from_file(file_with_path)
        except Exception:
            file_command_failed = True
        if file_command_failed:
            try:
                file_command_result = magic.from_buffer(open(file_with_path).read(BYTES))
            except Exception as ex:
                logger.debug(f"Failed to check file type:{file_with_path}, {ex}")

        if file_command_result:
            file_command_result = file_command_result.lower()
            if any(file_command_result.startswith(x) for x in _REMOVE_FILE_COMMAND_RESULT):
                return False
            if any(file_command_result.startswith(x) for x in INCLUDE_FILE_COMMAND_RESULT):
                is_bin_confirmed = True
        if is_binary(file_with_path):
            is_bin_confirmed = True
    return is_bin_confirmed


def error_occured(error_msg, exit=False, result_log={}, mode="Normal mode"):
    global _error_logs
    _error_logs.append(error_msg)
    if exit:
        print_result_log(mode, success=False, result_log=result_log)
        sys.exit()


def print_result_log(mode="Normal Mode", success=True, result_log={}, file_cnt="", bin_file_cnt="", auto_bin_cnt="", bin_list=[]):

    if "Running time" in result_log:
        starttime = result_log["Running time"]
    else:
        starttime = start_time
    result_log["Mode"] = mode
    result_log["Running time"] = starttime + " ~ " + \
        datetime.now().strftime('%Y%m%d_%H%M%S')
    result_log["Execution result"] = 'Success' if success else 'Error occurred'
    result_log["Binaries / Scanned files"] = f"{bin_file_cnt}/{file_cnt}"
    result_log["Identified in Binary DB / Binaries"] = f"{auto_bin_cnt}/{bin_file_cnt}"
    if len(_error_logs) > 0:
        result_log["Error Log"] = _error_logs
        if success:
            result_log["Execution result"] += " but it has minor errors"
    if bin_list:
        result_log["Binary list"] = bin_list
    try:
        _str_final_result_log = yaml.safe_dump(result_log, allow_unicode=True, sort_keys=True)
        logger.info(_str_final_result_log)
    except Exception as ex:
        logger.warning(f"Error to print final log: {ex}")
