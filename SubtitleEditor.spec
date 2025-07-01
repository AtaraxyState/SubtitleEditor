# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('requirements.txt', '.'), ('C:\\Users\\Rain\\AppData\\Roaming\\Python\\Python313\\site-packages\\customtkinter\\assets', 'customtkinter/assets'), ('C:\\Users\\Rain\\AppData\\Roaming\\Python\\Python313\\site-packages\\customtkinter\\assets\\fonts', 'customtkinter/assets/fonts'), ('C:\\Users\\Rain\\AppData\\Roaming\\Python\\Python313\\site-packages\\customtkinter\\assets\\icons', 'customtkinter/assets/icons')],
    hiddenimports=['customtkinter', 'ffmpeg', 'PIL', 'PIL.Image', 'PIL._tkinter_finder', 'PIL.ImageTk', 'customtkinter.windows', 'customtkinter.windows.widgets', 'customtkinter.appearance_mode', 'customtkinter.theme_manager', 'customtkinter.settings', 'customtkinter.draw_engine', 'tkinter', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.simpledialog', 'tkinter.ttk', '_tkinter', 'threading', 'pathlib', 'subprocess', 'shutil', 'tempfile', 'json', 'os', 'sys', 'platform', 'time', 'ffmpeg._run', 'ffmpeg._probe', 'ffmpeg._dag', 'future', 'future.builtins', 'pkg_resources', 'setuptools', 'importlib', 'importlib.util', 'collections', 'collections.abc', 'typing', 'typing_extensions'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['FixTk', 'tcl', 'tk'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    name='SubtitleEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
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
