# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['cli.py'],
    pathex=['src'],  # source package path for fosslight_binary
    binaries=[],
    datas=[
        # Use original repository location (no pre-install): third_party/dependency-check
        ('third_party/dependency-check/bin', 'third_party/dependency-check/bin'),
        ('third_party/dependency-check/lib', 'third_party/dependency-check/lib'),
        ('third_party/dependency-check/licenses', 'third_party/dependency-check/licenses'),
        ('third_party/dependency-check', 'third_party/dependency-check'),  # txt/md root files
        ('LICENSES', 'LICENSES'),
        ('LICENSE', 'LICENSES'),
    ],
    hiddenimports=[
        'pkg_resources.extern',
        'fosslight_binary.cli',
        'fosslight_binary._jar_analysis',
        'fosslight_binary._binary',
    ],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='cli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
