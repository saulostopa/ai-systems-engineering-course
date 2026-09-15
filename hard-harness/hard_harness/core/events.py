"""Eventos do workflow — trilha de auditoria.

Toda transição, gate, erro e proposta de agente vira um Event. Eventos são
persistidos (events.jsonl) e propagados a listeners. Nenhuma transição
acontece em silêncio (requisito do curso).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .schemas import new_id, now_iso


@dataclass
class Event:
    kind: str  # transition | gate | agent_proposal | evidence | error | note | close
    node_id: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: new_id("evt"))
    ts: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "ts": self.ts, "kind": self.kind, "node_id": self.node_id, "message": self.message, "data": self.data}


class EventBus:
    def __init__(self) -> None:
        self._listeners: list[Callable[[Event], None]] = []

    def subscribe(self, listener: Callable[[Event], None]) -> None:
        self._listeners.append(listener)

    def emit(self, event: Event) -> None:
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                pass  # listener de auditoria nunca derruba o workflow