"""Adapter ADK 2 (opcional) — inspiração, não dependência do core.

O núcleo do hard-harness é framework-agnóstico. Este módulo só existe para:
  1. Documentar o mapeamento conceitual ADK 2 -> hard-harness;
  2. Exportar a estrutura do grafo num formato que o ADK entenda (edges),
     quando o google.adk estiver instalado (import opcional).

Se o ADK não estiver instalado, nada quebra — a orquestração é nossa.
"""

from __future__ import annotations

from typing import Any

from hard_harness.core.graph import WorkflowGraph


def to_adk_edges(graph: WorkflowGraph) -> list[tuple[str, str]]:
    """Projeta o grafo em arestas estilo ADK Workflow(edges=[...]).

    Routers viram pares (router_node, {route: node}) — ver exemplo L2b do
    codelab ADK 2. Serve para inspeção e para adaptadores futuros.
    """
    edges: list[tuple[str, str]] = []
    for src, dsts in graph.edges.items():
        for dst in dsts:
            edges.append((src, dst))
    return edges


def adk_available() -> bool:
    try:
        import google.adk  # noqa: F401

        return True
    except ImportError:
        return False


def mapping_table() -> dict[str, str]:
    """ADK 2 (codelab) -> hard-harness (componente)."""
    return {
        "START": "graph.start",
        "function node": "Node(kind=DETERMINISTIC)",
        "agent node": "Node(kind=AGENT)",
        "fan-out (arestas múltiplas)": "WorkflowGraph.fan_out",
        "JoinNode": "WorkflowGraph.join (agrega por id de fonte)",
        "router + DEFAULT_ROUTE": "WorkflowGraph.router (default OBRIGATÓRIO)",
        "input_schema/output_schema": "NodeInput/NodeOutput tipados (schemas.py)",
        "Event(output, route)": "NodeOutput(payload, proposed_next) + runner decide",
        "mode=chat/task/single_turn": "agentes são nós com contrato único (run(NodeInput) -> NodeOutput)",
        "MAX_DEPTH em código (L4b)": "Limits.max_depth aplicado no Runner",
        "parallel_worker runtime": "run_fanout com MAX_CHILDREN no Runner",
    }