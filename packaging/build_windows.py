"""Compila o editor em um único executável Windows x64."""
from pathlib import Path
import os
import platform
import sys
import PyInstaller.__main__

ROOT = Path(__file__).resolve().parents[1]
ICON = ROOT / "packaging" / "adny.ico"
if sys.platform != "win32" or platform.architecture()[0] != "64bit":
    raise SystemExit("Execute este empacotamento no Windows com Python de 64 bits.")

PyInstaller.__main__.run([
    str(ROOT / "packaging" / "windows_entry.py"),
    "--name", "ADNY-DTF-Halftone", "--onefile", "--windowed", "--noupx", "--clean", "--noconfirm",
    "--paths", str(ROOT), "--distpath", str(ROOT / "dist"),
    "--workpath", str(ROOT / "build"), "--specpath", str(ROOT / "build"),
    "--icon", str(ICON),
    "--add-data", f"{ROOT / 'packaging' / 'adny-icon.png'}{os.pathsep}.",
])
exe = ROOT / "dist" / "ADNY-DTF-Halftone.exe"
assert exe.is_file() and exe.open("rb").read(2) == b"MZ"
