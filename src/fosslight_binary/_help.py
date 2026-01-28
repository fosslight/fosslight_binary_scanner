#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
from fosslight_util.help import PrintHelpMsg
from fosslight_util.output_format import SUPPORT_FORMAT

_HELP_MESSAGE_BINARY = f"""
    📖 Usage
    ────────────────────────────────────────────────────────────────────
    fosslight_bin [options] <arguments>

    📝 Description
    ────────────────────────────────────────────────────────────────────
    FOSSLight Binary Scanner extracts binaries and retrieves open source
    and license information by comparing similarity with binaries stored
    in the Binary DB using TLSH (Trend Micro Locality Sensitive Hash).

    📚 Guide: https://fosslight.org/fosslight-guide/scanner/4_binary.html

    ⚙️  General Options
    ────────────────────────────────────────────────────────────────────
    -p <path>              Binary path to analyze (default: current directory)
    -o <path>              Output file path or directory
    -f <format>            Output formats: {', '.join(SUPPORT_FORMAT)}
                           (multiple formats can be specified, separated by space)
    -e <pattern>           Exclude paths from analysis (files and directories)
                           ⚠️  IMPORTANT: Always wrap in quotes to avoid shell expansion
                           Example: fosslight_bin -e "test/" "*.jar"
    -h                     Show this help message
    -v                     Show version information

    🔍 Scanner-Specific Options
    ────────────────────────────────────────────────────────────────────
    -s                     Extract only the binary list in simple mode
    -d <db_url>            DB Connection (format: 'postgresql://user:pass@host:port/db')
    --notice               Print the open source license notice text
    --no_correction        Skip OSS information correction with sbom-info.yaml
    --correct_fpath <path> Path to custom sbom-info.yaml file

    💡 Examples
    ────────────────────────────────────────────────────────────────────
    # Scan current directory
    fosslight_bin

    # Scan specific path with exclusions
    fosslight_bin -p /path/to/binaries -e "test/" "*.so"

    # Generate output in specific format
    fosslight_bin -f excel -o results/

    # Simple mode (extract binary list only)
    fosslight_bin -s -o binary_list.txt

    # Connect to Binary DB for OSS information
    fosslight_bin -d "postgresql://user:pass@localhost:5432/exampledb"
"""


def print_help_msg():
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_BINARY)
    helpMsg.print_help_msg(True)
