#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FOSSLight Binary analysis script
# Copyright (c) 2024 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import re
import logging
import zipfile
import tarfile
import yaml
import fosslight_util.constant as constant
from fosslight_util.set_log import init_log
from fosslight_util.time import timestamp_for_filename

REMOVE_FILE_EXTENSION_SIMPLE = ['ttf', 'otf', 'png', 'gif', 'jpg', 'bmp', 'jpeg']
logger = logging.getLogger(constant.LOGGER_NAME)


def is_compressed_file(filename):
    return zipfile.is_zipfile(filename) or tarfile.is_tarfile(filename)


def is_jar_file(filename):
    return filename.lower().endswith('.jar')


def exclude_bin_for_simple_mode(binary_list):
    bin_list_exclude_compressed = []
    compressed_list = []

    for bin in binary_list:
        if bin.exclude:
            continue

        path = bin.bin_name_with_path

        if is_jar_file(path) and not re.search(r".*sources\.jar", path.lower()):
            bin_list_exclude_compressed.append(path)
        elif re.search(r".*sources\.jar", path.lower()) or is_compressed_file(path):
            compressed_list.append(path)
        else:
            bin_list_exclude_compressed.append(path)
    return compressed_list, bin_list_exclude_compressed


def check_output_path(output, start_time):
    output_path = ""
    binary_yaml_file = ""
    compressed_yaml_file = ""
    file_time = timestamp_for_filename(start_time)

    if output != "":
        if not os.path.isdir(output) and output.endswith('.yaml'):
            output_path = os.path.dirname(output)
            basename = os.path.basename(output)
            basename_stem, _ = os.path.splitext(basename)
            binary_yaml_file = basename
            compressed_yaml_file = f"{basename_stem}_compressed.yaml"
        else:
            output_path = output
            binary_yaml_file = f"binary_list_{file_time}.yaml"
            compressed_yaml_file = f"compressed_list_{file_time}.yaml"
    else:
        binary_yaml_file = f"binary_list_{file_time}.yaml"
        compressed_yaml_file = f"compressed_list_{file_time}.yaml"

    if output_path == "":
        output_path = os.getcwd()
    else:
        output_path = os.path.abspath(output_path)

    binary_yaml_file = os.path.join(output_path, binary_yaml_file)
    compressed_yaml_file = os.path.join(output_path, compressed_yaml_file)

    return output_path, binary_yaml_file, compressed_yaml_file


def init_simple(output_file_name, pkg_name, start_time):
    global logger, _result_log

    output_path, binary_yaml_file, compressed_yaml_file = check_output_path(output_file_name, start_time)

    log_file = os.path.join(output_path, f"fosslight_log_bin_{timestamp_for_filename(start_time)}.txt")
    logger, _result_log = init_log(log_file, False, logging.INFO, logging.DEBUG, pkg_name)

    return _result_log, binary_yaml_file, compressed_yaml_file


def print_simple_mode(binary_yaml_file, compressed_yaml_file, compressed_list, bin_list):
    results = []

    if not bin_list and not compressed_list:
        results.append(tuple([True, "", ""]))
        return results

    def _write_yaml(filepath, data):
        msg = ""
        output_file = ""
        try:
            output_dir = os.path.dirname(filepath)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            output_file = filepath
        except Exception as e:
            msg = f"Error to write yaml file for simple mode : {e}"
        return tuple([output_file != "", msg, output_file])

    if bin_list:
        data = {
            'binary_files_excluding_archives': {
                'count': len(bin_list),
                'files': bin_list
            }
        }
        results.append(_write_yaml(binary_yaml_file, data))

    if compressed_list:
        data = {
            'compressed_files': {
                'count': len(compressed_list),
                'files': compressed_list
            }
        }
        results.append(_write_yaml(compressed_yaml_file, data))

    return results


def filter_binary(bin_list):
    compressed_list, bin_list_exclude_compressed = exclude_bin_for_simple_mode(bin_list)
    return compressed_list, bin_list_exclude_compressed
