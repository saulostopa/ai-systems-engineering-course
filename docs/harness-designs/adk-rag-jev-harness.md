---
title: ADK + RAG + Jev Harness
---

# ADK + RAG + Jev Harness

This design combines Google ADK for the runtime, a RAG adapter for evidence, and
Jev for bounded typed decisions based on the principle: **"The LLM writes, Jev decides"**.
The generative model proposes structured text and actions; Jev evaluates decisions across
four operational pillars (**Route, Filter, Score, and Release**), and the policy code owns
routing, thresholds, and fallback paths.

```text
user request
  │
  ▼
[ Jev Guardrail (Filter) ] ── (abusive / injection) ──► blocked
  │ (clean)
  ▼
[ Jev Model Router (Route) ]
  ├─ simple request ──────► Small LLM ($) ─────────► Direct Answer
  └─ complex / knowledge ──► ADK Workflow
                               │
                               ├─ [ Jev Tool Call Gate (Filter) ] ──► allow / ask / deny
                               ├─ RAG adapter ──► [ Jev Reranker (Score) ] ──► top-K evidence
                               │
                               ▼
                        Large LLM ($$$) (Synthesis)
                               │
                               ▼
                        [ Jev Response Eval (Score) ]
                               │
                               ▼
                        [ Tripartite Gate (Release) ]
                          ├─ high confidence (≥ 0.85) ──► execute / return
                          ├─ medium confidence ─────────► confirm with user
                          └─ low confidence (< 0.50) ───► human escalation (HITL)
```

## The 4 Operational Pillars in this Harness

| Pillar | Jev Responsibility | Harness Authority |
|---|---|---|
| **Route** | Evaluates prompt complexity; selects Small vs. Large LLM | Preserves tokens and enforces cost/latency budgets |
| **Filter** | Pre-LLM Guardrail (blocks injections); Tool Call authorization (`allow`, `ask`, `deny`) | Prevents malicious prompts and guards destructive tool actions |
| **Score** | Reranks retrieved RAG chunks; scores LLM output groundedness | Minimizes context window and catches hallucinations |
| **Release** | Emits confidence scores for tripartite gating | Code executes, asks user confirmation, or stops on `blocked` |

The RAG layer never selects the next workflow node. It returns source, text,
score and line metadata. The workflow blocks when the provider fails or evidence
is insufficient, so the model cannot turn an unsupported answer into success.

## Core Architectural Layers

| Layer | Responsibility | Authority |
|---|---|---|
| ADK | session, tool call and Dev UI traces | runtime lifecycle |
| Jev | typed `noul`, `choice` and `score` answers across the 4 pillars | bounded decision output |
| Workflow & Policy | route, tripartite thresholds, fallbacks and blocked state | final control flow |
| RAG adapter | query the selected collection, rerank chunks, return sources | evidence only |
| Tiered LLMs | generation and synthesis calibrated by model tier | prose generation only |

## Reference project

The implementation is available in
[`adk-rag-harness`](https://github.com/saulostopa/harnesses/tree/main/adk-rag-harness).
The [ADK + RAG + Jev project](/projects/project-06) explains installation,
providers, prompts and evaluations.

The foundational design principles are documented in the [Jev decision architecture reference](/reference/jev).
The architecture diagram is available as
[`adk-harness-architecture.html`](https://github.com/svslwm/harness-plannig/blob/develop/docs/architecture/adk-harness-architecture.html).

## When to use it

Use this design when retrieval needs explicit routing and reviewable evidence,
especially for repository assistants, architecture questions, multi-tier cost management,
and mission-critical workflows where an unsupported answer or unauthorized action must stop execution.
