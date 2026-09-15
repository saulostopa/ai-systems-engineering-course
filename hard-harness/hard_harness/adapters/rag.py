"""RagContextProvider — o RAG como PROVEDOR DE CONTEXTO, nunca orquestrador.

Regras (requisito do curso):
  - O workflow pode pedir contexto ao AgentController do rag-harness;
  - o resultado chega tipado como contexto (NodeInput.context);
  - o RAG NÃO decide transições: não recebe o runner, não emite eventos de
    transição, não propõe próximo nó.

A dependência do rag-harness é opcional e injetada (caminho de import).
"""

from __future__ import annotations

import importlib
import sys
from typing import Any


class RagContextProvider:
    """Envolve o AgentController do rag-harness com um contrato mínimo."""

    def __init__(self, rag_harness_root: str, index_dir: str | None = None, embedder=None) -> None:
        self.rag_harness_root = rag_harness_root
        self.index_dir = index_dir
        self.embedder = embedder
        self._controller = None

    def _load_controller(self) -> Any:
        if self._controller is not None:
            return self._controller
        if self.rag_harness_root not in sys.path:
            sys.path.insert(0, self.rag_harness_root)
        agentic = importlib.import_module("rag_harness.agentic")
        indexer = importlib.import_module("rag_harness.indexer")
        embeddings = importlib.import_module("rag_harness.embeddings")
        embedder = self.embedder or embeddings.make_embedder()
        if self.index_dir:
            index = indexer.load_index(self.index_dir)
        else:
            raise RuntimeError("RagContextProvider exige index_dir (índice do rag_harness)")
        self._controller = agentic.AgentController(index, embedder)
        return self._controller

    # ── Contrato com o workflow ──────────────────────────────────

    def provide_context(self, question: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Retorna contexto TIPADO: [{path, start_line, text, kind, name}].

        É uma função de leitura pura — nunca altera estado do workflow.
        """
        controller = self._load_controller()
        chunks = controller.retrieve(question, self.rag_harness_root)
        return [
            {
                "path": c.path,
                "start_line": c.start_line,
                "end_line": c.end_line,
                "kind": c.kind,
                "name": c.name,
                "text": c.text[:600],
            }
            for c in chunks[:top_k]
        ]

    # ── Nó determinístico opcional ───────────────────────────────

    def as_node(self):
        """Cria um nó determinístico 'context' que injeta o contexto no payload
        do workflow (NodeInput.context). O RAG nunca propõe próximo nó."""

        def context_node(ninput) -> Any:
            from hard_harness.core.schemas import NodeOutput

            question = ninput.payload.get("question") or str(ninput.payload)
            context = self.provide_context(question)
            return NodeOutput(node_id="context", ok=True, payload={"context": context})

        return context_node