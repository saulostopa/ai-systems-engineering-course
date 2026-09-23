---
title: Feature — ADK + RAG + Jev harness
---

# Feature — ADK + RAG + Jev harness

Status: **active** · Owner: Harness Foundation Course · Target: Project 06

## Decision

Create a separate `adk-rag-harness` composition project. Keep the existing RAG harness independent and make Google ADK the workflow and runtime layer. Add Jev as a typed decision provider for bounded routing and evidence decisions.

| Layer | Responsibility |
|---|---|
| ADK | Session lifecycle, workflow graph, agents, tools, retries and runtime integration |
| Jev | Noul, Choice and Score decisions with confidence |
| Policy code | Thresholds, fallbacks, escalation and irreversible-action rules |
| RAG | Ingestion, chunking, embeddings, retrieval, reranking and citations |
| LLM | Query rewriting, synthesis and final answer generation |

## First slice

Evaluate three decisions:

1. Does this request require retrieval?
2. Which knowledge collection or retrieval strategy should be used?
3. Is the returned evidence sufficient to answer?

Jev must not generate prose, replace semantic retrieval, or become the only safety boundary. Code retains a deterministic fallback for unavailable, low-confidence or contradictory decisions.

The initial implementation is available in `adk-rag-harness/`. It provides the provider-neutral contracts, deterministic retrieval policy, a dependency-free Jev adapter for TypeSafe's `/v1/systemone` contract, an optional adapter for the official `typesafe-sdk` Python package, an allowlisted adapter for the existing `rag-harness`, provider-failure fallback and twelve offline tests. The optional Google ADK runtime adapter exposes the bounded workflow as a structured `LlmAgent` tool and an `App`; install `adk-rag-harness[adk,jev-sdk]` only when running it with Google ADK and the official SDK.

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

- Confidence thresholds are policy configuration, not model behavior.
- Low confidence goes to a deterministic fallback or clarification path.
- Evidence and user-controlled text are treated as untrusted input.
- No irreversible action is authorized solely by a Jev score.
- Provider failures, timeouts and schema errors are observable and fail closed.
- The initial version supports offline tests without an API key.

Move from planned to active only after measuring retrieval-needed classification, collection and strategy routing, evidence sufficiency, false negatives and positives, latency, cost, fallback rate, citation completeness and final answer quality.

The decision is visualized in the [ADK + RAG + Jev architecture](https://github.com/svslwm/harness-plannig/blob/develop/docs/architecture/adk-harness-architecture.html).

## References

- [Google ADK](https://adk.dev/)
- [ADK integrations](https://adk.dev/integrations/)
- [Jev overview](https://imasters.com.br/inteligencia-artificial/o-que-e-o-jev-e-por-que-eu-comecei-a-usar)
- [Jev decision model notes](https://github.com/dannote/jev/blob/master/guides/introduction/why-jev.md)
