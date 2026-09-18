"""AgEnFKStore — optional adapter for AgEnFK.

When AgEnFK is available (linked project + accessible CLI), it is the source
of truth for item progress and evidence — the runner does NOT duplicate this:
  - read_state: reads the item/status from AgEnFK (when the workflow maps an item);
  - append_event: records events as auditable comments;
  - write_state: records status progress via `agenfk verify` (evidence) —
    the runner remains the flow authority; AgEnFK is the management system
    behind it (consistent with EPIC B2).

If AgEnFK is unavailable, we do NOT work around it: the store raises an
explicit error (the caller decides between a FileStateStore fallback or stopping).
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
            raise AgEnFKUnavailableError(f"AgEnFK unavailable: {exc}") from exc
        if proc.returncode != 0:
            raise AgEnFKUnavailableError(f"AgEnFK error ({proc.returncode}): {proc.stderr[-500:]}")
        return proc.stdout

    def check_available(self) -> bool:
        try:
            self._run("get", self.item_id, "--json")
            return True
        except AgEnFKUnavailableError:
            return False

    # ── State ───────────────────────────────────────────────────

    def read_state(self) -> WorkflowState | None:
        """Reads the item from AgEnFK and projects it into a WorkflowState (if any)."""
        out = self._run("get", self.item_id, "--json")
        try:
            item = json.loads(out)
        except json.JSONDecodeError as exc:
            raise AgEnFKUnavailableError(f"invalid response: {exc}") from exc
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
        """Records progress in AgEnFK (evidence via verify). NEVER duplicates the
        runner's state as a second source of truth — AgEnFK manages it."""
        if state.status is WorkflowStatus.PASSED:
            self._run("verify", self.item_id, "--evidence", "workflow completed by the hard harness")
        elif state.status is WorkflowStatus.BLOCKED:
            self._run("comment", self.item_id, f"[hard-harness] blocked: {state.error[:200]}")

    # ── Events ──────────────────────────────────────────────────

    def append_event(self, event: Event) -> None:
        """Mirrors critical events as comments (auditability)."""
        if event.kind in ("gate", "error", "close"):
            self._run("comment", self.item_id, f"[hard-harness:{event.kind}] {event.message[:300]}")

    def list_events(self) -> list[Event]:
        raise NotImplementedError("AgEnFK events are read via telemetry/comments")

    def record_evidence(self, command: str, output: str, status: str) -> None:
        """Records test/evidence in AgEnFK (existing mechanism)."""
        self._run("log-test", self.item_id, "--command", command, "--output", output[:500], "--status", status)