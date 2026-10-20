"""Índice BM25 local. A pontuação vem dos termos do texto, sem valor inventado."""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGENS = (ROOT / "rag" / "base", ROOT / "docs")
TOKEN = re.compile(r"[a-z0-9]{2,}")


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(caractere for caractere in sem_acento if unicodedata.category(caractere) != "Mn")
    return sem_acento.lower()


def tokenizar(texto: str) -> list[str]:
    return TOKEN.findall(normalizar(texto))


def ler_corpus() -> list[dict]:
    trechos: list[dict] = []
    for pasta in ORIGENS:
        if not pasta.exists():
            continue
        for caminho in sorted(pasta.rglob("*.md")):
            trechos.extend(_fatiar(caminho))
    return trechos


def _fatiar(caminho: Path) -> list[dict]:
    texto = caminho.read_text(encoding="utf-8")
    fonte = caminho.relative_to(ROOT).as_posix()
    blocos = re.split(r"\n(?=# )", texto)
    saida: list[dict] = []
    for indice, bloco in enumerate(blocos):
        linhas = [linha for linha in bloco.splitlines() if linha.strip()]
        if not linhas:
            continue
        titulo = linhas[0].lstrip("# ").strip()
        corpo = "\n".join(linhas).strip()
        if len(tokenizar(corpo)) < 8:
            continue
        saida.append(
            {
                "id": f"{fonte}#{indice}",
                "fonte": fonte,
                "titulo": titulo,
                "texto": corpo,
            }
        )
    return saida


class Indice:
    def __init__(self, trechos: list[dict], k1: float = 1.5, b: float = 0.75) -> None:
        self.trechos = trechos
        self.k1 = k1
        self.b = b
        self.frequencias: list[Counter] = []
        self.tamanhos: list[int] = []
        documentos = Counter()
        for trecho in trechos:
            tokens = tokenizar(trecho["texto"])
            frequencia = Counter(tokens)
            self.frequencias.append(frequencia)
            self.tamanhos.append(len(tokens))
            for termo in frequencia:
                documentos[termo] += 1
        self.documentos = documentos
        self.quantidade = len(trechos)
        self.media = (sum(self.tamanhos) / self.quantidade) if self.quantidade else 1.0

    def pontuar(self, pergunta: str) -> list[float]:
        termos = tokenizar(pergunta)
        notas: list[float] = []
        for frequencia, tamanho in zip(self.frequencias, self.tamanhos):
            nota = 0.0
            for termo in termos:
                vezes = frequencia.get(termo, 0)
                if vezes == 0:
                    continue
                presentes = self.documentos[termo]
                idf = math.log(1.0 + (self.quantidade - presentes + 0.5) / (presentes + 0.5))
                norma = 1.0 - self.b + self.b * tamanho / self.media
                nota += idf * (vezes * (self.k1 + 1.0)) / (vezes + self.k1 * norma)
            notas.append(nota)
        return notas
