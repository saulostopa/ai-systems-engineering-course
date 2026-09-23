"""Pluggable embeddings — n-gram hashing (local fallback) or Ollama.

No external model needed for the POC: the fallback generates deterministic
n-gram embeddings (works offline). If `OLLAMA_API_URL` is set, uses Ollama
(e.g. nomic-embed-text) when reachable.
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.request

DIM = 256
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")


class NGramEmbedder:
    """Deterministic local embedding: n-gram hash into a DIM-sized vector.

    Not truly semantic — meant to validate the *architecture* (pipeline,
    cache, RRF) without an external model. Swap for Ollama/API to get real
    semantics.
    """

    def __init__(self, dim: int = DIM) -> None:
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        tokens = "".join(c if c.isalnum() else " " for c in text.lower()).split()
        grams: list[str] = []
        for tok in tokens:
            grams.append(tok)
            if len(tok) >= 3:
                grams.append(tok[:3])
                grams.append(tok[-3:])
        for g in grams:
            idx = int(hashlib.md5(g.encode("utf-8")).hexdigest()[:8], 16) % self.dim
            vec[idx] += 1.0
        norm = sum(v * v for v in vec) ** 0.5
        if norm:
            vec = [v / norm for v in vec]
        return vec


class OllamaEmbedder:
    def __init__(self, api_url: str = OLLAMA_API_URL, model: str = OLLAMA_MODEL) -> None:
        self.api_url = api_url.rstrip("/")
        self.model = model

    def _available(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.api_url}/api/tags", timeout=2) as res:
                return res.status == 200
        except Exception:
            return False

    def embed(self, text: str) -> list[float]:
        if not self._available():
            raise RuntimeError("Ollama unavailable")
        payload = json.dumps({"model": self.model, "prompt": text}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.api_url}/api/embeddings", data=payload, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read())
        return data["embedding"]


def make_embedder() -> NGramEmbedder | OllamaEmbedder:
    if os.environ.get("RAG_EMBEDDER", "").lower() == "ngram":
        return NGramEmbedder()
    try:
        ollama = OllamaEmbedder()
        if ollama._available():
            return ollama
    except Exception:
        pass
    return NGramEmbedder()


def cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
