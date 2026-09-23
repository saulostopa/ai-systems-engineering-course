---
title: Project 06 — ADK + RAG + Jev harness
---

# Project 06 — ADK + RAG + Jev harness

> A deterministic agent workflow where typed decisions choose retrieval policies and code remains in control.

## Objective

Build `adk-rag-harness` as a composition project. Google ADK owns the workflow graph and agent runtime, the RAG subsystem owns evidence retrieval, and Jev evaluates bounded decisions before code routes the run.

The existing `rag-harness` remains usable without ADK or Jev. This project adds an adapter boundary instead of moving RAG internals into the orchestration layer.

## First slice

Implement and evaluate:

1. whether retrieval is needed;
2. which collection or search strategy to use;
3. whether the evidence is sufficient to answer.

Use Jev's typed Noul, Choice and Score decisions. Apply thresholds in code and keep deterministic fallback paths for low confidence, provider failure and contradictory evidence.

## Suggested structure

```text
adk-rag-harness/
├── adk_rag_harness/
│   ├── agent.py
│   ├── workflow.py
│   ├── decision/{interface.py,jev_adapter.py}
│   ├── policies/
│   ├── tools/rag_tool.py
│   └── validators/
├── rag_adapter/client.py
└── tests/
    ├── test_decision_policy.py
    ├── test_retrieval_routing.py
    ├── test_low_confidence_fallback.py
    ├── test_adversarial_state.py
    └── test_full_trajectory.py
```

## Completion criteria

- The provider interface is testable without network access.
- Jev decisions log question, answer, confidence, threshold and selected route.
- Every retrieval result carries source references.
- Low confidence and provider errors take a tested safe path.
- Evaluation reports routing accuracy, retrieval quality, citation completeness, latency, cost and fallback rate.

## Current implementation

The local slice is available in the [standalone `adk-rag-harness` project](https://github.com/saulostopa/harnesses/tree/main/adk-rag-harness) and includes the ADK Dev UI
entrypoint. Install it with `uv sync --extra adk --extra ollama --extra jev-sdk`
from the cloned standalone repository and start it with `uv run adk web`. The
default conversation model is
`llama3.1:8b`; the typed decision provider is local `ollama-system-one` using
`qwen2.5:14b`. The [Ollama Dev UI lesson](/lectures/lecture-18) contains the
complete prompt sequence, screenshots and evidence checklist.
Set `HARNESS_RAG_PROVIDER=rag-harness` after creating the local course index to
replace the demo evidence with real repository sources.

Run the full offline suite with `python3 -m unittest discover -s tests -v` from
that directory. It includes the golden prompt contract evals and does not
require a cloud API key.

See the [feature record](/tasks/adk-rag-jev-harness) for the adopted decisions and guardrails.

**Blueprints**: [ADK + RAG + Jev](/harness-designs/adk-rag-jev-harness) ·
[ADK RAG PostgreSQL](/harness-designs/adk-rag-postgres-harness) ·
[Project 06B](/projects/project-06-postgres)
