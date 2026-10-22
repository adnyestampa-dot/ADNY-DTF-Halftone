"""Prepara ZIP portátil, procedência e hashes após os testes do .exe."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import os
import zipfile

ROOT = Path(__file__).resolve().parents[1]
dist = ROOT / "dist"
exe = dist / "ADNY-DTF-Halftone.exe"
resultado = json.loads((ROOT / "validacao-exe" / "resultado.json").read_text(encoding="utf-8"))
assert resultado["ok"] and resultado["frozen"]
sha = hashlib.sha256(exe.read_bytes()).hexdigest()
(dist / "ADNY-DTF-Halftone.exe.sha256").write_text(sha + "  " + exe.name + "\n", encoding="ascii")
build = {"commit": os.environ["GITHUB_SHA"], "platform": "Windows x64", "exe_sha256": sha,
         "versions": {p: importlib.metadata.version(p) for p in ["PySide6", "numpy", "Pillow", "opencv-python-headless", "pyinstaller"]},
         "validation": resultado}
# Não divulgar caminhos da máquina de compilação no pacote distribuído.
build["validation"].pop("dados_persistentes", None)
(dist / "BUILD.json").write_text(json.dumps(build, indent=2), encoding="utf-8")
with zipfile.ZipFile(dist / "ADNY-DTF-Halftone-Windows-x64.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for p in [exe, dist / "BUILD.json", dist / "ADNY-DTF-Halftone.exe.sha256", ROOT / "ABRIR-ADNY.bat", ROOT / "LEIA-ME-WINDOWS.md"]:
        z.write(p, p.name)
with (dist / "SHA256SUMS.txt").open("w", encoding="ascii") as f:
    for p in [exe, dist / "ADNY-DTF-Halftone-Windows-x64.zip"]:
        f.write(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name + "\n")
