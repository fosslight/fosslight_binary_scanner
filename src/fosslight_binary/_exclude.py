# Copyright (c) 2026 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

"""Binary-scanner filename excludes."""

from fosslight_util.exclude import is_excluded_filename

# Scanner output binaries that should not be re-analyzed.
EXCLUDE_FILENAME_BINARY = frozenset({
    "fosslight_bin", "fosslight_bin.exe",
})


def is_excluded_binary_filename(file_path: str) -> bool:
    return is_excluded_filename(file_path, EXCLUDE_FILENAME_BINARY)
