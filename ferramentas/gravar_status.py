import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from monitor.status_io import atualizar

atualizar(
    etapa="Tom pela pesquisa pública",
    detalhe=(
        "A pesquisa está em rag/base/pesquisa-publica-reticula.md. "
        "Cor opaca e viva fica contínua. Alfa parcial e cinza em rampa viram ponto. "
        "13 testes de motor passaram. Degradê opaco entre cores vivas permanece contínuo, como na fonte DTF pública. "
        "A suavização da janela continua só no plano."
    ),
    estado="funcionando",
    motivo="",
    agentes={
        "orquestrador": {
            "state": "aguardando",
            "activity": "Método público escolhido e aplicado no motor de tom. A suavização da janela ainda não começou.",
        },
        "pesquisador": {
            "state": "aguardando",
            "activity": "Pesquisa DTF registrada. A fórmula do aplicativo de referência continua sem publicação.",
        },
        "construtor": {
            "state": "aguardando",
            "activity": "Motor de tom separado da presença. A interface não foi redesenhada.",
        },
        "executor": {
            "state": "aguardando",
            "activity": "Tom novo no motor central. Editor reaberto com esse código.",
        },
        "validador": {
            "state": "aguardando",
            "activity": "13 testes de motor passaram no chapado, na fumaça parcial e no cinza em rampa.",
        },
    },
    tarefas={
        "motores": {
            "status": "concluida",
            "note": "Presença, tom, retícula 20–45, base e PNG. Prova automática, sem comparação com o aplicativo original.",
        },
        "motor-finalidade": {
            "status": "concluida",
            "note": "Chapado vivo contínuo. Alfa parcial e cinza em rampa viram ponto. Degradê vivo opaco fica contínuo.",
        },
        "traducao": {
            "status": "concluida",
            "note": "Rótulos, menus, vistas, diálogos e avisos no vocabulário de serigrafia e DTF.",
        },
    },
    checkpoint={
        "id": "20261020-150011-antes-do-tom-pela-pesquisa-publica",
        "stage": "Antes do tom pela pesquisa publica",
        "at": "2026-10-20T15:00:11-03:00",
        "path": "checkpoints/20261020-150011-antes-do-tom-pela-pesquisa-publica",
    },
)
print("ok")
