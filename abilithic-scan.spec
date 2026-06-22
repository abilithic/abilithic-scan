# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Abilithic Scan (PyInstaller 6.x).
# Build:  pyinstaller abilithic-scan.spec --noconfirm --clean
#
# NOTE on bundling Nmap:
#   Drop a Windows Nmap build into abilithic_scan/data/nmap/ (nmap.exe + its
#   data files) BEFORE building to ship a self-contained binary. Mind the Nmap
#   Public Source License (NPSL). Npcap is NOT redistributed here; the app
#   guides the user to install the official Npcap on first run (see README).

datas = [
    ("abilithic_scan/data", "abilithic_scan/data"),
    ("abilithic_scan/i18n/locales", "abilithic_scan/i18n/locales"),
    ("assets", "assets"),
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=["openpyxl"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "PyQt5", "PyQt6"],
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
    name="AbilithicScan",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                 # GUI app, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version="version_info.txt",
    icon="assets/abilithic-scan.ico",
)
