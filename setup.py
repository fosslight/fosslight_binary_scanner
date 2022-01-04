#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
from codecs import open
from setuptools import setup, find_packages

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

with open('requirements.txt', 'r', 'utf-8') as f:
    install_requires = f.read().splitlines()

if __name__ == "__main__":
    setup(
        name='fosslight_binary',
        version='4.0.3',
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
                     "Programming Language :: Python :: 3.6",
                     "Programming Language :: Python :: 3.7",
                     "Programming Language :: Python :: 3.8",
                     "Programming Language :: Python :: 3.9", ],
        install_requires=install_requires,
        extras_require={
            ':sys_platform == "win32"': [
                'python-magic-bin'
            ],
            ':"darwin" in sys_platform': [
                'python-magic-bin'
            ],
            ':"linux" in sys_platform': [
                'python-magic'
            ],
        },
        entry_points={
            "console_scripts": [
                "binary_analysis = fosslight_binary.binary_analysis:main",
                "fosslight_bin = fosslight_binary.binary_analysis:main",
                "fosslight_binary = fosslight_binary.binary_analysis:main",
            ]
        }
    )
