# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Anaconda路径
anaconda_path = 'C:/Users/qhlin/anaconda3'

# 收集必要的数据文件
datas = [
    ('config', 'config'),
    ('examples', 'examples'),
    ('.env.example', '.'),
    ('src', 'src'),  # 添加整个src目录
]

# 添加tkinter的TCL/TK库文件
tcl_lib = os.path.join(anaconda_path, 'Library/lib/tcl8.6')
tk_lib = os.path.join(anaconda_path, 'Library/lib/tk8.6')
if os.path.exists(tcl_lib):
    datas.append((tcl_lib, 'tcl'))
if os.path.exists(tk_lib):
    datas.append((tk_lib, 'tk'))

# 需要的二进制文件（tkinter DLLs）
binaries = [
    (os.path.join(anaconda_path, 'Library/bin/tcl86t.dll'), '.'),
    (os.path.join(anaconda_path, 'Library/bin/tk86t.dll'), '.'),
    (os.path.join(anaconda_path, 'DLLs/_tkinter.pyd'), '.'),
    # SSL支持（requests需要）
    (os.path.join(anaconda_path, 'Library/bin/libssl-3-x64.dll'), '.'),
    (os.path.join(anaconda_path, 'Library/bin/libcrypto-3-x64.dll'), '.'),
]

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'tkinter', '_tkinter', 'tkinter.ttk', 'tkinter.messagebox',
        'src', 'src.guardian', 'src.utils',
        'src.detectors', 'src.detectors.regex_detector', 'src.detectors.keyword_detector',
        'src.detectors.ai_detector', 'src.detectors.llm_detector', 'src.detectors.llm_detector_api',
        'src.obfuscators', 'src.obfuscators.obfuscator',
        'yaml', 'requests', 'dotenv'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'cv2',
        'torch', 'tensorflow', 'sklearn', 'IPython', 'jupyter',
        'pytest', 'setuptools', 'wheel', 'pip'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AI_Chat_Guardian',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 生产版本不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI_Chat_Guardian',
)
