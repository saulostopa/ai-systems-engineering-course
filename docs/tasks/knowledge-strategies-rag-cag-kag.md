---
title: Backlog — knowledge strategies for RAG, CAG and KAG
---

# Backlog — knowledge strategies for RAG, CAG and KAG

Status: **backlog** · Priority: **P1** · Scope: ADK + RAG + Jev and the RAG harnesses

## Why this belongs in the harness backlog

The current course treats RAG as the main external-knowledge strategy. The
article's distinction is useful because knowledge has different shapes:

- **RAG** searches a changing or large corpus and injects selected evidence at
  request time.
- **CAG** preloads a stable, bounded context pack and reuses the processed
  context. KV caching is an implementation technique, not a guarantee every
  model or local runtime exposes in the same way.
- **KAG** reasons over connected entities, relations and rules, while keeping
  links back to source material. The KAG research framework combines knowledge
  graphs with retrieval and logical-form-guided reasoning; it is more specific
  than simply adding a graph database to a RAG system.

The supplied visual is registered as backlog evidence:

![RAG vs CAG vs KAG knowledge strategies](/images/rag-cag-kag.gif)

## Recommended placement

Do not create three independent harnesses yet. Add a typed **knowledge
strategy decision** to the ADK + RAG + Jev harness, with these bounded modes:

| Mode | Best fit | Course placement | Decision |
|---|---|---|---|
| `rag` | Large, changing or selectively searchable knowledge | Existing local and PostgreSQL RAG harnesses | Keep as the default baseline. |
| `cag` | Stable, small knowledge packs such as policies, API contracts or a domain playbook | First add as a context-pack profile to `adk-rag-harness` and domain harnesses | Benchmark before adding provider-specific KV-cache code. |
| `kag` | Connected entities, multi-hop questions, rules and explainable domain reasoning | Future `adk-kag-harness`, likely building on the PostgreSQL and ADK boundaries | Create only after a real graph-shaped use case is selected. |

The router should decide from measurable signals: corpus size, freshness,
context budget, relationship density, query hop count, citation requirements
and latency budget. Jev can classify the bounded choice; code validates the
choice, applies limits and preserves deterministic fallback behavior.

## Proposed evolution

1. Define a provider-neutral `KnowledgeStrategy` contract with `rag`, `cag` and
   `kag` decisions.
2. Implement `cag` as a versioned context pack first: manifest, source hashes,
   token budget, provenance and invalidation rules. Keep the initial version
   compatible with Ollama and OpenRouter without requiring KV-cache APIs.
3. Add a benchmark suite that sends the same prompts through RAG and CAG and
   measures answer quality, citation completeness, freshness, latency, tokens
   and fallback rate.
4. Specify a KAG pilot with a small domain graph, source-linked edges,
   multi-hop questions and a blocked path for unsupported reasoning.
5. Create a separate KAG harness only if the pilot shows that graph traversal
   materially improves answer quality over hybrid RAG.

## Acceptance criteria

- The router records why it selected `rag`, `cag` or `kag`.
- Every mode returns source provenance or explicitly reports that provenance is
  unavailable.
- CAG invalidates a context pack when its source manifest changes.
- KAG never treats an inferred edge as a verified fact without a source link.
- The evaluation compares all available modes on the same golden prompts.
- Low confidence, stale context, graph gaps and provider failures take a
  deterministic safe path.

## References

- [Cache-Augmented Generation](https://arxiv.org/abs/2412.15605)
- [KAG: Boosting LLMs in Professional Domains via Knowledge Augmented Generation](https://arxiv.org/abs/2409.13731)
- [Current ADK + RAG + Jev feature](/tasks/adk-rag-jev-harness)
