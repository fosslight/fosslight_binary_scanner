#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess


def run_command(*args):  # 리눅스 명령어 실행
    result = subprocess.run(args, capture_output=True, text=True)
    success = result.returncode == 0
    output = result.stdout if success else result.stderr
    return success, output


def test_output_file_format():  # 테스트 환경 tox.ini
    # Given
    run_command("rm", "-rf", "test_result")
    os.makedirs("test_result", exist_ok=True)

    # When
    excel_success, _ = run_command("fosslight_bin", "-p", ".", "-o", "test_result", "-f", "excel")
    csv_success, _ = run_command("fosslight_bin", "-p", ".", "-o", "test_result", "-f", "csv")
    opossum_success, _ = run_command("fosslight_bin", "-p", ".", "-o", "test_result", "-f", "opossum")
    yaml_success, _ = run_command("fosslight_bin", "-p", ".", "-o", "test_result", "-f", "yaml")
    files_in_result = os.listdir("test_result")

    # Then
    excel_files = [f for f in files_in_result if f.endswith('.xlsx')]  # Assuming Excel files end with .xlsx
    csv_files = [f for f in files_in_result if f.endswith('.csv')]
    opossum_files = [f for f in files_in_result if f.endswith('.json')]  # Assuming opossum files are in JSON format
    yaml_files = [f for f in files_in_result if f.endswith('.yaml') or f.endswith('.yml')]

    assert excel_success is True, "Test Output File : Excel files not properly created (not create)"
    assert len(excel_files) > 0, "Test Output File : Excel files not properly created (length)"

    assert csv_success is True, "Test Output File : CSV files not properly created (not create)"
    assert len(csv_files) > 0, "Test Output File : CSV files not properly created (length)"

    assert opossum_success is True, "Test Output File : JSON files not properly created (not create)"
    assert len(opossum_files) > 0, "Test Output File : JSON files not properly created (length)"

    assert yaml_success is True, "Test Output File : Yaml files not properly created (not create)"
    assert len(yaml_files) > 0, "Test Output File : Yaml files not properly created (length)"
