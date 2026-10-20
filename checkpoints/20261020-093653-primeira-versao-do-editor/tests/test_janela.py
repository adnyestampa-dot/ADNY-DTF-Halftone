"""A janela abre, separa e exporta sem diálogo."""

from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from PySide6.QtWidgets import QApplication

from app.engines.export_engine import alfa_binario
from app.ui.main_window import JanelaPrincipal


def esperar(janela: JanelaPrincipal, aplicativo: QApplication, segundos: float = 20) -> None:
    limite = time.time() + segundos
    while time.time() < limite:
        aplicativo.processEvents()
        if janela.preview is not None and janela.preview_rev == janela.edit_rev:
            if janela.trabalhador is None or not janela.trabalhador.isRunning():
                return
        time.sleep(0.02)
    raise TimeoutError("A separação não terminou.")


class Janela(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.aplicativo = QApplication.instance() or QApplication([])

    def test_separa_aplica_e_exporta(self) -> None:
        janela = JanelaPrincipal()
        janela.show()
        imagem = np.zeros((180, 220, 4), np.uint8)
        imagem[..., 3] = 255
        imagem[30:140, 40:180] = (240, 40, 60, 255)
        janela.carregar_array(imagem)
        esperar(janela, self.aplicativo)
        self.assertTrue(alfa_binario(janela.preview.separacao))
        self.assertEqual(janela.preview.lpi, 30.0)
        self.assertFalse(janela.exportar.isEnabled())
        janela._aplicar()
        self.assertTrue(janela.exportar.isEnabled())
        indice = janela.lpi.findData(25)
        janela.lpi.setCurrentIndex(indice)
        self.assertFalse(janela.exportar.isEnabled())
        esperar(janela, self.aplicativo)
        self.assertEqual(janela.preview.lpi, 25.0)
        janela._aplicar()
        with tempfile.TemporaryDirectory() as pasta:
            caminhos = janela.exportar_para(Path(pasta) / "arte.png")
            self.assertEqual(caminhos[0].suffix, ".png")
            self.assertTrue(caminhos[0].exists())
        janela.close()


if __name__ == "__main__":
    unittest.main()
