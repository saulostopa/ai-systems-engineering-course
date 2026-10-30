---
title: Project 06B — ADK RAG with PostgreSQL
description: PostgreSQL and pgvector reference harness for larger software teams.
---

# Project 06B — ADK RAG with PostgreSQL

This is the larger-project variant of Project 06. It keeps the same ADK + RAG
workflow boundary and replaces the local JSON index with PostgreSQL and
pgvector.

Use it when several people or services share the knowledge base, when the
repository contains many functions and architectural records, or when the
retrieval data needs metadata filters and centralized persistence. The local
`adk-rag-harness` remains the recommended implementation for the course and
small projects.

## Download and run

The reference project is available in the repository under
[`adk-rag-postgres-harness`](https://github.com/saulostopa/harnesses/tree/main/adk-rag-postgres-harness).

```bash
git clone https://github.com/saulostopa/harnesses.git
cd adk-rag-postgres-harness
uv sync --extra postgres
docker compose up -d postgres
uv run python -m adk_rag_postgres_harness.cli migrate
```

Ingest a collection with local semantic embeddings:

```bash
ollama pull nomic-embed-text
HARNESS_EMBED_PROVIDER=ollama HARNESS_EMBED_MODEL=nomic-embed-text \
PYTHONPATH=.:../rag-harness \
uv run python -m adk_rag_postgres_harness.cli ingest /path/to/your-repository --collection docs
```

The database stores the source, chunk boundaries, metadata and embedding. The
retrieval query combines PostgreSQL full-text search with pgvector cosine
similarity and returns the same evidence contract used by the local harness.

The database does not make a workflow deterministic by itself. Determinism
comes from the typed route, allowed collections and strategies, stable ordering,
thresholds and the blocked state when evidence is insufficient.

**Blueprint**: [ADK RAG PostgreSQL Harness](/harness-designs/adk-rag-postgres-harness)
