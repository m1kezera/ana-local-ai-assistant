# -*- mode: python ; coding: utf-8 -*-

import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
icon_path = os.path.join(project_root, 'prisma2.ico')

block_cipher = None

a = Analysis(
    [os.path.join(project_root, 'app_desktop.py')],
    pathex=[project_root],
    binaries=[],
    datas=[(icon_path, '.')],  # adiciona o ícone
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='app_desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=icon_path,  # usa o caminho do ícone corretamente
)
