"""Indexador da intranet — varre os diretórios de artefatos e indexa no
motor rag_harness (chunking + cache por hash + RRF).

HTML é convertido em texto (tags removidas) antes do chunking por linhas;
Markdown é chunkado por seções (reuso do chunker de negócio).
"""

from __future__ import annotations

import html as html_lib
import os
import re

from rag_harness.chunker import Chunk
from rag_harness.embeddings import make_embedder
from rag_harness.indexer import Index, file_hash


def html_to_text(source: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", source, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def chunk_artifact_file(path: str) -> list[Chunk]:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        source = fh.read()
    lower = path.lower()
    if lower.endswith((".html", ".htm")):
        text = html_to_text(source)
    else:
        text = source
    lines = text.splitlines(keepends=True)
    size, overlap = 120, 20
    chunks: list[Chunk] = []
    for start in range(0, max(1, len(lines)), size - overlap):
        seg = lines[start : start + size]
        if not seg:
            break
        body = "".join(seg)
        if len(body.strip()) < 40:  # pedaço sem conteúdo real
            continue
        chunks.append(
            Chunk(
                path=path,
                kind="artifact",
                name=f"{os.path.basename(path)} L{start + 1}",
                text=body,
                start_line=start + 1,
                end_line=start + len(seg),
            )
        )
    return chunks


def discover_artifact_dirs(repo_root: str) -> list[str]:
    """Diretórios de artefatos conhecidos do ecossistema."""
    candidates = [
        "skills-artifacts/reports",
        "skills-artifacts/quizzes",
        "domains/finance/relatorios",
        "domains/games/design-docs",
        "domains/commercial/materiais",
        "docs",
        "templates",
        "harness-basic",
    ]
    return [os.path.join(repo_root, c) for c in candidates if os.path.isdir(os.path.join(repo_root, c))]


def index_artifacts(repo_root: str, embedder=None, verbose: bool = False) -> Index:
    embedder = embedder or make_embedder()
    dirs = discover_artifact_dirs(repo_root)
    chunks: list[Chunk] = []
    seen: set[str] = set()
    for d in dirs:
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames[:] = [x for x in dirnames if not x.startswith((".", "__")) and x != "node_modules"]
            for name in sorted(filenames):
                if not name.endswith((".html", ".htm", ".md", ".markdown", ".txt")):
                    continue
                path = os.path.join(dirpath, name)
                if path in seen:
                    continue
                seen.add(path)
                chunks.extend(chunk_artifact_file(path))
    index = Index(chunks=chunks, vectors={}, file_hashes={})
    index.vectors = {c.hash: embedder.embed(c.text) for c in chunks}
    index.file_hashes = {c.path: file_hash(c.path) for c in chunks}
    out_dir = os.path.join(repo_root, "artifacts-intranet", ".intranet_index")
    os.makedirs(out_dir, exist_ok=True)
    import json as _json

    with open(os.path.join(out_dir, "vectors.json"), "w", encoding="utf-8") as fh:
        _json.dump(index.vectors, fh)
    with open(os.path.join(out_dir, "chunks.json"), "w", encoding="utf-8") as fh:
        _json.dump(
            [
                {"path": c.path, "kind": c.kind, "name": c.name, "text": c.text,
                 "start_line": c.start_line, "end_line": c.end_line, "hash": c.hash}
                for c in chunks
            ],
            fh,
            ensure_ascii=False,
        )
    if verbose:
        print(f"[intranet] {len(chunks)} chunks de {len(seen)} artefatos ({len(dirs)} dirs)")
    return index


def load_artifact_index(repo_root: str) -> Index:
    import json as _json

    out_dir = os.path.join(repo_root, "artifacts-intranet", ".intranet_index")
    with open(os.path.join(out_dir, "vectors.json"), "r", encoding="utf-8") as fh:
        vectors = _json.load(fh)
    with open(os.path.join(out_dir, "chunks.json"), "r", encoding="utf-8") as fh:
        chunks = [Chunk(**r) for r in _json.load(fh)]
    return Index(chunks, vectors, {})