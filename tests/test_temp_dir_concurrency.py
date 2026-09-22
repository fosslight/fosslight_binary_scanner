#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

import os

import fosslight_binary.binary_analysis as ba


def test_same_timestamp_uses_unique_temp_directory(tmp_path):
    output_dir = tmp_path / 'out'

    first = ba._prepare_temp_dir(str(output_dir), "20260917_120000")
    second = ba._prepare_temp_dir(str(output_dir), "20260917_120000")

    assert os.path.basename(first).startswith('.fosslight_temp_20260917_120000')
    assert os.path.basename(second).startswith('.fosslight_temp_20260917_120000')
    assert first != second
    assert os.path.isdir(first)
    assert os.path.isdir(second)


def test_same_timestamp_replaces_stale_temp_directory(tmp_path):
    output_dir = tmp_path / 'out'
    first = ba._prepare_temp_dir(str(output_dir), '20260917_120000')
    stale_file = os.path.join(first, 'stale.txt')
    with open(stale_file, 'w', encoding='utf-8') as file:
        file.write('stale')

    second = ba._prepare_temp_dir(str(output_dir), '20260917_120000')

    assert second != first
    assert os.path.exists(stale_file)
    assert os.path.isdir(second)


def test_cleanup_temp_dir_only_removes_requested_path(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()

    ba._cleanup_temp_dir(str(first))

    assert not first.exists()
    assert second.exists()


def test_find_binaries_passes_invocation_path_to_cleanup(tmp_path, monkeypatch):
    temp_path = tmp_path / "invocation-temp"
    observed = {}

    def fake_analyze(*args, temp_path_holder=None, **kwargs):
        temp_path.mkdir()
        temp_path_holder["path"] = str(temp_path)

    def capture_cleanup(path):
        observed["path"] = path

    monkeypatch.setattr(ba, "_analyze_binaries", fake_analyze)
    monkeypatch.setattr(ba, "_cleanup_temp_dir", capture_cleanup)
    ba.find_binaries("scan", "out", ["excel"])

    assert observed["path"] == str(temp_path)
