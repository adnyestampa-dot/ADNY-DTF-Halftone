"""Mantém os dados do executável fora da extração temporária do PyInstaller."""
from pathlib import Path
import os
import sys


def raiz_de_dados() -> Path:
    if getattr(sys, "frozen", False):
        local = os.environ.get("LOCALAPPDATA")
        base = Path(local) if local else Path.home() / "AppData" / "Local"
        pasta = base / "ADNY-DTF-Halftone"
        pasta.mkdir(parents=True, exist_ok=True)
        return pasta
    return Path(__file__).resolve().parents[1]
