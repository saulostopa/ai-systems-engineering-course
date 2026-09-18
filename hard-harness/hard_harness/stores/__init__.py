"""Stores — workflow persistence (no database in the first version).

Minimum interface (StateStore):
  read_state() -> WorkflowState | None
  write_state(state) -> None
  append_event(event) -> None
  list_events() -> list[Event]

Implementations:
  - FileStateStore  (.harness/state.json + events.jsonl + artifacts/ + locks/)
  - AgEnFKStore     (optional adapter: mirrors progress/evidence in AgEnFK)
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


from .file_store import FileStateStore
from .agenfk_store import AgEnFKStore

__all__ = ["StateStore", "FileStateStore", "AgEnFKStore"]