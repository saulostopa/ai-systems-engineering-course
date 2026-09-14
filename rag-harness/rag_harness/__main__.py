"""CLI da POC — indexação e recuperação agêntica.

Uso:
    python -m rag_harness index <dir> [--verbose]
    python -m rag_harness query <dir> "<consulta>" [--top-k N]
    python -m rag_harness agent <dir> "<consulta>"
    python -m rag_harness hybrid <dir> "<consulta>"
"""

from __future__ import annotations

import argparse
import os
import sys

from .agentic import AgentController, pretty
from .embeddings import make_embedder
from .indexer import index_dir, load_index
from .retrieval import hybrid_search, lexical_search


def _index_dir_for(root: str) -> str:
    return os.path.join(root, ".rag_index")


def main() -> None:
    ap = argparse.ArgumentParser(prog="rag_harness")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_index = sub.add_parser("index")
    p_index.add_argument("root")
    p_index.add_argument("--verbose", action="store_true")

    p_query = sub.add_parser("query")
    p_query.add_argument("root")
    p_query.add_argument("text")
    p_query.add_argument("--top-k", type=int, default=5)

    p_hybrid = sub.add_parser("hybrid")
    p_hybrid.add_argument("root")
    p_hybrid.add_argument("text")
    p_hybrid.add_argument("--top-k", type=int, default=5)

    p_agent = sub.add_parser("agent")
    p_agent.add_argument("root")
    p_agent.add_argument("text")

    args = ap.parse_args()
    embedder = make_embedder()
    print(f"embedder: {type(embedder).__name__}")

    if args.cmd == "index":
        index = index_dir(args.root, embedder, verbose=args.verbose)
        print(f"OK: {len(index.chunks)} chunks em {_index_dir_for(args.root)}")
        return

    idx_dir = _index_dir_for(args.root)
    if not os.path.exists(idx_dir):
        print(f"ERRO: índice não existe em {idx_dir} — rode 'index' primeiro", file=sys.stderr)
        sys.exit(1)
    index = load_index(idx_dir)

    if args.cmd == "query":
        print(f"\n== lexical top-{args.top_k} ==")
        print(pretty(lexical_search(index, args.text, args.top_k)))

    elif args.cmd == "hybrid":
        print(f"\n== hybrid (RRF) top-{args.top_k} ==")
        print(pretty(hybrid_search(index, embedder, args.text, args.top_k)))

    elif args.cmd == "agent":
        ctrl = AgentController(index, embedder)
        results = ctrl.retrieve(args.text, args.root)
        print(f"\n== agent (ferramentas usadas: {', '.join(ctrl.used_tools)}) ==")
        print(pretty(results))


if __name__ == "__main__":
    main()