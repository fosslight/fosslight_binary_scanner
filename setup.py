#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
from codecs import open
import os
import shutil
import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)

        # Skip auto-install if explicitly disabled
        if os.environ.get('FOSSLIGHT_SKIP_AUTO_INSTALL', '').lower() in ('1', 'true', 'yes'):
            print("Auto-install disabled by environment variable")
            return

        # Install syft and grype using standalone installer
        try:
            print("Installing syft and grype...")
            # Use standalone installer script - no package dependencies!
            script_path = os.path.join(os.path.dirname(__file__), 'install_tools.py')
            if os.path.exists(script_path):
                result = subprocess.run([sys.executable, script_path],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    print("Syft and grype installation completed.")
                else:
                    print(f"Warning: Tool installation failed: {result.stderr}")
            else:
                print("Warning: install_tools.py not found, skipping auto-install")
        except Exception as e:
            print(f"Warning: Failed to auto-install syft/grype: {e}")
            print("You can install them manually or they will be installed on first use.")


with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

with open('requirements.txt', 'r', 'utf-8') as f:
    install_requires = f.read().splitlines()

_PACKAEG_NAME = 'fosslight_binary'
_LICENSE_FILE = 'LICENSE'
_LICENSE_DIR = 'LICENSES'

if __name__ == "__main__":
    dest_path = os.path.join('src', _PACKAEG_NAME, _LICENSE_DIR)
    try:
        if not os.path.exists(dest_path):
            os.mkdir(dest_path)
        if os.path.isfile(_LICENSE_FILE):
            shutil.copy(_LICENSE_FILE, dest_path)
        if os.path.isdir(_LICENSE_DIR):
            license_f = [f_name for f_name in os.listdir(_LICENSE_DIR) if f_name.upper().startswith(_LICENSE_FILE)]
            for lic_f in license_f:
                shutil.copy(os.path.join(_LICENSE_DIR, lic_f), dest_path)
    except Exception as e:
        print(f'Warning: Fail to copy the license text: {e}')

    setup(
        name=_PACKAEG_NAME,
        version='5.1.9',
        package_dir={"": "src"},
        packages=find_packages(where='src'),
        description='FOSSLight Binary Scanner',
        long_description=readme,
        long_description_content_type='text/markdown',
        license='Apache-2.0',
        author='LG Electronics',
        url='https://github.com/fosslight/fosslight_binary_scanner',
        download_url='https://github.com/fosslight/fosslight_binary_scanner',
        classifiers=['License :: OSI Approved :: Apache Software License',
                     "Programming Language :: Python :: 3",
                     "Programming Language :: Python :: 3.10",
                     "Programming Language :: Python :: 3.11",
                     "Programming Language :: Python :: 3.12"],
        python_requires='>=3.10,<3.13',
        install_requires=install_requires,
        extras_require={
            ':sys_platform == "win32"': [
                'python-magic-bin'
            ],
            ':"darwin" in sys_platform': [
                'python-magic'
            ],
            ':"linux" in sys_platform': [
                'python-magic'
            ],
        },
        package_data={_PACKAEG_NAME: [os.path.join(_LICENSE_DIR, '*')]},
        include_package_data=True,
        # Include install_tools.py in the package
        data_files=[
            ('', ['install_tools.py']),
        ],
        cmdclass={
            'install': PostInstallCommand,
        },
        entry_points={
            "console_scripts": [
                "binary_analysis = fosslight_binary.cli:main",
                "fosslight_bin = fosslight_binary.cli:main",
                "fosslight_binary = fosslight_binary.cli:main",
                "fosslight_install_tools = fosslight_binary.install_cli:main",
            ]
        }
    )
    shutil.rmtree(dest_path, ignore_errors=True)
