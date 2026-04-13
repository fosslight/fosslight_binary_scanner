#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2021 LG Electronics

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('fosslight_binary')

# Collect binaryornot package including data files
datas_binaryornot, binaries_binaryornot, hiddenimports_binaryornot = collect_all('binaryornot')
datas += datas_binaryornot
binaries += binaries_binaryornot
hiddenimports += hiddenimports_binaryornot

# Collect python-magic / python-magic-bin (magic database and DLLs)
datas_magic, binaries_magic, hiddenimports_magic = collect_all('magic')
datas += datas_magic
binaries += binaries_magic
hiddenimports += hiddenimports_magic

# Collect rfc3987_syntax data files (.lark grammar file)
datas_rfc, binaries_rfc, hiddenimports_rfc = collect_all('rfc3987_syntax')
datas += datas_rfc
binaries += binaries_rfc
hiddenimports += hiddenimports_rfc
