#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess
import shutil
import pytest

TEST_RESULT_DIR = "test_result"  # 테스트 디렉토리 명


@pytest.fixture(scope="function", autouse=True)  # 테스트 디렉토리 생성/삭제 로직
def setup_test_result_dir_and_teardown():
    print("==============setup==============")
    os.makedirs(TEST_RESULT_DIR, exist_ok=True)

    yield

    print("==============tearDown==============")
    shutil.rmtree(TEST_RESULT_DIR)


def run_command(*args):  # 리눅스 명령어 실행
    result = subprocess.run(args, capture_output=True, text=True)
    success = result.returncode == 0
    output = result.stdout if success else result.stderr
    return success, output


def test_test_run_environment():  # 테스트 환경 tox.ini
    # When
    csv_success, _ = run_command("fosslight_bin", "-p", ".", "-o", "test_result", "-f", "csv")
    exclude_success, _ = run_command(
        "fosslight_bin",
        "-p", ".",
        "-e", "test", "commons-logging-1.2.jar",
        "-o", "test_result/exclude_result.csv",
        "-f", "csv"
    )

    files_in_result = run_command("ls", "test_result")[1].split()
    txt_success, txt_output = run_command("find", "test_result", "-type", "f", "-name", "fosslight_log*.txt")

    # Then
    csv_files = [f for f in files_in_result if f.endswith('.csv')]
    txt_files = txt_output.split()
    assert csv_success is True, "Test Run Environment: CSV files not properly created (not create)"
    assert len(csv_files) > 0, "Test Run Environment: CSV files not properly created (length)"
    assert exclude_success is True, "Test Run Environment: Exclude feature fail"
    assert len(txt_files) > 0, "Test Run Environment: txt files not properly created"


def test_release_environment():  # 릴리즈 환경 tox.ini
    # When
    help_success, _ = run_command("fosslight_bin", "-h")
    csv_success, _ = run_command("fosslight_bin", "-p", ".", "-o", "test_result/result.csv", "-f", "csv")
    exclude_csv_success, _ = run_command(
        "fosslight_bin",
        "-p", ".",
        "-e", "test", "commons-logging-1.2.jar",
        "-o", "test_result/exclude_result.csv",
        "-f", "csv"
    )

    json_success, _ = run_command("fosslight_bin", "-p", ".", "-o", "test_result/result.json", "-f", "opossum")
    files_in_result = run_command("ls", "test_result")[1].split()

    # Then
    required_files = ['result.csv', 'exclude_result.csv', 'result.json']
    files_exist = all(f in files_in_result for f in required_files)
    assert help_success is True, "Release Run Environment: help method not properly processing"
    assert csv_success is True, "Release Run Environment: CSV files not properly created"
    assert exclude_csv_success is True, "Release Run Environment: Exclude feature fail"
    assert json_success is True, "Release Run Environment: json files not properly created"
    assert files_exist is True, "Release Run Environment: Required files not properly created"
