---
title: Project 06 — ADK + RAG + Jev harness
---

# Project 06 — ADK + RAG + Jev harness

> A deterministic agent workflow where typed decisions choose retrieval policies, route models, and filter tools while code remains in control.

## Objective

Build `adk-rag-harness` as a composition project implementing the core principle: **"The LLM writes, Jev decides"** (see the [Jev reference](/reference/jev)). Google ADK owns the workflow graph and agent runtime, the RAG subsystem owns evidence retrieval, and Jev evaluates bounded decisions across the 4 operational pillars (**Route, Filter, Score, and Release**) before code routes execution.

The existing `rag-harness` remains usable without ADK or Jev. This project adds an adapter boundary instead of moving RAG internals into the orchestration layer.

## Architecture and Slices

### Slice 1 — Retrieval Policy and Evidence Gating
Implement and evaluate:
1. whether retrieval is needed (`direct` vs `retrieve` vs `clarify`);
2. which collection or search strategy to use;
3. whether the evidence is sufficient to answer (`sufficient` vs `blocked`).

Use Jev's typed Noul, Choice and Score decisions. Apply thresholds in code and keep deterministic fallback paths for low confidence, provider failure and contradictory evidence.

### Slice 2 — 4-Pillar Decision Evolution
1. **Route**: Dynamic model routing evaluating query complexity to pick Small LLM ($) vs Large LLM ($$$).
2. **Filter**: Pre-LLM Guardrail blocking prompt injection without LLM token cost; Tool Call filtering authorizing `allow`, `ask` (HITL confirmation), or `deny`.
3. **Score**: Reranking of retrieved evidence chunks; inline answer eval checking groundedness against sources.
4. **Release**: Tripartite execution gating in policy code:
   - high confidence ($\ge 0.85$): execute;
   - medium confidence ($0.50$–$0.84$): confirm with user;
   - low confidence ($< 0.50$): human review (HITL).

## Suggested structure

```text
adk-rag-harness/
├── adk_rag_harness/
│   ├── agent.py
│   ├── workflow.py
│   ├── decision/
│   │   ├── interface.py
│   │   ├── jev_adapter.py
│   │   ├── guardrail.py
│   │   └── model_router.py
│   ├── policies/
│   │   ├── tripartite_threshold.py
│   │   └── tool_policy.py
│   ├── tools/rag_tool.py
│   └── validators/
├── rag_adapter/client.py
└── tests/
    ├── test_decision_policy.py
    ├── test_retrieval_routing.py
    ├── test_guardrail_filter.py
    ├── test_model_routing.py
    ├── test_tool_call_gate.py
    ├── test_low_confidence_fallback.py
    ├── test_adversarial_state.py
    └── test_full_trajectory.py
```

## Completion criteria

- The provider interface is testable without network access.
- Jev decisions log question, answer, confidence, threshold and selected route.
- Adversarial and prompt-injection inputs are blocked by the guardrail filter without LLM token consumption.
- Direct simple requests route to a lightweight model tier while complex synthesis routes to the reasoning tier.
- Tool calls enforce `allow` / `ask` / `deny` boundaries.
- Every retrieval result carries source references and is reranked before LLM synthesis.
- Tripartite confidence thresholds (`execute`, `confirm`, `human`) are enforced in code.
- Evaluation reports routing accuracy, retrieval quality, citation completeness, latency, cost and fallback rate.

## Current implementation

The local slice is available in the [standalone `adk-rag-harness` project](https://github.com/saulostopa/harnesses/tree/main/adk-rag-harness) and includes the ADK Dev UI
entrypoint. Install it with `uv sync --extra adk --extra openrouter`
from the cloned standalone repository and start it with `uv run adk web`. By
default, both the conversation model and the typed decision provider
(`openrouter`) use Jev through OpenRouter (`typesafe/jev-router`),
so the only requirement is an OpenRouter key in `OPENROUTER_API_KEY` or in
`~/.local/share/opencode/auth.json`. The [Ollama Dev UI lesson](/lectures/lecture-18)
runs the same app fully locally and contains the complete prompt sequence,
screenshots and evidence checklist.
Set `HARNESS_RAG_PROVIDER=index` after creating the local course index to
replace the demo evidence with real repository sources.

Run the full offline suite with `python3 -m unittest discover -s tests -v` from
that directory. It includes the golden prompt contract evals and does not
require a cloud API key.

See the [feature record](/tasks/adk-rag-jev-harness) for the adopted decisions and guardrails.

**Blueprints**: [ADK + RAG + Jev](/harness-designs/adk-rag-jev-harness) ·
[ADK RAG PostgreSQL](/harness-designs/adk-rag-postgres-harness) ·
[Project 06B](/projects/project-06-postgres)
