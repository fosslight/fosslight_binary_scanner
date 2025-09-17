#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2025 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import stat
import subprocess
import tempfile
import urllib.request
import zipfile
import sys

logger = logging.getLogger(__name__)
DEPENDENCY_CHECK_VERSION = "12.1.7"


def _install_dependency_check():
    """Install OWASP dependency-check"""
    try:
        # Skip if explicitly disabled
        if os.environ.get('FOSSLIGHT_SKIP_AUTO_INSTALL', '').lower() in ('1', 'true', 'yes'):
            logger.info("Auto-install disabled by environment variable")
            return

        env_home = os.environ.get('DEPENDENCY_CHECK_HOME', '').strip()
        install_dir = None
        forced_env = False
        if env_home:
            # Normalize
            env_home_abs = os.path.abspath(env_home)
            # Detect if env_home already the actual extracted root (ends with dependency-check)
            candidate_bin_win = os.path.join(env_home_abs, 'bin', 'dependency-check.bat')
            candidate_bin_nix = os.path.join(env_home_abs, 'bin', 'dependency-check.sh')
            if os.path.exists(candidate_bin_win) or os.path.exists(candidate_bin_nix):
                # env points directly to dependency-check root; install_dir is its parent
                install_dir = os.path.dirname(env_home_abs)
                forced_env = True
            else:
                # Assume env_home is the base directory where we should extract dependency-check/
                install_dir = env_home_abs

        if not install_dir:
            # Fallback hierarchy: executable dir (if frozen) -> CWD
            candidate_base = None
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(os.path.abspath(sys.executable))
                candidate_base = os.path.join(exe_dir, 'fosslight_dc_bin')

                if not os.access(exe_dir, os.W_OK):
                    candidate_base = None
                else:
                    logger.debug(f"Using executable directory base: {candidate_base}")
            if not candidate_base:
                candidate_base = os.path.abspath(os.path.join(os.getcwd(), 'fosslight_dc_bin'))
            install_dir = candidate_base
        else:
            logger.debug(f"Resolved install_dir: {install_dir}")
        bin_dir = os.path.join(install_dir, 'dependency-check', 'bin')
        if sys.platform.startswith('win'):
            dc_path = os.path.join(bin_dir, 'dependency-check.bat')
        else:
            dc_path = os.path.join(bin_dir, 'dependency-check.sh')

        # Check if dependency-check already exists
        if os.path.exists(dc_path):
            try:
                result = subprocess.run([dc_path, '--version'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.debug("dependency-check already installed and working")
                    # If we detected an existing root via env, retain it, else set home now.
                    if forced_env:
                        os.environ['DEPENDENCY_CHECK_HOME'] = env_home_abs
                    else:
                        os.environ['DEPENDENCY_CHECK_HOME'] = os.path.join(install_dir, 'dependency-check')
                    os.environ['DEPENDENCY_CHECK_VERSION'] = DEPENDENCY_CHECK_VERSION
                    return
            except (subprocess.TimeoutExpired, FileNotFoundError) as ex:
                logger.debug(f"Exception in dependency-check --version: {ex}")
                pass

        # Download URL
        download_url = (f"https://github.com/dependency-check/DependencyCheck/releases/"
                        f"download/v{DEPENDENCY_CHECK_VERSION}/"
                        f"dependency-check-{DEPENDENCY_CHECK_VERSION}-release.zip")

        os.makedirs(install_dir, exist_ok=True)
        logger.info(f"Downloading dependency-check {DEPENDENCY_CHECK_VERSION} from {download_url} ...")

        # Download and extract
        with urllib.request.urlopen(download_url) as response:
            content = response.read()

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_zip_path = tmp_file.name

        with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_dir)
        os.unlink(tmp_file.name)

        # Make shell scripts executable
        if os.path.exists(bin_dir):
            if sys.platform.startswith('win'):
                # Windows: .bat files only
                scripts = ["dependency-check.bat"]
            else:
                # Linux/macOS: .sh files only
                scripts = ["dependency-check.sh", "completion-for-dependency-check.sh"]

            for script in scripts:
                script_path = os.path.join(bin_dir, script)
                if os.path.exists(script_path):
                    st = os.stat(script_path)
                    os.chmod(script_path, st.st_mode | stat.S_IEXEC)

        logger.info("✅ OWASP dependency-check installed successfully!")
        logger.info(f"Installed to: {os.path.join(install_dir, 'dependency-check')}")

        # Set environment variables after successful installation
        os.environ['DEPENDENCY_CHECK_VERSION'] = DEPENDENCY_CHECK_VERSION
        os.environ['DEPENDENCY_CHECK_HOME'] = os.path.join(install_dir, 'dependency-check')

        return True

    except Exception as e:
        logger.error(f"Failed to install dependency-check: {e}")
        logger.info("dependency-check can be installed manually from: https://github.com/dependency-check/DependencyCheck/releases")
        return False


def _auto_install_dependencies():
    """Auto-install required dependencies if not present."""
    # Only run this once per session
    if hasattr(_auto_install_dependencies, '_already_run'):
        return
    _auto_install_dependencies._already_run = True

    try:
        # Install binary version
        _install_dependency_check()

        logger.info(f"✅ dependency-check setup completed with version {DEPENDENCY_CHECK_VERSION}")
    except Exception as e:
        logger.warning(f"Auto-install failed: {e}")


# Auto-install on import
_auto_install_dependencies()
