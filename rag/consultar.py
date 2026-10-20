"""Consulta do RAG e registro verificável para os agentes."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from rag.indice import Indice, ler_corpus

ROOT = Path(__file__).resolve().parents[1]
CONSULTAS = ROOT / "rag" / "consultas"


def consultar(pergunta: str, k: int = 4) -> dict:
    pergunta = pergunta.strip()
    if not pergunta:
        raise ValueError("A consulta precisa de uma pergunta.")
    trechos = ler_corpus()
    if not trechos:
        return _registrar(pergunta, [], "A base não tem trechos.")
    indice = Indice(trechos)
    notas = indice.pontuar(pergunta)
    ordenados = sorted(zip(notas, trechos), key=lambda item: item[0], reverse=True)
    escolhidos = [
        {
            "id": trecho["id"],
            "fonte": trecho["fonte"],
            "titulo": trecho["titulo"],
            "pontuacao": round(nota, 4),
            "texto": trecho["texto"],
        }
        for nota, trecho in ordenados[:k]
        if nota > 0
    ]
    aviso = "" if escolhidos else "Nenhum trecho teve termo em comum com a pergunta."
    return _registrar(pergunta, escolhidos, aviso)


def _registrar(pergunta: str, trechos: list[dict], aviso: str) -> dict:
    CONSULTAS.mkdir(parents=True, exist_ok=True)
    carimbo = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    caminho = CONSULTAS / f"{carimbo}.json"
    resultado = {
        "pergunta": pergunta,
        "aviso": aviso,
        "trechos": trechos,
        "arquivo": caminho.relative_to(ROOT).as_posix(),
    }
    caminho.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    return resultado


def _imprimir(resultado: dict) -> None:
    print(resultado["arquivo"])
    if resultado["aviso"]:
        print(resultado["aviso"])
    if not resultado["trechos"]:
        return
    for indice, trecho in enumerate(resultado["trechos"], start=1):
        print(f"\n[{indice}] {trecho['titulo']}  {trecho['pontuacao']}")
        print(trecho["fonte"])
        print(trecho["texto"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Uso: python -m rag.consultar \"pergunta\"")
    _imprimir(consultar(" ".join(sys.argv[1:])))
