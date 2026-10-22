"""Janela principal."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QLocale
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app import NOME
from app.ui.main_window import JanelaPrincipal


def main() -> int:
    QLocale.setDefault(QLocale(QLocale.Language.Portuguese, QLocale.Country.Brazil))
    aplicativo = QApplication(sys.argv)
    aplicativo.setApplicationName(NOME)
    aplicativo.setApplicationDisplayName(NOME)
    if getattr(sys, "frozen", False):
        icon_path = Path(sys._MEIPASS) / "adny-icon.png"
    else:
        icon_path = Path(__file__).resolve().parents[1] / "packaging" / "adny-icon.png"
    if icon_path.is_file():
        aplicativo.setWindowIcon(QIcon(str(icon_path)))
    janela = JanelaPrincipal()
    if len(sys.argv) > 1:
        janela.carregar_caminho(sys.argv[1])
    janela.show()
    return aplicativo.exec()


if __name__ == "__main__":
    raise SystemExit(main())
