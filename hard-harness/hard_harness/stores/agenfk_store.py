"""AgEnFKStore — adapter opcional para o AgEnFK.

Quando o AgEnFK está disponível (projeto vinculado + CLI acessível), ele é a
fonte de verdade do avanço de itens e evidências — o runner NÃO duplica isso:
  - read_state: lê o item/status do AgEnFK (quando o workflow mapeia um item);
  - append_event: registra eventos como comentários auditáveis;
  - write_state: registra avanço de status via `agenfk verify` (evidência) —
    o runner continua sendo a autoridade do fluxo; o AgEnFK é o sistema de
    gestão por trás (consistente com o EPIC B2).

Se o AgEnFK estiver indisponível, NÃO contornamos: o store levanta erro
explícito (o chamador decide entre FileStateStore fallback ou parar).
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

from hard_harness.core.events import Event
from hard_harness.core.schemas import WorkflowState, WorkflowStatus

from .base import StateStore

CLI = "/home/svslwm/wm/agenfk/agenfk"


class AgEnFKUnavailableError(RuntimeError):
    pass


class AgEnFKStore(StateStore):
    def __init__(self, item_id: str, cli: str = CLI, project_root: str | None = None) -> None:
        self.item_id = item_id
        self.cli = cli
        self.project_root = project_root or os.getcwd()

    # ── CLI helpers ──────────────────────────────────────────────

    def _run(self, *args: str) -> str:
        cmd = [self.cli, *args]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=self.project_root)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise AgEnFKUnavailableError(f"AgEnFK indisponível: {exc}") from exc
        if proc.returncode != 0:
            raise AgEnFKUnavailableError(f"AgEnFK erro ({proc.returncode}): {proc.stderr[-500:]}")
        return proc.stdout

    def check_available(self) -> bool:
        try:
            self._run("get", self.item_id, "--json")
            return True
        except AgEnFKUnavailableError:
            return False

    # ── Estado ───────────────────────────────────────────────────

    def read_state(self) -> WorkflowState | None:
        """Lê o item do AgEnFK e o projeta num WorkflowState (se houver)."""
        out = self._run("get", self.item_id, "--json")
        try:
            item = json.loads(out)
        except json.JSONDecodeError as exc:
            raise AgEnFKUnavailableError(f"resposta inválida: {exc}") from exc
        status = str(item.get("status", "TODO")).upper()
        wf_status = {
            "TODO": WorkflowStatus.PENDING,
            "IN_PROGRESS": WorkflowStatus.RUNNING,
            "REVIEW": WorkflowStatus.RUNNING,
            "TEST": WorkflowStatus.RUNNING,
            "DONE": WorkflowStatus.PASSED,
            "BLOCKED": WorkflowStatus.BLOCKED,
        }.get(status, WorkflowStatus.PENDING)
        return WorkflowState(
            workflow_id=f"agenfk_{self.item_id[:8]}",
            status=wf_status,
            data={"item_id": self.item_id, "title": item.get("title", ""), "agenfk_status": status},
        )

    def write_state(self, state: WorkflowState) -> None:
        """Registra avanço no AgEnFK (evidência via verify). NUNCA duplica o
        estado do runner como segunda fonte de verdade — o AgEnFK gerencia."""
        if state.status is WorkflowStatus.PASSED:
            self._run("verify", self.item_id, "--evidence", "workflow concluído pelo hard harness")
        elif state.status is WorkflowStatus.BLOCKED:
            self._run("comment", self.item_id, f"[hard-harness] bloqueado: {state.error[:200]}")

    # ── Eventos ──────────────────────────────────────────────────

    def append_event(self, event: Event) -> None:
        """Espelha eventos críticos como comentários (auditabilidade)."""
        if event.kind in ("gate", "error", "close"):
            self._run("comment", self.item_id, f"[hard-harness:{event.kind}] {event.message[:300]}")

    def list_events(self) -> list[Event]:
        raise NotImplementedError("eventos do AgEnFK são lidos via telemetria/comentários")

    def record_evidence(self, command: str, output: str, status: str) -> None:
        """Registra teste/evidência no AgEnFK (mecânica existente)."""
        self._run("log-test", self.item_id, "--command", command, "--output", output[:500], "--status", status)