---
title: ADK RAG PostgreSQL Harness
---

# ADK RAG PostgreSQL Harness

This is the shared-storage variant of the ADK + RAG + Jev design. It keeps the
same typed workflow and evidence contract while storing chunks, metadata and
embeddings in PostgreSQL with pgvector.

```text
repositories and docs → AST/line chunks → Ollama embeddings
                                      ↓
                         PostgreSQL + pgvector
                          ├─ full-text search
                          └─ vector similarity
                                      ↓
                           hybrid evidence ranking
                                      ↓
                         ADK + Jev → retrieved or blocked
```

| Concern | Local ADK RAG | PostgreSQL ADK RAG |
|---|---|---|
| Storage | ignored JSON index | PostgreSQL + pgvector |
| Audience | course and small projects | shared team projects |
| Updates | local reindex command | centralized collection replacement |
| Filters | adapter-level configuration | metadata and JSONB filters |
| Retrieval | lexical/semantic controller | full-text + cosine ranking |

PostgreSQL provides shared persistence and efficient retrieval; it does not
decide workflow transitions. Determinism still comes from typed decisions,
allowed collections and strategies, stable ordering, thresholds and `blocked`.

## Reference project

The implementation is available in
[`adk-rag-postgres-harness`](https://github.com/svslwm/harness-plannig/tree/develop/adk-rag-postgres-harness).
See [Project 06B](/projects/project-06-postgres) for Docker, migrations,
ingestion and local Ollama embedding commands.

## When to use it

Use this design when several users or services share the index, when the
repository has many code and architecture chunks, or when retrieval needs
metadata filters and centralized updates.
