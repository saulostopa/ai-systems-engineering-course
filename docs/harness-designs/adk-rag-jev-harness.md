---
title: ADK + RAG + Jev Harness
---

# ADK + RAG + Jev Harness

This design combines Google ADK for the runtime, a RAG adapter for evidence and
Jev for bounded typed decisions. The model proposes structured answers; the
workflow validates them and the code owns routing, thresholds and failure paths.

```text
user request → ADK agent → run_workflow tool → Jev decision
                                      ├─ direct → answer
                                      ├─ clarify → ask again
                                      └─ retrieve → RAG adapter → evidence
                                                        ├─ retrieved
                                                        └─ blocked
```

| Layer | Responsibility | Authority |
|---|---|---|
| ADK | session, tool call and Dev UI traces | runtime lifecycle |
| Jev | typed `noul`, `choice` and `score` answers | bounded decision output |
| Workflow | route, thresholds, fallbacks and blocked state | final control flow |
| RAG adapter | query the selected collection and return sources | evidence only |

The RAG layer never selects the next workflow node. It returns source, text,
score and line metadata. The workflow blocks when the provider fails or evidence
is insufficient, so the model cannot turn an unsupported answer into success.

## Reference project

The implementation is available in
[`adk-rag-harness`](https://github.com/saulostopa/harnesses/tree/main/adk-rag-harness).
The [ADK + RAG + Jev project](/projects/project-06) explains installation,
providers, prompts and evaluations.

The architecture diagram is available as
[`adk-harness-architecture.html`](https://github.com/svslwm/harness-plannig/blob/develop/docs/architecture/adk-harness-architecture.html).

## When to use it

Use this design when retrieval needs explicit routing and reviewable evidence,
especially for repository assistants, architecture questions and workflows
where an unsupported answer must stop execution.
