import os
import sys


def generate_spec(cwd: str, mcmd_file: str, imports: list | dict):
    """Generates a PyInstaller .spec file configured for the current project."""
    entry_script = os.path.abspath(sys.argv[0])
    script_name = os.path.basename(entry_script)
    exe_name = os.path.splitext(script_name)[0]
    spec_path = os.path.join(cwd, f"{exe_name}.spec")
    mcmd_name = os.path.basename(mcmd_file)

    # Flatten imports for hiddenimports
    hidden_imports = []
    if isinstance(imports, list):
        hidden_imports = imports
    elif isinstance(imports, dict):
        hidden_imports = list(imports.keys())

    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['{script_name}'],
    pathex=[],
    binaries=[],
    datas=[('{mcmd_name}', '.'), ('__compiled__', '__compiled__')],
    hiddenimports={repr(hidden_imports)},
    hookspath=[],
    hooksconfig={{}},
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
    name='{exe_name}',
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
)"""
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    f.close()