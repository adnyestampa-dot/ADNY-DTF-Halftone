"""Abre o monitor, se ele ainda não estiver ativo, e em seguida o editor."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def _vivo(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def garantir_monitor() -> None:
    pid_path = ROOT / "monitor" / "monitor.pid"
    if pid_path.exists():
        try:
            if _vivo(int(pid_path.read_text(encoding="utf-8").strip())):
                return
        except ValueError:
            pass
    executavel = Path(sys.executable)
    janela = executavel.with_name("pythonw.exe")
    comando = [str(janela if janela.exists() else executavel), str(ROOT / "monitor" / "monitor.py")]
    subprocess.Popen(
        comando,
        cwd=ROOT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


if __name__ == "__main__":
    garantir_monitor()
    from app.main import main

    raise SystemExit(main())
