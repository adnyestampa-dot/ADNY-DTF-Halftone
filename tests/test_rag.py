"""O RAG devolve trecho real e não inventa acerto."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rag.consultar import consultar


class Consulta(unittest.TestCase):
    def test_encontra_a_falha_do_motor(self) -> None:
        resultado = consultar("resultado da separação errado retícula sólida camiseta", k=3)
        fontes = [trecho["fonte"] for trecho in resultado["trechos"]]
        self.assertIn("rag/base/falha-do-motor-atual.md", fontes)
        self.assertGreater(resultado["trechos"][0]["pontuacao"], 0)

    def test_pergunta_sem_termo_nao_fabrica_trecho(self) -> None:
        resultado = consultar("xyzqwv bromzix 991823", k=3)
        self.assertEqual(resultado["trechos"], [])
        self.assertIn("Nenhum trecho", resultado["aviso"])

    def test_estrutura_de_criacao_entra_na_consulta_do_motor(self) -> None:
        resultado = consultar("estrutura de criação presença tom retícula base branca", k=4)
        fontes = {trecho["fonte"] for trecho in resultado["trechos"]}
        self.assertIn("rag/base/estrutura-de-criacao.md", fontes)


if __name__ == "__main__":
    unittest.main()
