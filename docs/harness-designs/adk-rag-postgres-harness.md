---
title: ADK RAG PostgreSQL Harness
---

# ADK RAG PostgreSQL Harness

This design is a **code memory**: one local index of a repository, its decisions and its
feature logs, used with Jev or by a coding agent alone. It is built from open source
parts and needs no paid API to search.

**Quick View: How it Works:** <a href="/demos/code-memory-postgres-jev.html" target="_blank" rel="noopener">open the flow</a> (in Portuguese) of one question, with Jev and without it.

```text
Git files → syntax-aware chunks → Ollama embeddings → PostgreSQL + pgvector
                                                              │
             ┌────────────────────────────────────────────────┤
             │                                                │
   With Jev: adk web                              Without Jev: MCP or CLI
   Jev picks collection and strategy              the agent decides what to search
   gates can block for human review               the agent writes the answer
   conversation and decisions are billed          no OpenRouter call
```

## What it stores

| Data | Source | If the database is lost |
|---|---|---|
| Chunks, symbols and imports | Git files, chunked by tree-sitter or by lines | `index` rebuilds them |
| Embeddings | `qwen3-embedding:4b`, keyed by content hash and model | `index` computes them again |
| Memories | `docs/harness/memories.jsonl`, committed in the target repository | `index` restores them |
| Recorded questions | Searches from the CLI, MCP and `adk web` | Lost, so export them first |

## The boundaries that matter

- **Search does not decide.** PostgreSQL returns evidence. The typed route, allowed
  collections, thresholds and `blocked` still come from the workflow.
- **Text comes from disk.** The database gives the path and lines, and `stale` marks a file
  that changed after indexing.
- **Some files stay out.** Symbolic links, names such as `.env*` or `secret`, binary files
  and very large files are skipped and listed.
- **Failures are visible.** Without the database or the model, a retrieval ends in `blocked`
  with `human_review`. `keyword` needs no model, so it still works without Ollama.

## What the evaluation changed

We measured 32 questions about one repository, counting the right file in the top 5.
The results changed the design more than the choice of model did:

| Search | Result |
|---|---|
| Hybrid across all collections, the first default | 56% |
| By meaning across all collections, the current default | 91% |
| Hybrid in the right collection | 94% |

- **The model was not the problem.** `qwen3-embedding:8b` and `voyage-code-4` gave no clear
  gain over the smaller local model.
- **Mixing rankings can hurt.** Full text matched any word and favored long documents, which
  buried the code.
- **Names need a direct path.** Ranking finds the many uses of a name before its one
  definition, so names in code style now return the definition first.
- **The router needs context.** Told that questions are about the repository, Jev stopped
  answering them from general knowledge, and rose from 20 to 26 of 32.
- **A tool that exists may go unused.** Claude Code chose MCP in 3 of 10 questions, and agy in
  none. Claude Code still answered well with grep, so the gain from MCP is not proven at this size.

These numbers use questions written after reading the code, and the fixes were chosen with
them, so they may be slightly optimistic. The next evaluation uses recorded real questions.

## When to use it

Use it when you want searchable decisions, or when a repository is large enough that grep
stops being enough. For a small project, the [local RAG harness](/harness-designs/rag-harness)
needs no Docker.

## Reference project

See [Project 06B](/projects/project-06-postgres) for the steps, and the
[backlog](/tasks/code-memory-postgres) for the full record.
