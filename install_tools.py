#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Standalone tool installer for syft and grype.
This script can be run independently without any package dependencies.
"""

import platform
import tarfile
import zipfile
from pathlib import Path
from urllib.request import urlopen, urlretrieve


def get_platform_info():
    """Get platform and architecture information."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize architecture names
    if machine in ['x86_64', 'amd64']:
        arch = 'amd64'
    elif machine in ['aarch64', 'arm64']:
        arch = 'arm64'
    elif machine in ['i386', 'i686']:
        arch = '386'
    else:
        arch = machine

    return system, arch


def get_latest_release_url(tool_name, system, arch):
    """Get the latest release download URL for a tool."""
    import json

    # GitHub API to get latest release
    api_url = f"https://api.github.com/repos/anchore/{tool_name}/releases/latest"

    try:
        with urlopen(api_url) as response:
            release_data = json.loads(response.read().decode())

        # Find the right asset for our platform
        for asset in release_data['assets']:
            name = asset['name'].lower()
            if system in name and arch in name:
                if system == 'windows' and name.endswith('.zip'):
                    return asset['browser_download_url']
                elif system != 'windows' and name.endswith('.tar.gz'):
                    return asset['browser_download_url']

    except Exception as e:
        print(f"Failed to get release info for {tool_name}: {e}")

    # Fallback to direct URLs
    base_urls = {
        'syft': f'https://github.com/anchore/syft/releases/latest/download/syft_{system}_{arch}',
        'grype': f'https://github.com/anchore/grype/releases/latest/download/grype_{system}_{arch}'
    }

    if system == 'windows':
        return f"{base_urls[tool_name]}.zip"
    else:
        return f"{base_urls[tool_name]}.tar.gz"


def install_tool(tool_name, install_dir):
    """Install a tool (syft or grype) to the specified directory."""
    system, arch = get_platform_info()

    print(f"Installing {tool_name} for {system}/{arch}...")

    # Create install directory
    install_path = Path(install_dir)
    install_path.mkdir(parents=True, exist_ok=True)

    # Get download URL
    download_url = get_latest_release_url(tool_name, system, arch)

    # Download file
    if system == 'windows':
        archive_name = f"{tool_name}.zip"
    else:
        archive_name = f"{tool_name}.tar.gz"

    archive_path = install_path / archive_name

    try:
        print(f"Downloading {download_url}...")
        urlretrieve(download_url, archive_path)

        # Extract archive
        if system == 'windows':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(install_path)
        else:
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(install_path)

        # Make executable (Unix systems)
        if system != 'windows':
            tool_binary = install_path / tool_name
            if tool_binary.exists():
                tool_binary.chmod(0o755)

        # Clean up archive
        archive_path.unlink()

        print(f"✅ {tool_name} installed successfully!")
        return True

    except Exception as e:
        print(f"❌ Failed to install {tool_name}: {e}")
        return False


def install_syft_grype():
    """Install both syft and grype tools."""
    # Determine install directory
    home_dir = Path.home()
    install_dir = home_dir / '.local' / 'bin'

    print("Installing Syft and Grype tools...")
    print(f"Install directory: {install_dir}")

    # Install both tools
    syft_ok = install_tool('syft', install_dir)
    grype_ok = install_tool('grype', install_dir)

    if syft_ok and grype_ok:
        print("🎉 Both tools installed successfully!")
        print(f"Make sure {install_dir} is in your PATH")
        return True
    else:
        print("⚠️ Some tools failed to install")
        return False


if __name__ == '__main__':
    install_syft_grype()
