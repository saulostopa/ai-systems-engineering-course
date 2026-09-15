"""Base — interface StateStore (Protocol) e helpers de lock.

Contrato mínimo de persistência. Novas implementações (SQLite, AgEnFK,
Redis) implementam o mesmo Protocol — o runner não sabe onde o estado vive.
"""

from __future__ import annotations

from typing import Protocol

from hard_harness.core.events import Event
from hard_harness.core.schemas import WorkflowState


class StateStore(Protocol):
    def read_state(self) -> WorkflowState | None: ...
    def write_state(self, state: WorkflowState) -> None: ...
    def append_event(self, event: Event) -> None: ...
    def list_events(self) -> list[Event]: ...