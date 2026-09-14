"""Controlador agêntico de recuperação (rag-harness.md: Agent Controller).

O agente decide QUAL ferramenta usar (semântica / léxica / glob / regex),
executa, avalia se o resultado é suficiente e repete — em vez de despejar
tudo no prompt. Estratégia de custo: barato primeiro (glob/regex/léxico),
semântica por último. Gancho opcional para decisão via LLM.
"""

from __future__ import annotations

import fnmatch
import os
import re

from .chunker import Chunk
from .embeddings import cosine
from .indexer import Index
from .retrieval import hybrid_search, lexical_search, semantic_search


class AgentController:
    def __init__(self, index: Index, embedder, max_iters: int = 3) -> None:
        self.index = index
        self.embedder = embedder
        self.max_iters = max_iters
        self.used_tools: list[str] = []

    # ── Ferramentas ──────────────────────────────────────────────

    def tool_semantic_search(self, query: str, top_k: int = 3) -> list[Chunk]:
        self.used_tools.append("semantic_search")
        return [c for c, _s in semantic_search(self.index, self.embedder, query, top_k)]

    def tool_full_text_search(self, query: str, top_k: int = 3) -> list[Chunk]:
        self.used_tools.append("full_text_search")
        return [c for c, _s in lexical_search(self.index, query, top_k)]

    def tool_glob_search(self, pattern: str, root: str, top_k: int = 8) -> list[Chunk]:
        self.used_tools.append("glob_path_search")
        hits = [c for c in self.index.chunks if fnmatch.fnmatch(c.path, pattern)]
        return hits[:top_k]

    def tool_regex_search(self, pattern: str, top_k: int = 8) -> list[Chunk]:
        self.used_tools.append("regex_search")
        rx = re.compile(pattern, re.IGNORECASE)
        hits = [c for c in self.index.chunks if rx.search(c.text)]
        return hits[:top_k]

    @staticmethod
    def _exact_symbol_patterns(query: str) -> list[str]:
        """Extrai padrões de símbolo exato: quoted ('foo'), CamelCase, snake_case
        com ponto (models.Veiculo), nomes de método (registerItem)."""
        patterns: list[str] = []
        for m in re.findall(r'"([a-zA-Z_][\w.]*)"', query):
            patterns.append(re.escape(m))
        for m in re.findall(r"\b[A-Z][a-zA-Z0-9]*(?:\.[A-Z][a-zA-Z0-9]*)+", query):
            patterns.append(re.escape(m))
        for m in re.findall(r"\b[a-z]+_[a-z0-9_]+", query):
            patterns.append(re.escape(m))
        return patterns[:3]

    # ── Heurística de suficiência ────────────────────────────────

    def _sufficient(self, query: str, chunks: list[Chunk]) -> bool:
        """O top resultado contém pelo menos um termo chave da consulta?"""
        key = [t for t in re.findall(r"[a-z0-9_]{4,}", query.lower())]
        if not key:
            return True
        for c in chunks:
            text = c.text.lower()
            if any(t in text for t in key):
                return True
        return False

    # ── Loop agêntico ────────────────────────────────────────────

    def retrieve(self, query: str, root: str) -> list[Chunk]:
        """Barato primeiro; escala se insuficiente (máx. max_iters)."""
        self.used_tools = []
        gathered: list[Chunk] = []

        # Iter 1: léxico (exato) — nomes de símbolos são o alvo mais comum
        hits = self.tool_full_text_search(query, 3)
        gathered.extend(hits)
        if self._sufficient(query, hits):
            return gathered[:5]

        # Iter 2: glob por nome de arquivo (símbolo provável em arquivo homônimo)
        words = re.findall(r"[a-z0-9_]{4,}", query.lower())
        if words:
            globs = [f"**/*{words[0]}*" for words in [words[:1]]]
            for pat in globs:
                g = self.tool_glob_search(pat, root, 5)
                gathered.extend(g)
                if self._sufficient(query, gathered):
                    return gathered[:5]

        # Iter 2.5: regex para símbolos exatos (quoted ou CamelCase/snake_case
        # com ponto, ex.: 'registerItem', 'models.Veiculo', "exato")
        exact = AgentController._exact_symbol_patterns(query)
        for pat in exact:
            rx = self.tool_regex_search(pat, 5)
            gathered.extend(rx)
            if self._sufficient(query, gathered):
                return gathered[:5]

        # Iter 3: semântica (conceito) — a mais cara, por último
        sem = self.tool_semantic_search(query, 5)
        gathered.extend(sem)
        return gathered[:5]

    # ── Decisão por LLM (opcional) ───────────────────────────────

    def decide_with_llm(self, query: str, context: list[Chunk]) -> str:
        """Ponto de extensão: chame um LLM para escolher a próxima ferramenta.

        Retorna o nome da ferramenta ('semantic_search', 'regex_search', ...)
        ou 'done'. Sem LLM conectado, a heurística da Aula 11 assume.
        """
        return "done"


def pretty(chunks: list[Chunk] | list[tuple[Chunk, float]]) -> str:
    lines = []
    for i, entry in enumerate(chunks, 1):
        c = entry[0] if isinstance(entry, tuple) else entry
        preview = c.text[:160].replace("\n", " ")
        lines.append(f"  [{i}] {c.path}:{c.start_line} ({c.kind} {c.name})")
        lines.append(f"      {preview}...")
    return "\n".join(lines)