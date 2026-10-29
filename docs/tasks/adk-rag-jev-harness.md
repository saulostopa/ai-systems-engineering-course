---
title: Feature — ADK + RAG + Jev harness
---

# Feature — ADK + RAG + Jev harness

Status: **active** · Owner: Harness Foundation Course · Target: Project 06

## Decision

Create a separate `adk-rag-harness` composition project. Keep the existing RAG harness independent and make Google ADK the workflow and runtime layer. Add Jev as a typed decision provider for bounded routing, guardrails, and evidence decisions structured across the 4 pillars: **Route, Filter, Score, and Release**.

| Layer | Responsibility |
|---|---|
| ADK | Session lifecycle, workflow graph, agents, tools, retries and runtime integration |
| Jev | Bounded typed decisions (`Noul`, `Choice`, `Score`) covering model routing, guardrails, tool call authorization, reranking, and response evaluation |
| Policy code | Tripartite thresholds (`execute`, `confirm`, `human`), fallbacks, escalation and irreversible-action rules |
| RAG | Ingestion, chunking, embeddings, retrieval, reranking adapter and citations |
| LLM | Tiered models: small for direct answers, large for reasoning and final synthesis |

## Architecture Pillars (The 4 Jev Quadrants)

The harness architecture implements the operational decision principles detailed in the [Jev reference](/reference/jev):

1. **Route (Model Routing)**:
   - Jev evaluates prompt complexity: routes simple tasks to lightweight models ($) and complex synthesis/reasoning to frontier models ($$$).
2. **Filter (Guardrails & Tool Calls)**:
   - *Pre-LLM Guardrail*: blocks prompt injection and abusive requests before invoking generative models.
   - *Tool Call Authorization*: intercepts agent tool requests and deterministically evaluates `allow`, `ask` (HITL confirmation), or `deny`.
3. **Score (Reranking & Evals)**:
   - *Evidence Reranking*: scores retrieved chunks so the synthesis LLM only receives the highest-signal context.
   - *Inline LLM Eval*: scores generated responses for factual groundedness and source adherence prior to display.
4. **Release (Tripartite Confidence Gating)**:
   - High confidence ($\ge 0.85$): automated execution.
   - Medium confidence ($0.50$–$0.84$): requires interactive user confirmation.
   - Low confidence ($< 0.50$): escalates to human review (HITL).

## Implementation Slices

### Slice 1 — Retrieval and Evidence Policy (Delivered)
Evaluates three bounded questions:
1. Does this request require retrieval? (`direct` vs `retrieve` vs `clarify`)
2. Which knowledge collection or retrieval strategy should be used?
3. Is the returned evidence sufficient to answer? (`sufficient` vs `insufficient/blocked`)

### Slice 2 — Guardrail, Routing, and Action Gating (Evolution)
1. Add input sanitization guardrail before tool dispatch.
2. Route `direct` requests to small local models (`llama3.2:3b`) and complex RAG synthesis to larger models (`qwen2.5:14b` / hosted).
3. Intercept tool executions with the `allow` / `ask` / `deny` policy gate.
4. Apply inline answer evaluation to catch hallucinations prior to UI response.

The initial implementation is available in the [standalone `adk-rag-harness` project](https://github.com/saulostopa/harnesses/tree/main/adk-rag-harness). It provides the provider-neutral contracts, deterministic retrieval policy, a dependency-free Jev adapter for TypeSafe's `/v1/systemone` contract, an optional adapter for the official `typesafe-sdk` Python package, an allowlisted adapter for the existing `rag-harness`, provider-failure fallback and twenty-nine offline tests. The optional Google ADK runtime adapter exposes the bounded workflow as a structured `LlmAgent` tool and an `App`; its `adk_app/agent.py` is an executable ADK entrypoint with Jev through OpenRouter (`typesafe/jev-router`) as the default conversation model and typed decision model, Ollama (`llama3.1:8b` and `qwen2.5:14b`) as the opt-in local alternative and an opt-in real `rag-harness` retrieval provider. Install the `adk` and `openrouter` extras for the default app, and add `ollama` and `jev-sdk` for the local and official TypeSafe modes.

## Contracts

Introduce a provider-neutral decision interface so tests can use a fake provider and the harness can compare Jev with rules or another classifier.

```python
class DecisionProvider(Protocol):
    async def decide(
        self,
        state: DecisionState,
        questions: list[Question],
    ) -> DecisionResult:
        ...
```

The RAG adapter exposes a typed retrieval contract containing the query, collection, filters, requested result count, evidence chunks, answerability and reason. Every answer preserves source references.

## Guardrails and evaluation gate

- Confidence thresholds are policy configuration in code, not model behavior.
- Low confidence routes to a deterministic fallback or human-in-the-loop escalation.
- Evidence and user-controlled text are treated as untrusted input.
- No irreversible action is authorized solely by a Jev score.
- Provider failures, timeouts and schema errors are observable and fail closed.
- The initial version supports offline tests without an API key.

Move from planned to active only after measuring retrieval-needed classification, collection and strategy routing, evidence sufficiency, false negatives and positives, latency, cost, fallback rate, citation completeness and final answer quality.

The decision is visualized in the [ADK + RAG + Jev architecture](https://github.com/svslwm/harness-plannig/blob/develop/docs/architecture/adk-harness-architecture.html).

## References

- [Google ADK](https://adk.dev/)
- [ADK integrations](https://adk.dev/integrations/)
- [Jev Decision Architecture](/reference/jev)
- [Jev overview](https://imasters.com.br/inteligencia-artificial/o-que-e-o-jev-e-por-que-eu-comecei-a-usar)
- [Jev decision model notes](https://github.com/dannote/jev/blob/master/guides/introduction/why-jev.md)
