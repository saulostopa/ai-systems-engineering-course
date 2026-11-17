---
title: Backlog — token and cost ledger
---

# Backlog — token and cost ledger

Status: **in progress** · Priority: **P1** · Scope: `harness-usage`, `rag-harness`, ADK + RAG + Jev and hard harness

## Why this belongs in the harness backlog

Every LLM call made by a harness spends tokens and, with hosted providers,
money: Jev decisions, the conversation model, embeddings for indexing and for
each query, and the hard-harness agents. Until now only the hard harness kept
token counts, and no harness recorded what a question, a feature or an index
actually cost. Without that evidence the course cannot compare providers
(for example [Jev through TypeSafe](/tasks/jev-typesafe-decisions)) or keep a
monthly budget.

## Decisions (2026-10-29)

| Topic | Decision |
|---|---|
| Storage | One JSONL file per month inside each target repository, at `.harness/usage/YYYY-MM.jsonl`, ignored by Git |
| Budget | `HARNESS_BUDGET_USD`, default US$ 25 per month across all ledgers; warn at 80% and 100%, never block |
| First delivery | `rag-harness`, `adk-rag-harness` and `hard-harness` |
| Reports | Terminal table, CSV, Markdown and a self-contained HTML dashboard |

## Record format

One line per provider call, append-only. Prompts, answers, code and keys are
never stored.

```json
{"schema": 1, "ts": "2026-10-29T22:10:03Z", "run_id": "…", "request_id": "…",
 "harness": "adk-rag-harness", "component": "decision",
 "provider": "openrouter", "model": "typesafe/jev-router", "routed_model": "deepseek/…",
 "input_tokens": 812, "output_tokens": 64, "cached_tokens": 0,
 "cost_usd": 0.00041, "cost_source": "provider",
 "latency_ms": 930, "status": "ok", "error_kind": null,
 "project": "biometrik-app-reactnative", "feature": "jev-adk-rag-harness"}
```

- `component`: `decision`, `chat`, `embedding_index`, `embedding_query` or
  `agent`.
- `request_id` groups every call made for one question.
- `routed_model` is the model a router such as `typesafe/jev-router` picked.
- `cost_source`: `provider` (OpenRouter returns `usage.cost` in US$),
  `price_table` (tokens × the cached OpenRouter price list), `local` (Ollama,
  zero) or `unknown`.
- `feature` comes from the target repository's `active_feature_id` when it
  exists.

## Reports

- Totals by day and month, with a month-end projection and budget status.
- By component, provider, model and routed model.
- By project and feature.
- Per question (`request_id`): average, p50 and p95.
- Indexing cost and error rate per provider.

## Acceptance criteria

- Every billed call in the three harnesses writes one ledger line, also when
  it fails.
- Writing the ledger never breaks a harness: an I/O error is reported once and
  the call proceeds.
- A ledger inside a Git repository that is not ignored triggers a warning.
- The budget warning appears at 80% and 100% of `HARNESS_BUDGET_USD`.
- Reports read several repositories at once.
- No prompt, answer, code excerpt or credential reaches the ledger.

## References

- [ADK + RAG + Jev feature](/tasks/adk-rag-jev-harness)
- [Jev decisions through TypeSafe](/tasks/jev-typesafe-decisions)
