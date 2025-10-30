#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2025 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)

# Static path always used; environment overrides are ignored now.
_PKG_DIR = os.path.dirname(__file__)
_DC_HOME = os.path.join(_PKG_DIR, 'third_party', 'dependency-check')

# Fallback: project root layout (editable install) or current working directory
if not os.path.isdir(_DC_HOME):
    _PROJECT_ROOT = os.path.abspath(os.path.join(_PKG_DIR, '..', '..'))
    candidate = os.path.join(_PROJECT_ROOT, 'third_party', 'dependency-check')
    if os.path.isdir(candidate):
        _DC_HOME = candidate
    else:
        cwd_candidate = os.path.join(os.getcwd(), 'third_party', 'dependency-check')
        if os.path.isdir(cwd_candidate):
            _DC_HOME = cwd_candidate
if not os.path.isdir(_DC_HOME) and getattr(sys, 'frozen', False):
    # Frozen executable scenario (PyInstaller onefile): check exe dir and _MEIPASS temp dir.
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    exe_candidate = os.path.join(exe_dir, 'third_party', 'dependency-check')
    if os.path.isdir(exe_candidate):
        _DC_HOME = exe_candidate
    else:
        tmp_root = getattr(sys, '_MEIPASS', '')
        if tmp_root:
            tmp_candidate = os.path.join(tmp_root, 'third_party', 'dependency-check')
            if os.path.isdir(tmp_candidate):
                _DC_HOME = tmp_candidate


def get_dependency_check_script():
    """Return path to static dependency-check CLI script or None if missing."""
    bin_dir = os.path.join(_DC_HOME, 'bin')
    if sys.platform.startswith('win'):
        script = os.path.join(bin_dir, 'dependency-check.bat')
    else:
        script = os.path.join(bin_dir, 'dependency-check.sh')
    return script if os.path.isfile(script) else None


def _set_version_env(script_path):
    """Attempt to run '--version' to populate DEPENDENCY_CHECK_VERSION; ignore errors."""
    if not script_path or not os.path.exists(script_path):
        return
    try:
        result = subprocess.run([script_path, '--version'], capture_output=True, text=True, timeout=8)
        if result.returncode == 0:
            version_line = (result.stdout or '').strip().splitlines()[-1]
            if version_line:
                os.environ['DEPENDENCY_CHECK_VERSION'] = version_line
    except Exception as ex:
        logger.debug(f"Could not obtain dependency-check version: {ex}")


def _init_static_dependency_check():
    if not os.path.isdir(_DC_HOME):
        logger.info("Dependency-check not found under third_party/dependency-check.")
        return
    os.environ['DEPENDENCY_CHECK_HOME'] = _DC_HOME
    script = get_dependency_check_script()
    _set_version_env(script)
    logger.debug(f"dependency-check home set to: {_DC_HOME}")


# Perform lightweight initialization (no network, no extraction)
_init_static_dependency_check()

__all__ = [
    'get_dependency_check_script'
]
