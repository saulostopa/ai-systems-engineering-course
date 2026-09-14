"""Area Copilot — motor de contexto de negócio sobre o rag_harness.

O índice vive em <root>/area_context/ (por convenção: planilhas/, documentos/,
imagens/) e o índice vetorial em <root>/.area_index. O agente consulta com
fonte citável — número sem fonte é proibido (Aula 09).

Uso:
    python -m area_harness index <root> [--verbose]
    python -m area_harness query <root> "<pergunta>"
    python -m area_harness eval <root> [--queries area_harness/tests/queries.json]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from rag_harness.agentic import AgentController
from rag_harness.chunker import Chunk
from rag_harness.embeddings import make_embedder
from rag_harness.indexer import Index

from .business_chunker import chunk_business_dir


def index_area(root: str, embedder=None, verbose: bool = False) -> Index:
    embedder = embedder or make_embedder()
    chunks = chunk_business_dir(root)
    index = Index(chunks=chunks, vectors={}, file_hashes={})
    index.vectors = {c.hash: embedder.embed(c.text) for c in chunks}
    os.makedirs(os.path.join(root, ".area_index"), exist_ok=True)
    import json as _json

    with open(os.path.join(root, ".area_index", "vectors.json"), "w", encoding="utf-8") as fh:
        _json.dump(index.vectors, fh)
    with open(os.path.join(root, ".area_index", "chunks.json"), "w", encoding="utf-8") as fh:
        _json.dump(
            [
                {"path": c.path, "kind": c.kind, "name": c.name, "text": c.text,
                 "start_line": c.start_line, "end_line": c.end_line, "hash": c.hash}
                for c in chunks
            ],
            fh,
            ensure_ascii=False,
            indent=1,
        )
    if verbose:
        print(f"[area-copilot] {len(chunks)} chunks de negócio indexados")
    return index


def load_area_index(root: str) -> Index:
    import json as _json

    with open(os.path.join(root, ".area_index", "vectors.json"), "r", encoding="utf-8") as fh:
        vectors = _json.load(fh)
    with open(os.path.join(root, ".area_index", "chunks.json"), "r", encoding="utf-8") as fh:
        chunks = [Chunk(**r) for r in _json.load(fh)]
    return Index(chunks, vectors, {})


def answer_with_sources(root: str, question: str, embedder=None, top_k: int = 3) -> str:
    """Recupera o contexto e devolve o trecho com FONTE CITADA — pronto para
    o agente (ou a skill area-report) montar o artefato."""
    embedder = embedder or make_embedder()
    index = load_area_index(root)
    ctrl = AgentController(index, embedder)
    results = ctrl.retrieve(question, root)
    if not results:
        return "Sem contexto encontrado na área."
    lines = [f"Pergunta: {question}", "Contexto com fontes:"]
    for c in results[:top_k]:
        preview = c.text[:300].replace("\n", " ")
        lines.append(f"- FONTE: {c.path} (linhas {c.start_line}-{c.end_line})")
        lines.append(f"  {preview}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(prog="area_harness")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_i = sub.add_parser("index")
    p_i.add_argument("root")
    p_i.add_argument("--verbose", action="store_true")
    p_q = sub.add_parser("query")
    p_q.add_argument("root")
    p_q.add_argument("text")
    p_e = sub.add_parser("eval")
    p_e.add_argument("root")
    p_e.add_argument("--queries", default=os.path.join(os.path.dirname(__file__), "tests", "queries.json"))

    args = ap.parse_args()
    embedder = make_embedder()
    print(f"embedder: {type(embedder).__name__}")

    if args.cmd == "index":
        index_area(args.root, embedder, verbose=True)
        return
    if args.cmd == "query":
        print(answer_with_sources(args.root, args.text, embedder))
        return
    if args.cmd == "eval":
        from .eval import run_area_eval

        run_area_eval(args.root, args.queries, embedder)


if __name__ == "__main__":
    main()