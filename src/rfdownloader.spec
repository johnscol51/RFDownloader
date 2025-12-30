# -*- mode: python ; coding: utf-8 -*-
import sys
import platform

# Detect current OS
current_os = platform.system().lower()

# Default icon (Windows/Linux use .ico, macOS uses .icns)
if current_os == "darwin":   # macOS
    use_upx = False             # UPX often breaks macOS binaries
    app_icon = ['icooo.ico']
elif current_os == "windows":
    app_icon = ['icooo.ico']
    use_upx = True              # safe on Windows
else:  # Linux
    app_icon = ['icooo.ico']    # icon usually ignored by Linux DEs
    use_upx = True

a = Analysis(
    ['rfdownloader.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('GPS-logo.png', '.'),          # your logo
        ('README-macOS.txt', '.'),      # bundle the README
    ],
    hiddenimports=['tkinter',
 "PIL", "PIL._imaging", "PIL._imagingtk", "PIL.Image", "PIL.ImageFilter", "PIL.ImageOps", "PIL.ImageEnhance", "PIL.ImageStat", "PIL.ImageChops", "PIL.ImageFile","PIL._tkinter_finder",
    ],   # add GUI libs if needed
    hookspath=[],
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
    name='rfdownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=use_upx,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,               # suppress console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,      # macOS signing (leave None if not signing)
    entitlements_file=None,      # macOS entitlements (leave None if not signing)
    icon=app_icon,
)

