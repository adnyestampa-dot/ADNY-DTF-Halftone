"""Janela principal."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.ui.main_window import JanelaPrincipal


def main() -> int:
    aplicativo = QApplication(sys.argv)
    janela = JanelaPrincipal()
    if len(sys.argv) > 1:
        janela.carregar_caminho(sys.argv[1])
    janela.show()
    return aplicativo.exec()


if __name__ == "__main__":
    raise SystemExit(main())
