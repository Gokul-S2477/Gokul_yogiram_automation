# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

streamlit_datas, streamlit_binaries, streamlit_hiddenimports = collect_all("streamlit")

hiddenimports = (
    streamlit_hiddenimports
    + collect_submodules("core")
    + collect_submodules("modules")
    + collect_submodules("ui")
)


def collect_package_files(package_name):
    files = []
    package_root = Path(package_name)
    for path in package_root.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        relative_parent = path.parent.as_posix()
        files.append((str(path), relative_parent))
    return files


datas = (
    streamlit_datas
    + copy_metadata("streamlit")
    + [
        ("app.py", "."),
        ("config", "config"),
    ]
    + collect_package_files("core")
    + collect_package_files("modules")
    + collect_package_files("ui")
    + collect_package_files("utils")
)


a = Analysis(
    ["desktop_launcher.py"],
    pathex=["."],
    binaries=streamlit_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name="PharmaForecastApp",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="PharmaForecastApp",
)
