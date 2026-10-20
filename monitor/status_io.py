"""Registro verificável do andamento. O monitor só lê este arquivo."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "monitor" / "status.json"

AGENTES = (
    "orquestrador",
    "pesquisador",
    "construtor",
    "executor",
    "validador",
)

TAREFAS_INICIAIS = [
    {"id": "monitor", "title": "Monitor visual lendo registro real", "status": "pendente", "note": ""},
    {"id": "regras", "title": "Regras e sistema de checkpoint", "status": "pendente", "note": ""},
    {"id": "pesquisa", "title": "Pesquisa pública do DTX Live", "status": "pendente", "note": ""},
    {"id": "mapa", "title": "Mapa de interface só com o que foi visto", "status": "pendente", "note": ""},
    {"id": "plano", "title": "Planejamento da árvore de motores", "status": "pendente", "note": ""},
    {"id": "motores", "title": "Motores próprios de separação e retícula 20–45 LPI", "status": "pendente", "note": ""},
    {"id": "interface", "title": "Interface do editor", "status": "pendente", "note": ""},
    {"id": "dtx", "title": "Arquivo de projeto próprio .dtx", "status": "pendente", "note": ""},
    {"id": "testes", "title": "Testes automáticos dos motores e da janela", "status": "pendente", "note": ""},
    {"id": "validacao", "title": "Validação abrindo o aplicativo", "status": "pendente", "note": ""},
    {
        "id": "ai",
        "title": "AI Upscaler",
        "status": "bloqueada",
        "note": "Serviço com créditos do site original. Sem motor público para reproduzir.",
    },
    {
        "id": "gang",
        "title": "Gang Sheet Builder",
        "status": "bloqueada",
        "note": "A página descreve Auto Build, quantidade e rotação. A tela e a medida do filme não foram publicadas.",
    },
    {
        "id": "dtx-original",
        "title": "Abrir o .dtx proprietário",
        "status": "bloqueada",
        "note": "O formato interno do arquivo original não foi publicado.",
    },
    {
        "id": "lado-a-lado",
        "title": "Comparar resultado com o app original no mesmo arquivo",
        "status": "bloqueada",
        "note": "Sem acesso ao aplicativo. Falta captura ou arquivo de teste processado lá.",
    },
    {
        "id": "rag",
        "title": "RAG dos agentes para a estrutura de criação",
        "status": "pendente",
        "note": "",
    },
    {
        "id": "motor-finalidade",
        "title": "Lógica do motor alinhada à finalidade DTF têxtil",
        "status": "pendente",
        "note": "A interface atende. O resultado do motor ainda não atende.",
    },
    {
        "id": "traducao",
        "title": "Interface e navegação em português do Brasil",
        "status": "pendente",
        "note": "",
    },
]


def agora() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def vazio() -> dict:
    return {
        "updated_at": agora(),
        "project_state": "funcionando",
        "state_reason": "",
        "stage": "Preparação",
        "stage_detail": "",
        "agents": {nome: {"state": "aguardando", "activity": ""} for nome in AGENTES},
        "tasks": [dict(item) for item in TAREFAS_INICIAIS],
        "checkpoint": {"id": "", "stage": "", "at": "", "path": ""},
        "blockers": [],
    }


def carregar() -> dict:
    if not STATUS_PATH.exists():
        dados = vazio()
        gravar(dados)
        return dados
    dados = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    ids = {item.get("id") for item in dados.get("tasks", [])}
    for item in TAREFAS_INICIAIS:
        if item["id"] not in ids:
            dados["tasks"].append(dict(item))
    return dados


def gravar(dados: dict) -> None:
    dados["updated_at"] = agora()
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def atualizar(
    *,
    etapa: str | None = None,
    detalhe: str | None = None,
    estado: str | None = None,
    motivo: str | None = None,
    agentes: dict | None = None,
    tarefas: dict | None = None,
    checkpoint: dict | None = None,
    blockers: list | None = None,
) -> dict:
    dados = carregar()
    if etapa is not None:
        dados["stage"] = etapa
    if detalhe is not None:
        dados["stage_detail"] = detalhe
    if estado is not None:
        dados["project_state"] = estado
    if motivo is not None:
        dados["state_reason"] = motivo
    if agentes:
        for nome, info in agentes.items():
            dados["agents"][nome] = {
                "state": info.get("state", "aguardando"),
                "activity": info.get("activity", ""),
            }
    if tarefas:
        for item in dados["tasks"]:
            if item["id"] in tarefas:
                novo = tarefas[item["id"]]
                item["status"] = novo.get("status", item["status"])
                if "note" in novo:
                    item["note"] = novo["note"]
    if checkpoint is not None:
        dados["checkpoint"] = checkpoint
    if blockers is not None:
        dados["blockers"] = blockers
    gravar(dados)
    return dados
