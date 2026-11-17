---
title: Project 06B — ADK RAG with PostgreSQL
description: A code memory on PostgreSQL and pgvector, used with Jev or by a coding agent alone.
---

# Project 06B — ADK RAG with PostgreSQL

Build a code memory for a real repository, then measure it. The search runs locally, so
only the path with Jev has a cost.

**Quick View: How it Works:** <a href="/demos/code-memory-postgres-jev.html" target="_blank" rel="noopener">open the flow</a> (in Portuguese).

## 1. Install and index

The project is in
[`adk-rag-postgres-harness`](https://github.com/saulostopa/ai-systems-engineering-harnesses/tree/feature/code-memory-postgres/adk-rag-postgres-harness),
on the `feature/code-memory-postgres` branch until it is merged.

```bash
git clone -b feature/code-memory-postgres https://github.com/saulostopa/ai-systems-engineering-harnesses.git
cd harnesses/adk-rag-postgres-harness
uv sync --extra postgres
docker compose up -d postgres
ollama pull qwen3-embedding:4b
uv run python -m adk_rag_postgres_harness.cli index /path/to/repo --project my-repo
```

The first run embeds every chunk, which took about 13 minutes for 1,300 chunks on an M1 Max.
A run with no changes takes under a second.

## 2. Search and save decisions

```bash
uv run python -m adk_rag_postgres_harness.cli search "where is the login handled" --project my-repo
uv run python -m adk_rag_postgres_harness.cli symbol useUser --project my-repo
uv run python -m adk_rag_postgres_harness.cli uses useUser --project my-repo
uv run python -m adk_rag_postgres_harness.cli remember "Retries live in the API client." \
  --project my-repo --kind decision --source "PR 12"
uv run python -m adk_rag_postgres_harness.cli recall "where do retries live" --project my-repo
```

`remember` writes to `docs/harness/memories.jsonl` in the target repository. Commit that file:
Git is the backup, and `index` restores it on a new machine.

## 3. Use it without Jev

From the target repository, give the tools to your agent:

```bash
claude mcp add --scope local code-memory -- uv run --directory /path/to/adk-rag-postgres-harness \
  --extra postgres python -m adk_rag_postgres_harness.cli mcp --project my-repo
```

agy takes the same command through `agy mcp add`, but its setting applies to every
repository. Claude Code and agy have been tested, and Codex has not.

## 4. Use it with Jev

```bash
cd ../adk-rag-harness
uv sync --extra adk --extra openrouter --extra postgres
HARNESS_RAG_PROVIDER=postgres HARNESS_RAG_PROJECT=my-repo uv run adk web
```

Jev and the conversation model are billed through OpenRouter, while the search stays local.
Ollama must be running for `hybrid` and `semantic`.

## 5. Measure before you tune

Write questions with the file that should answer each one, as in
`evals/biometrik_questions.json`, and run:

```bash
uv run --extra postgres python evals/run_retrieval.py --questions my_questions.json --out results.json
```

Our first default found the right file in only 56% of the questions. We could only see that,
and fix it, because we measured. Use `queries --json` to turn recorded questions into your
next evaluation set: questions you write after reading the code favor the search.

**Blueprint**: [ADK RAG PostgreSQL Harness](/harness-designs/adk-rag-postgres-harness)
