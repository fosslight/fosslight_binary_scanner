#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

"""Regression tests for temp directory cleanup and excel exclusion.

Interrupting an analysis used to leave .fosslight_temp behind, and a following
run then showed the excel inside that directory in the Binary result. Design:
docs/superpowers/specs/2026-08-27-binary-temp-dir-cleanup-design.md
"""

import glob
import logging
import os
import zipfile

import pytest

import fosslight_util.constant as constant
from fosslight_util.exclude import get_excluded_paths
from fosslight_util.time import timestamp_for_filename
from fosslight_binary import binary_analysis as ba

TEMP_DIR_PREFIX = '.fosslight_temp_'


@pytest.fixture(autouse=True)
def real_log_init(monkeypatch):
    """Let init_log initialize logging as it does under the real CLI.

    init_log skips both the log directory creation and the FileHandler setup
    when logger.hasHandlers() is True. The pytest logging plugin attaches a
    capture handler for every test phase (directly onto a logger whose
    propagate is False), so left alone neither the temp directory nor the log
    file is created and the cleanup cannot be observed. Clearing the handlers
    right before the call reproduces the real condition; the initialization
    itself is delegated to the real init_log.
    """
    logger = logging.getLogger(constant.LOGGER_NAME)
    original_propagate = logger.propagate
    real_init_log = ba.init_log

    def _clear_handlers():
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    def _init_log_without_pytest_handlers(*args, **kwargs):
        _clear_handlers()
        logger.propagate = False
        return real_init_log(*args, **kwargs)

    monkeypatch.setattr(ba, 'init_log', _init_log_without_pytest_handlers)
    ba._error_logs.clear()
    yield
    _clear_handlers()
    logger.propagate = original_propagate


@pytest.fixture(autouse=True)
def offline_binary_db(monkeypatch):
    """Pass through the Binary DB lookup, the only step that hits the network."""
    monkeypatch.setattr(
        ba, 'get_oss_info_from_db',
        lambda bin_list, kb_url="", kb_token="": (bin_list, 0, ""))


def _write_binary(path):
    """Write a file that binaryornot classifies as a binary."""
    with open(path, 'wb') as f:
        f.write(b'\x7fELF\x02\x01\x01\x00' + b'\x00' * 512)


def _write_xlsx(path):
    """Write a real xlsx-shaped zip, which content sniffing reports as binary."""
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('xl/workbook.xml', '<workbook/>')


def _scan_dir(tmp_path):
    """A scan target directory holding exactly one binary."""
    scan_dir = tmp_path / 'scan'
    scan_dir.mkdir()
    _write_binary(scan_dir / 'mybin')
    return scan_dir


def _out_dir(tmp_path):
    out_dir = tmp_path / 'out'
    out_dir.mkdir(exist_ok=True)
    return out_dir


def _temp_dirs(out_dir):
    return list(out_dir.glob(f'{TEMP_DIR_PREFIX}*'))


def _reported_paths(scan_item):
    return {item.source_name_or_path
            for items in scan_item.file_items.values()
            for item in items}


def test_excel_is_not_reported_as_binary(tmp_path):
    """An excel file never shows up as a row in the Binary result.

    Reproduces the fosslight_scanner path: the exclude list is computed up
    front and the excel appears afterwards. get_file_list only checks
    membership in that pre-computed excluded_files, so a file created later
    slips past the extension policy and lands in the result.
    """
    scan_dir = _scan_dir(tmp_path)
    all_exclude_mode = get_excluded_paths(str(scan_dir), [])
    _write_xlsx(scan_dir / 'fosslight_report_src_20260827.xlsx')

    _, scan_item = ba.find_binaries(str(scan_dir), str(_out_dir(tmp_path)), ['excel'],
                                    all_exclude_mode=all_exclude_mode)

    assert _reported_paths(scan_item) == {'mybin'}


def test_temp_dir_name_includes_timestamp(tmp_path, monkeypatch):
    """The temp directory name includes the run timestamp."""
    scan_dir = _scan_dir(tmp_path)
    out_dir = _out_dir(tmp_path)
    fixed_start_time = '20260827_000000'
    created_paths = []

    real_prepare_temp_dir = ba._prepare_temp_dir

    def _capture_temp_path(output_dir, file_time):
        temp_path = real_prepare_temp_dir(output_dir, file_time)
        created_paths.append(temp_path)
        return temp_path

    monkeypatch.setattr(ba, 'current_timestamp_utc', lambda: fixed_start_time)
    monkeypatch.setattr(ba, '_prepare_temp_dir', _capture_temp_path)

    ba.find_binaries(str(scan_dir), str(out_dir), ['excel'])

    assert os.path.dirname(created_paths[0]) == str(out_dir)
    assert os.path.basename(created_paths[0]).startswith(
        f'{TEMP_DIR_PREFIX}{timestamp_for_filename(fixed_start_time)}_')


def test_finalize_temp_output_copies_and_removes_temp_dir(tmp_path):
    """Finalization publishes artifacts"""
    temp_dir = tmp_path / 'temp'
    final_dir = tmp_path / 'final'
    temp_dir.mkdir()
    (temp_dir / 'report.xlsx').write_bytes(b'report')

    publish_ok = ba._finalize_temp_output(
        str(temp_dir), str(final_dir), str(temp_dir / 'missing.log'),
        '20260917_120000')

    assert publish_ok is True
    assert (final_dir / 'report.xlsx').read_bytes() == b'report'
    assert temp_dir.exists()


def test_finalize_temp_output_reports_copy_failure_and_removes_temp_dir(tmp_path, monkeypatch):
    """A publication failure is reported without forcing cleanup here."""
    temp_dir = tmp_path / 'temp'
    final_dir = tmp_path / 'final'
    temp_dir.mkdir()

    def fail_copytree(*args, **kwargs):
        raise OSError('copy failed')

    monkeypatch.setattr(ba.shutil, 'copytree', fail_copytree)

    publish_ok = ba._finalize_temp_output(
        str(temp_dir), str(final_dir), str(temp_dir / 'missing.log'),
        '20260917_120000')

    assert publish_ok is False
    assert temp_dir.exists()


def test_copy_failure_marks_analysis_unsuccessful(tmp_path, monkeypatch):
    """A failed result copy changes the analysis result to unsuccessful."""
    scan_dir = _scan_dir(tmp_path)
    out_dir = _out_dir(tmp_path)

    def fail_copytree(*args, **kwargs):
        raise OSError('copy failed')

    monkeypatch.setattr(ba.shutil, 'copytree', fail_copytree)

    success, _ = ba.find_binaries(str(scan_dir), str(out_dir), ['excel'])

    assert success is False


def test_success_path_cleans_temp_dir_once(tmp_path, monkeypatch):
    """The success path delegates temp cleanup to one place only."""
    scan_dir = _scan_dir(tmp_path)
    out_dir = _out_dir(tmp_path)
    real_cleanup = ba._cleanup_temp_dir
    cleanup_calls = []

    def capture_cleanup(path):
        cleanup_calls.append(path)
        return real_cleanup(path)

    monkeypatch.setattr(ba, '_cleanup_temp_dir', capture_cleanup)

    ba.find_binaries(str(scan_dir), str(out_dir), ['excel'])

    assert len(cleanup_calls) == 1


def test_stale_temp_dir_is_not_copied_into_output(tmp_path, monkeypatch):
    """A file left in the temp directory never leaks into the output directory.

    The copytree at the end of the run copies the whole temp directory into
    the output directory, so an excel left there by a previous run killed with
    SIGKILL or a power loss would show up among the results.
    """
    scan_dir = _scan_dir(tmp_path)
    out_dir = _out_dir(tmp_path)
    fixed_start_time = '20260827_000000'
    monkeypatch.setattr(ba, 'current_timestamp_utc', lambda: fixed_start_time)
    stale_temp = out_dir / (
        f'{TEMP_DIR_PREFIX}{timestamp_for_filename(fixed_start_time)}')
    stale_temp.mkdir()
    _write_xlsx(stale_temp / 'fosslight_report_bin_leftover.xlsx')

    ba.find_binaries(str(scan_dir), str(out_dir), ['excel'])

    assert not (out_dir / 'fosslight_report_bin_leftover.xlsx').exists()


def test_temp_dir_removed_on_keyboard_interrupt(tmp_path, monkeypatch):
    """Interrupting with Ctrl+C leaves no temp directory behind."""
    scan_dir = _scan_dir(tmp_path)
    out_dir = _out_dir(tmp_path)

    def _interrupt(bin_with_path):
        raise KeyboardInterrupt

    monkeypatch.setattr(ba, 'get_checksum_and_tlsh', _interrupt)

    with pytest.raises(KeyboardInterrupt):
        ba.find_binaries(str(scan_dir), str(out_dir), ['excel'])

    assert not _temp_dirs(out_dir)


def test_log_file_is_removed_with_temp_dir_on_interrupt(tmp_path, monkeypatch):
    """The interrupted run's log is removed with its temp directory."""
    scan_dir = _scan_dir(tmp_path)
    out_dir = _out_dir(tmp_path)

    def _interrupt(bin_with_path):
        raise KeyboardInterrupt

    monkeypatch.setattr(ba, 'get_checksum_and_tlsh', _interrupt)

    with pytest.raises(KeyboardInterrupt):
        ba.find_binaries(str(scan_dir), str(out_dir), ['excel'])

    assert not glob.glob(os.path.join(str(out_dir), 'fosslight_log_bin_*.txt'))


def test_temp_dir_removed_on_unexpected_exception(tmp_path, monkeypatch):
    """An unexpected exception leaves no temp directory behind."""
    scan_dir = _scan_dir(tmp_path)
    out_dir = _out_dir(tmp_path)

    def _boom(*args, **kwargs):
        raise RuntimeError("unexpected")

    monkeypatch.setattr(ba, 'get_excluded_paths', _boom)

    with pytest.raises(RuntimeError):
        ba.find_binaries(str(scan_dir), str(out_dir), ['excel'])

    assert not _temp_dirs(out_dir)


def test_temp_dir_removed_when_init_exits_before_returning(tmp_path, monkeypatch):
    """init() exiting before it returns still cleans up its temp directory.

    On Windows the spdx and cyclonedx formats are dropped, and init() calls
    sys.exit(0) once nothing is left. That happens after the temp directory has
    been created, so the cleanup cannot rely on init()'s return value.
    """
    scan_dir = _scan_dir(tmp_path)
    out_dir = _out_dir(tmp_path)
    monkeypatch.setattr(ba.platform, 'system', lambda: 'Windows')

    with pytest.raises(SystemExit):
        ba.find_binaries(str(scan_dir), str(out_dir), ['spdx-json'])

    assert not _temp_dirs(out_dir)


def test_temp_dir_removed_when_scan_path_is_missing(tmp_path):
    """The sys.exit raised by error_occured(exit=True) also cleans up."""
    out_dir = _out_dir(tmp_path)

    with pytest.raises(SystemExit):
        ba.find_binaries(str(tmp_path / 'no_such_dir'), str(out_dir), ['excel'])

    assert not _temp_dirs(out_dir)
