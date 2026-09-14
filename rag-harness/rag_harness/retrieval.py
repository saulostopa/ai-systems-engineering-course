"""Recuperação híbrida: léxica (BM25-ish) + semântica (vetores), fundidas
por Reciprocal Rank Fusion (RRF). rag-harness.md: 'lexical matches (nomes de
símbolos exatos) e semantic matches (similaridade conceitual) numa lista só'.
"""

from __future__ import annotations

import math
import re
from collections import Counter

from .chunker import Chunk
from .indexer import Index, semantic_search


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())


def _idf(index: Index) -> dict[str, float]:
    n = max(1, len(index.chunks))
    df: Counter[str] = Counter()
    for c in index.chunks:
        df.update(set(tokenize(c.text)))
    return {term: math.log(1 + n / (1 + df[term])) for term in df}


def lexical_search(index: Index, query: str, top_k: int = 5, idf: dict[str, float] | None = None) -> list[tuple[Chunk, float]]:
    idf = idf or _idf(index)
    qterms = tokenize(query)
    if not qterms:
        return []
    scored: list[tuple[Chunk, float]] = []
    for c in index.chunks:
        terms = Counter(tokenize(c.text))
        score = 0.0
        for t in qterms:
            if t in terms:
                score += idf.get(t, 1.0) * (1 + math.log(1 + terms[t]))
        if score > 0:
            scored.append((c, score))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_k]


def rrf_merge(
    *ranked_lists: list[tuple[Chunk, float]], k: int = 60, top_k: int = 5
) -> list[tuple[Chunk, float]]:
    """Reciprocal Rank Fusion: soma 1/(k+rank) por lista."""
    scores: dict[str, float] = {}
    chunks_by_hash: dict[str, Chunk] = {}
    for ranked in ranked_lists:
        for rank, (chunk, _score) in enumerate(ranked, start=1):
            scores[chunk.hash] = scores.get(chunk.hash, 0.0) + 1.0 / (k + rank)
            chunks_by_hash[chunk.hash] = chunk
    merged = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
    return [(chunks_by_hash[h], s) for h, s in merged[:top_k]]


def hybrid_search(
    index: Index, embedder, query: str, top_k: int = 5, idf: dict[str, float] | None = None
) -> list[tuple[Chunk, float]]:
    lex = lexical_search(index, query, top_k=top_k * 2, idf=idf)
    vec = semantic_search(index, embedder, query, top_k=top_k * 2)
    return rrf_merge(lex, vec, top_k=top_k)