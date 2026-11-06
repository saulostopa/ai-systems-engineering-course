---
title: Backlog — Jev decisions through TypeSafe
---

# Backlog — Jev decisions through TypeSafe

Status: **backlog** · Priority: **P1** · Scope: ADK + RAG + Jev harness

## Why this belongs in the harness backlog

The ADK + RAG + Jev harness currently decides through
`HARNESS_DECISION_PROVIDER=openrouter` with
`HARNESS_DECISION_MODEL=typesafe/jev-router`. That route is useful, but it is
a model router: Jev picks a model (Kimi answered the Biometrik tests on
2026-10-29) and that model fills the JSON decision contract. Its confidence
values are self-reported, exactly like a local Ollama model, so the tripartite
gate (`execute`, `confirm`, `human_review`) still rests on an LLM's opinion of
itself.

TypeSafe's `/v1/systemone` endpoint is the typed decision service the course
describes ("the LLM writes, Jev decides"). The harness already ships the
adapters — `JevDecisionProvider` (dependency-free) and
`TypeSafeSdkDecisionProvider` (`[jev-sdk]` extra), selected with
`HARNESS_DECISION_PROVIDER=typesafe` — and `evals/run_jev_evals.py`, but the mode has
never been validated against the live service.

## Goal

Make `typesafe` (TypeSafe System One) a validated decision provider, compare it with
`typesafe/jev-router` and the local Ollama mode on the same prompts, and decide
with evidence which one becomes the default.

## Proposed evolution

1. **Credential handling.** Read `TYPESAFE_API_KEY` from the environment or
   from a local credential file outside the repository, as the OpenRouter key
   already is. Never log, print or commit it; fail closed with an explicit
   message when it is missing.
2. **Live smoke test.** Run `evals/run_jev_evals.py` and the ADK app with
   `HARNESS_DECISION_PROVIDER=typesafe` against the demo RAG and a real index.
3. **Comparative evaluation.** Send the golden prompts plus a real-repository
   set (documentation, code, no-retrieval, injection attempts, ambiguous
   requests) through `typesafe`, `openrouter` (`typesafe/jev-router`)
   and `ollama` (`qwen2.5:14b`). Record route, collection,
   strategy, confidence, latency, tokens and cost per decision.
4. **Calibrate the gate.** Check whether TypeSafe confidences separate correct
   from wrong decisions better than self-reported ones, and adjust
   `auto_threshold` and `review_threshold` only from that evidence.
5. **Choose the default.** Keep `typesafe/jev-router` as default unless `typesafe`
   wins on accuracy or calibration at an acceptable cost; document the
   trade-off in lecture 18 and project 06.

## Acceptance criteria

- `HARNESS_DECISION_PROVIDER=typesafe` runs end to end in `adk web` with a real
  index and returns typed `Noul`, `Choice` and `Score` answers.
- Missing credentials, quota errors and timeouts produce `blocked` with
  `human_review`, never an unverified answer.
- The comparison report covers the three providers on the same prompts, with
  accuracy, confidence calibration, latency and cost.
- The default decision provider is chosen from that report and the reason is
  recorded in the harness README and the course.
- No credential reaches the repository, logs or evaluation output.

## Dependencies

- A TypeSafe account and API key.
- The token and cost ledger, so the comparison reports cost from the same
  source as daily use.

## References

- [Current ADK + RAG + Jev feature](/tasks/adk-rag-jev-harness)
- [Jev reference](/reference/jev)
- [TypeSafe Python SDK](https://github.com/typesafe-ai/typesafe-sdk-python)
