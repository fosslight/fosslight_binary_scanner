#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FOSSLight Binary analysis script
# Copyright (c) 2024 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import re
import logging
from datetime import datetime
import fosslight_util.constant as constant
from fosslight_util.write_txt import write_txt_file
from fosslight_util.download import compression_extension
import fosslight_binary.binary_analysis as fl_bin
from fosslight_util.set_log import init_log

_REMOVE_FILE_EXTENSION_SIMPLE = ['ttf', 'otf', 'png', 'gif', 'jpg', 'bmp', 'jpeg']
logger = logging.getLogger(constant.LOGGER_NAME)


def exclude_bin_for_simple_mode(binary_list):
    bin_list = []
    compressed_list = []
    compressed_ext_wo_dot = [ext.lstrip('.') for ext in compression_extension]

    for bin in binary_list:
        file_lower_case = bin.bin_name_with_path.lower()
        extension = os.path.splitext(file_lower_case)[1][1:].strip()

        for compress_ext in compressed_ext_wo_dot:
            if extension == compress_ext:
                compressed_list.append(bin.bin_name_with_path)

        remove_file_ext_list = _REMOVE_FILE_EXTENSION_SIMPLE + compressed_ext_wo_dot
        if any(extension == remove_ext for remove_ext in remove_file_ext_list):
            continue
        if not (re.search(r".*source\.jar", bin.bin_name_with_path.lower()) or bin.exclude):
            continue

        bin_list.append(bin.bin_name_with_path)
            
    return compressed_list, bin_list


def convert_list_to_str(input_list):
    output_text = '\n'.join(map(str, input_list))
    return output_text


def check_output_path(output='', start_time):
    compressed_list_txt = ""
    simple_bin_list_txt = ""
    output_path = ""

    if output != "":
        if not os.path.isdir(output) and output.endswith('.txt'):
            output_path = os.path.dirname(output)
            basename = os.path.basename(output)
            basename_file, _ = os.path.splitext(basename)
            compressed_list_txt = f"{basename_file}_compressed_list.txt"
            simple_bin_list_txt = f"{basename_file}.txt"
        else:
            output_path = output
            compressed_list_txt = f"compressed_list_{start_time}.txt"
            simple_bin_list_txt = f"binary_list_{start_time}.txt"
    else:
        compressed_list_txt = f"compressed_list_{start_time}.txt"
        simple_bin_list_txt = f"binary_list_{start_time}.txt"

    if output_path == "":
        output_path = os.getcwd()
    else:
        output_path = os.path.abspath(output_path)

    compressed_list_txt = os.path.join(output_path, compressed_list_txt)
    simple_bin_list_txt = os.path.join(output_path, simple_bin_list_txt)

    return output_path, compressed_list_txt, simple_bin_list_txt


def init_simple(output_file_name, pkg_name, start_time):
    global logger

    _result_log = {
        "Tool Info": pkg_name,
        "Mode": "Simple mode"
    }

    output_path, compressed_list_txt, simple_bin_list_txt = check_output_path(output_file_name, start_time) 
    
    log_file = os.path.join(output_path, f"fosslight_log_bin_{start_time}.txt")
    logger, _result_log = init_log(log_file, True, logging.INFO, logging.DEBUG,
                                   pkg_name)

    return _result_log, compressed_list_txt, simple_bin_list_txt


def print_simple_mode(compressed_list_txt, simple_bin_list_txt, compressed_list, bin_list):
    if compressed_list:
        success, error = write_txt_file(compressed_list_txt, convert_list_to_str(compressed_list))
        if not success:
            logger.info(f"Error to write compressed list file for simple mode : {error}")
    if bin_list:
        success, error = write_txt_file(simple_bin_list_txt, convert_list_to_str(bin_list))
        if not success:
            logger.info(f"Error to write binary list file for simple mode : {error}")
    return success


def filter_binary(bin_list):
    compressed_list, bin_list = exclude_bin_for_simple_mode(bin_list)
    return compressed_list, bin_list
