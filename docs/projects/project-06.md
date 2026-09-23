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

The first offline slice is available in `adk-rag-harness/`. Run its four tests with `python3 -m unittest discover -s tests -v` from that directory. It does not require an API key or Google ADK yet.

See the [feature record](/tasks/adk-rag-jev-harness) for the adopted decisions and guardrails.
