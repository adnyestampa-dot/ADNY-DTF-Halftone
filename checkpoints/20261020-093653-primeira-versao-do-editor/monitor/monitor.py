"""Pop-up de andamento. Lê monitor/status.json e não inventa atividade."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "monitor" / "status.json"
PID_PATH = ROOT / "monitor" / "monitor.pid"
STOP_PATH = ROOT / "monitor" / "STOP"
INTERVALO_MS = 15 * 60 * 1000
LIMITE_SEM_CONFIRMACAO_S = 20 * 60


def processo_vivo(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def assumir_instancia() -> bool:
    if PID_PATH.exists():
        try:
            pid = int(PID_PATH.read_text(encoding="utf-8").strip())
        except ValueError:
            pid = -1
        if processo_vivo(pid):
            return False
    PID_PATH.write_text(str(os.getpid()), encoding="utf-8")
    return True


def cursor_aberto() -> bool | None:
    try:
        resultado = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Cursor.exe", "/NH"],
            capture_output=True,
            text=True,
            timeout=8,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return "Cursor.exe" in (resultado.stdout or "")


def ler_status() -> tuple[dict | None, str | None]:
    if not STATUS_PATH.exists():
        return None, "Arquivo monitor/status.json ausente."
    try:
        dados = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"Registro ilegível: {exc}."
    if not isinstance(dados, dict) or "tasks" not in dados or "agents" not in dados:
        return None, "Registro sem tarefas ou sem agentes."
    return dados, None


def idade_segundos(dados: dict) -> float | None:
    texto = dados.get("updated_at")
    if not texto:
        return None
    try:
        momento = datetime.fromisoformat(texto)
    except ValueError:
        return None
    if momento.tzinfo is None:
        momento = momento.astimezone()
    return (datetime.now().astimezone() - momento).total_seconds()


def avaliar(dados: dict | None, erro: str | None) -> tuple[str, str]:
    if erro or dados is None:
        return "parado", erro or "Sem registro."
    idade = idade_segundos(dados)
    if idade is None:
        return "parado", "O registro não tem horário confiável."
    estado = dados.get("project_state")
    if estado == "funcionando" and idade > LIMITE_SEM_CONFIRMACAO_S:
        return "parado", "Sem confirmação de execução há mais de 20 minutos."
    if estado != "funcionando":
        return "parado", dados.get("state_reason") or "Projeto parado."
    if dados.get("blockers"):
        return "parado", "Há bloqueio registrado na cadeia."
    ativos = [
        nome
        for nome, info in dados.get("agents", {}).items()
        if isinstance(info, dict) and info.get("state") == "ativo"
    ]
    if not ativos:
        return "parado", "Nenhum agente marcado como ativo no registro."
    for nome in ativos:
        if not str(dados["agents"][nome].get("activity") or "").strip():
            return "parado", f"O agente {nome} está ativo sem atividade descrita."
    return "funcionando", ""


def porcentagem(tarefas: list) -> tuple[str, int, int]:
    if not tarefas:
        return "sem tarefas registradas", 0, 0
    feitas = sum(1 for item in tarefas if item.get("status") == "concluida")
    total = len(tarefas)
    return f"{feitas / total * 100:.1f}% ({feitas} de {total})", feitas, total


class Monitor:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw()
        self.janela: tk.Toplevel | None = None
        self.posicao: tuple[int, int] | None = None
        self.largura = 0
        self.altura = 0
        self.depois_id: str | None = None
        self.falhas_cursor = 0
        self.abrir()
        self.agendar()
        self.root.after(5000, self.vigiar)
        self.root.mainloop()

    def geometria_tela(self) -> tuple[int, int, int, int]:
        self.root.update_idletasks()
        largura = self.root.winfo_screenwidth()
        altura = self.root.winfo_screenheight()
        janela_w = max(520, largura // 2)
        janela_h = max(420, altura // 2)
        x = (largura - janela_w) // 2
        y = (altura - janela_h) // 2
        return janela_w, janela_h, x, y

    def guardar_posicao(self) -> None:
        if self.janela is None or not self.janela.winfo_exists():
            return
        self.posicao = (self.janela.winfo_x(), self.janela.winfo_y())
        self.largura = self.janela.winfo_width()
        self.altura = self.janela.winfo_height()

    def abrir(self) -> None:
        self.guardar_posicao()
        if self.janela is not None and self.janela.winfo_exists():
            self.janela.destroy()
        dados, erro = ler_status()
        nivel, motivo = avaliar(dados, erro)
        janela = tk.Toplevel(self.root)
        self.janela = janela
        janela.title("Andamento do projeto")
        janela.configure(bg="#f4f5f7")
        if self.posicao and self.largura and self.altura:
            janela.geometry(f"{self.largura}x{self.altura}+{self.posicao[0]}+{self.posicao[1]}")
        else:
            largura, altura, x, y = self.geometria_tela()
            self.largura, self.altura = largura, altura
            self.posicao = (x, y)
            janela.geometry(f"{largura}x{altura}+{x}+{y}")
        janela.protocol("WM_DELETE_WINDOW", self.fechar_aviso)
        faixa = tk.Frame(janela, bg="#146c36" if nivel == "funcionando" else "#8f1d1d")
        faixa.pack(fill="x")
        titulo = (
            "VERDE — PROJETO EM ANDAMENTO"
            if nivel == "funcionando"
            else "VERMELHO — PROJETO PARADO OU BLOQUEADO"
        )
        tk.Label(
            faixa,
            text=titulo,
            bg=faixa["bg"],
            fg="white",
            font=("Segoe UI", 16, "bold"),
            pady=14,
        ).pack(fill="x")
        if motivo:
            tk.Label(
                faixa,
                text=motivo,
                bg=faixa["bg"],
                fg="white",
                font=("Segoe UI", 10),
                wraplength=700,
                pady=4,
            ).pack(fill="x")
        texto = tk.Text(
            janela,
            wrap="word",
            bg="#f4f5f7",
            fg="#1c1c1c",
            font=("Segoe UI", 11),
            relief="flat",
            padx=18,
            pady=12,
        )
        barra = tk.Scrollbar(janela, command=texto.yview)
        texto.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        texto.pack(side="left", fill="both", expand=True)
        texto.tag_configure("secao", font=("Segoe UI", 12, "bold"), spacing1=10, spacing3=4)
        texto.insert("end", self.montar_texto(dados, erro, nivel))
        texto.configure(state="disabled")
        janela.attributes("-topmost", True)
        janela.after(1200, lambda: janela.attributes("-topmost", False))
        janela.bind("<Configure>", lambda _evento: self.guardar_posicao())

    def montar_texto(self, dados: dict | None, erro: str | None, nivel: str) -> str:
        if dados is None:
            return (
                "Estado geral\n"
                "Parado. Não há registro confiável.\n\n"
                "Agentes\n"
                "Não confirmados.\n\n"
                "Etapa\n"
                "Desconhecida.\n\n"
                "Conclusão da primeira versão\n"
                "Sem tarefas registradas. Porcentagem não calculada.\n\n"
                "Tarefas concluídas\n"
                "Nenhuma informação.\n\n"
                "Tarefas restantes\n"
                "Nenhuma informação.\n\n"
                "Último checkpoint\n"
                "Não informado.\n\n"
                "Problemas\n"
                f"{erro}\n\n"
                "O monitor não assume que a cadeia está funcionando.\n"
                "Próxima atualização em 15 minutos.\n"
            )
        tarefas = dados.get("tasks") or []
        percentual, _feitas, _total = porcentagem(tarefas)
        concluidas = [item["title"] for item in tarefas if item.get("status") == "concluida"]
        restantes = [
            f"{item['title']} — {item.get('status')}"
            + (f" ({item.get('note')})" if item.get("note") else "")
            for item in tarefas
            if item.get("status") != "concluida"
        ]
        agentes = []
        for nome, info in (dados.get("agents") or {}).items():
            estado = info.get("state", "sem estado")
            atividade = info.get("activity") or "sem atividade registrada"
            agentes.append(f"{nome}: {estado}. {atividade}")
        checkpoint = dados.get("checkpoint") or {}
        if checkpoint.get("id"):
            texto_checkpoint = (
                f"{checkpoint.get('id')} | etapa {checkpoint.get('stage') or 'não informada'}"
                f" | {checkpoint.get('at') or 'sem horário'}"
                f" | {checkpoint.get('path') or ''}"
            )
        else:
            texto_checkpoint = "Nenhum checkpoint gravado ainda."
        problemas = list(dados.get("blockers") or [])
        problemas.extend(
            f"{item['title']}: {item.get('note') or item.get('status')}"
            for item in tarefas
            if item.get("status") == "bloqueada"
        )
        if nivel != "funcionando" and dados.get("state_reason"):
            problemas.insert(0, dados["state_reason"])
        if not problemas:
            problemas = ["Nenhum bloqueio registrado neste arquivo."]
        return (
            "Estado geral\n"
            f"{'Funcionando' if nivel == 'funcionando' else 'Parado'}.\n"
            f"Registro: {dados.get('updated_at', 'sem horário')}\n\n"
            "Agentes\n"
            + "\n".join(agentes)
            + "\n\nEtapa\n"
            f"{dados.get('stage', 'não informada')}. {dados.get('stage_detail', '')}\n\n"
            "Conclusão da primeira versão\n"
            f"{percentual}. Conta tarefas concluídas sobre as tarefas planejadas no registro.\n\n"
            "Tarefas concluídas\n"
            + ("\n".join(concluidas) if concluidas else "Nenhuma concluída no registro.")
            + "\n\nTarefas restantes\n"
            + ("\n".join(restantes) if restantes else "Nenhuma restante no registro.")
            + "\n\nÚltimo checkpoint\n"
            f"{texto_checkpoint}\n"
            f"Etapa salva: {checkpoint.get('stage') or 'nenhuma'}\n\n"
            "Problemas ou bloqueios\n"
            + "\n".join(problemas)
            + "\n\nPróxima atualização em 15 minutos. A janela anterior é substituída.\n"
            "Fonte: monitor/status.json\n"
        )

    def fechar_aviso(self) -> None:
        self.guardar_posicao()
        if self.janela is not None and self.janela.winfo_exists():
            self.janela.destroy()
        self.janela = None

    def agendar(self) -> None:
        if self.depois_id is not None:
            self.root.after_cancel(self.depois_id)
        self.depois_id = self.root.after(INTERVALO_MS, self.atualizar)

    def atualizar(self) -> None:
        self.abrir()
        self.agendar()

    def encerrar(self) -> None:
        self.guardar_posicao()
        if self.janela is not None and self.janela.winfo_exists():
            self.janela.destroy()
        if PID_PATH.exists():
            try:
                if int(PID_PATH.read_text(encoding="utf-8").strip()) == os.getpid():
                    PID_PATH.unlink()
            except (ValueError, OSError):
                pass
        self.root.quit()

    def vigiar(self) -> None:
        if STOP_PATH.exists():
            self.encerrar()
            return
        estado = cursor_aberto()
        if estado is True:
            self.falhas_cursor = 0
        elif estado is False:
            self.falhas_cursor += 1
            if self.falhas_cursor >= 2:
                self.encerrar()
                return
        self.root.after(5000, self.vigiar)


def main() -> None:
    if not assumir_instancia():
        return
    try:
        Monitor()
    finally:
        if PID_PATH.exists():
            try:
                if int(PID_PATH.read_text(encoding="utf-8").strip()) == os.getpid():
                    PID_PATH.unlink()
            except (ValueError, OSError):
                pass


if __name__ == "__main__":
    main()
