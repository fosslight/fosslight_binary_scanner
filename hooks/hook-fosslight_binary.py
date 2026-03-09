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
