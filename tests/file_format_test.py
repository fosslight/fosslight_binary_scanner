#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess
import shutil
import pytest
import tempfile


@pytest.fixture(scope="function", autouse=True)
def setup_test_result_dir_and_teardown():
    # 각 테스트마다 임시 디렉토리 생성
    test_result_dir = tempfile.mkdtemp(dir=".")  # 고유한 임시 디렉토리 생성
    print("==============setup: {test_result_dir}==============")

    yield test_result_dir  # 임시 디렉토리 경로를 테스트 함수로 넘김

    print("==============tearDown==============")
    shutil.rmtree(test_result_dir)


def run_command(*args):  # 리눅스 명령어 실행
    result = subprocess.run(args, capture_output=True, text=True)
    success = result.returncode == 0
    output = result.stdout if success else result.stderr
    return success, output


@pytest.mark.parametrize("file_format, extension", [
    ("excel", ".xlsx"),
    ("csv", ".csv"),
    ("opossum", ".json"),
    ("yaml", [".yaml", ".yml"])
])
def test_output_file_format(file_format, extension, setup_test_result_dir_and_teardown):  # 테스트 환경 tox.ini
    # Given
    test_result_dir = setup_test_result_dir_and_teardown

    # When
    success, _ = run_command("fosslight_bin", "-p", ".", "-o", test_result_dir, "-f", file_format)
    files_in_result = os.listdir(test_result_dir)

    # Then
    if isinstance(extension, list):
        # 생성된 파일 명칭을 리스트로 갖고오는 로직
        matching_files = [f for f in files_in_result if any(f.endswith(ext) for ext in extension)]
    else:
        matching_files = [f for f in files_in_result if f.endswith(extension)]

    assert success is True, f"Test Output File : {file_format} files not properly created (not create)"
    assert len(matching_files) > 0, f"Test Output File : {file_format} files not properly created (length)"
