"""Gera a arte de teste, abre o editor e grava uma captura da janela."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication

from app.sample_art import gravar
from app.ui.main_window import JanelaPrincipal


def main() -> None:
    amostra = gravar(ROOT / "amostras" / "teste_dtf.png")
    aplicativo = QApplication([])
    janela = JanelaPrincipal()
    janela.resize(1440, 900)
    janela.show()
    janela.carregar_caminho(str(amostra))
    limite = time.time() + 30
    while time.time() < limite:
        aplicativo.processEvents()
        if janela.preview is not None and janela.preview_rev == janela.edit_rev:
            if janela.trabalhador is None or not janela.trabalhador.isRunning():
                break
        time.sleep(0.02)
    else:
        raise SystemExit("separação não terminou")
    janela.botoes_vista["split"].setChecked(True)
    janela._mostrar()
    janela._aplicar()
    aplicativo.processEvents()
    destino = ROOT / "docs" / "validacao-tela.png"
    janela.grab().save(str(destino))
    print(destino, destino.stat().st_size, "lpi", janela.preview.lpi)
    janela.close()


if __name__ == "__main__":
    main()
