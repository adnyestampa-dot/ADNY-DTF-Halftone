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
        self.assertTrue(janela.exportar.isEnabled())
        self.assertTrue(janela.acao_salvar.isEnabled())
        indice = janela.lpi.findData(25)
        janela.lpi.setCurrentIndex(indice)
        self.assertFalse(janela.exportar.isEnabled())
        esperar(janela, self.aplicativo)
        self.assertEqual(janela.preview.lpi, 25.0)
        self.assertTrue(janela.exportar.isEnabled())
        janela._aplicar()
        with tempfile.TemporaryDirectory() as pasta:
            caminhos = janela.exportar_para(Path(pasta) / "arte.png")
            self.assertEqual(caminhos[0].suffix, ".png")
            self.assertTrue(caminhos[0].exists())
            import app.ui.main_window as modulo

            anterior = modulo.ROOT
            modulo.ROOT = Path(pasta)
            try:
                janela._salvar_interno()
                self.assertTrue((Path(pasta) / "dados" / "projetos" / "projeto.dtx").exists())
            finally:
                modulo.ROOT = anterior
            self.assertEqual(janela.estado.text(), "●  Projeto salvo")
        janela.close()

    def test_original_e_lado_a_lado_mostram_a_arte(self) -> None:
        janela = JanelaPrincipal()
        janela.show()
        imagem = np.zeros((80, 160, 4), np.uint8)
        imagem[16:64, 16:144] = (180, 30, 40, 180)
        janela.carregar_array(imagem)
        self.aplicativo.processEvents()
        janela._definir_vista("original")
        composto = janela._sobrepor(imagem)
        self.assertEqual(janela.vista, "original")
        self.assertEqual(janela.tela.modo, "original")
        cor = janela.tela.esquerda.toImage().pixelColor(40, 40)
        self.assertEqual((cor.red(), cor.green(), cor.blue()), tuple(int(v) for v in composto[40, 40, 0:3]))
        self.assertGreater(cor.red(), 150)
        self.assertNotEqual((cor.red(), cor.green(), cor.blue()), (214, 214, 214))
        janela._definir_vista("split")
        self.assertEqual(janela.tela.modo, "split")
        esquerda = janela.tela.esquerda.toImage().pixelColor(40, 40)
        self.assertEqual((esquerda.red(), esquerda.green(), esquerda.blue()), (cor.red(), cor.green(), cor.blue()))
        self.assertIsNotNone(janela.tela.direita)
        janela.close()

    def test_fundo_da_camisa_fica_atras_das_vistas(self) -> None:
        janela = JanelaPrincipal()
        janela.show()
        self.assertEqual(janela.fundo_camisa.text(), "Visualizar fundo da camisa")
        self.assertFalse(janela.fundo_camisa.isChecked())
        imagem = np.zeros((48, 96, 4), np.uint8)
        imagem[12:36, 24:72] = (200, 20, 20, 255)
        janela.carregar_array(imagem)
        self.aplicativo.processEvents()

        def canto(pixmap):
            cor = pixmap.toImage().pixelColor(2, 2)
            return cor.red(), cor.green(), cor.blue()

        self.assertNotEqual(canto(janela.tela.esquerda), (0, 0, 0))
        janela.fundo_camisa.setChecked(True)
        self.aplicativo.processEvents()
        self.assertTrue(janela.ajustes.shirt_preview)
        self.assertTrue(janela.preview_camisa.isChecked())
        self.assertEqual(canto(janela.tela.esquerda), (0, 0, 0))
        miolo = janela.tela.esquerda.toImage().pixelColor(48, 24)
        self.assertGreater(miolo.red(), 150)
        janela._definir_cor_fundo((0, 0, 255))
        self.assertEqual(canto(janela.tela.esquerda), (0, 0, 255))
        self.assertEqual(janela.vista, "original")
        esperar(janela, self.aplicativo)
        janela._definir_vista("separation")
        self.assertEqual(canto(janela.tela.esquerda), (0, 0, 255))
        janela._definir_vista("split")
        self.assertEqual(janela.tela.modo, "split")
        self.assertEqual(canto(janela.tela.esquerda), (0, 0, 255))
        self.assertEqual(canto(janela.tela.direita), (0, 0, 255))
        janela.close()


if __name__ == "__main__":
    unittest.main()
