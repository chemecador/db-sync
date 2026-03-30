# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_dynamic_libs


binaries = collect_dynamic_libs("pymssql")

a = Analysis(
    ["src/db_sync/__main__.py"],
    pathex=["src"],
    binaries=binaries,
    datas=[("openssl.cnf", ".")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="db-sync",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="db-sync",
)
