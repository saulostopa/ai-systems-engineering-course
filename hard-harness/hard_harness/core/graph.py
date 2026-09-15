"""Grafo executável — a estrutura do workflow (ADK 2, Pillar 1).

- Nós determinísticos (função pura) e agênticos (raciocínio) são peers.
- fan-out: arestas de um nó para vários (execução paralela no runner).
- join: nó que agrega N entradas (JoinNode).
- router: função que escolhe UMA rota — SEMPRE com default obrigatório
  (rota inexistente nunca encerra em silêncio — lição ADK L2b).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .schemas import NodeKind, NodeOutput

NodeFn = Callable[["NodeInput"], NodeOutput]
RouterFn = Callable[[dict[str, Any]], str]


@dataclass
class Node:
    id: str
    kind: NodeKind
    fn: NodeFn
    description: str = ""
    max_retries: int = 1  # tentativas adicionais além da primeira
    timeout_s: float = 0.0  # 0 = sem timeout individual


@dataclass
class WorkflowGraph:
    """Grafo: nós + arestas + fan-outs + joins + routers.

    Convenções:
      - edge(n, m): n -> m (sequencial).
      - fan_out(n, [m1, m2, ...]): n dispara N em paralelo.
      - join(n, [s1, s2], m): m recebe payload {s1: {...}, s2: {...}}.
      - router(n, fn, routes, default): fn(payload) -> id em routes; default OBRIGATÓRIO.
    """

    name: str
    nodes: dict[str, Node] = field(default_factory=dict)
    start: str = ""
    edges: dict[str, list[str]] = field(default_factory=dict)  # n -> sucessores
    joins: dict[str, list[str]] = field(default_factory=dict)  # n -> fontes
    routers: dict[str, tuple[RouterFn, dict[str, str], str]] = field(default_factory=dict)
    is_join: set[str] = field(default_factory=set)

    def add_node(self, node: Node) -> "WorkflowGraph":
        if node.id in self.nodes:
            raise ValueError(f"nó duplicado: {node.id}")
        self.nodes[node.id] = node
        self.edges.setdefault(node.id, [])
        return self

    def set_start(self, node_id: str) -> "WorkflowGraph":
        if node_id not in self.nodes:
            raise ValueError(f"start desconhecido: {node_id}")
        self.start = node_id
        return self

    def edge(self, src: str, dst: str) -> "WorkflowGraph":
        self._require(src, dst)
        if dst in self.edges[src]:
            return self
        self.edges[src].append(dst)
        return self

    def fan_out(self, src: str, targets: list[str]) -> "WorkflowGraph":
        for t in targets:
            self.edge(src, t)
        return self

    def join(self, node_id: str, sources: list[str], target: str) -> "WorkflowGraph":
        """JoinNode: aguarda todas as fontes e entrega {source_id: payload}."""
        self._require(node_id, target)
        self.is_join.add(node_id)
        self.joins[node_id] = sources
        for s in sources:
            self._require(s, node_id)
            self.edge(s, node_id)
        self.edge(node_id, target)
        return self

    def router(self, node_id: str, fn: RouterFn, routes: dict[str, str], default: str) -> "WorkflowGraph":
        """Router determinístico — default OBRIGATÓRIO (sem morte silenciosa)."""
        if default not in routes.values():
            raise ValueError(f"router {node_id}: default '{default}' deve ser um destino existente em routes")
        for dst in routes.values():
            self._require(node_id, dst)
            self.edge(node_id, dst)  # rotas também são arestas (visíveis e auditáveis)
        self.routers[node_id] = (fn, routes, default)
        return self

    def _require(self, src: str, dst: str) -> None:
        for n in (src, dst):
            if n not in self.nodes:
                raise ValueError(f"nó desconhecido: {n}")

    def validate(self) -> list[str]:
        """Validação estrutural: nós referenciados existem; routers têm default;
        todo nó é alcançável; nenhum dead-end silencioso em rotas de router."""
        problems: list[str] = []
        if not self.start:
            problems.append("sem nó start")
        for node_id, (_, routes, default) in self.routers.items():
            for route, dst in routes.items():
                if dst not in self.nodes:
                    problems.append(f"router {node_id}: rota '{route}' -> nó inexistente '{dst}'")
            if default not in self.nodes:
                problems.append(f"router {node_id}: default -> nó inexistente '{default}'")
            if default not in routes.values():
                problems.append(f"router {node_id}: default '{default}' fora das rotas")
        reachable: set[str] = set()
        frontier = [self.start] if self.start else []
        while frontier:
            n = frontier.pop(0)
            if n in reachable:
                continue
            reachable.add(n)
            for dst in self.edges.get(n, []):
                if dst not in self.nodes:
                    problems.append(f"aresta {n} -> nó inexistente '{dst}'")
                else:
                    frontier.append(dst)
        for nid in self.nodes:
            if nid not in reachable:
                problems.append(f"nó inalcançável: {nid}")
        return problems