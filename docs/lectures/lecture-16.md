---
title: Lesson 16 — ADK 2 and the three orchestration patterns
---

# Lesson 16 — ADK 2 and the three orchestration patterns

> Required conceptual reference:
> [ADK 2 Orchestration codelab](https://codelabs.developers.google.com/adk2/instructions).
> Three patterns, one axis: **who decides the next step** — the graph you
> drew, the LLM or your code at runtime.

## The decision axis

| Pattern | Who decides the next step | When to use |
|---|---|---|
| **1 · Graph** | the graph you drew | you can draw the flow before the input arrives |
| **2 · Collaborative** | the LLM (coordinates experts) | the team is known, but the request picks the subset |
| **3 · Dynamic** | your code, at runtime | the *shape* of the work depends on the input |

A sentence from the codelab to keep: *"predictable work stays as functions;
clear rules become explicit routing; reasoning uses the model."*

## 1 · Graph workflows

When the flow is knowable a priori, draw the graph:

```
START ─► fetch_weather ─┐
START ─► analyze_course ┼─► JoinNode ─► strategy_agent
START ─► pull_fitness ──┘
```

- **functions and agents are peers** — predictable work costs 0 LLM;
- **parallel fan-out** — three edges leaving START are already parallelism;
- **JoinNode** — waits for ALL sources and aggregates by name;
- **deterministic router** — an `if`, not the model:
  `route = "HOT" if temp >= 70 else "COLD" ...` with **DEFAULT_ROUTE required**;
- agents only where there is reasoning (strategy, not routing).

The cost: the codelab shows the "one giant agent" version making 4 calls and
inventing numbers — the graph makes **1 call** with the data coming from code.

## 2 · Collaborative agents

When the team is fixed but the request picks the members:

- **`chat`** (subagent default) — transfers the whole conversation to an
  expert; never automatically returns;
- **`single_turn`** — each expert becomes a *tool*; the coordinator
  calls the subset **in parallel**, each returns a **typed** result,
  and the coordinator synthesizes;
- **`task`** — conversation with a *typed finish line*: asks until it collects
  the fields, pauses, and returns via `finish_task` with a validated object.

Choosing the mode in one question: *"does the user need to talk to it — until
when?"* → chat (indefinitely) · task (until the fields) · single_turn (never).

## 3 · Dynamic workflows

When the shape of the work is born from the input:

- **runtime width** — `parallel_worker=True` fans a worker over N items
  decided by the LLM;
- **recursion written by you** — the worker calls itself via `ctx.run_node`;
- **limits in code** — `if finding.needs_deeper and depth < MAX_DEPTH` is
  YOUR code, not configuration. The codelab is explicit: the recursion is yours, the
  brake is yours.

⚠️ The ceiling grows fast: `MAX_DEPTH=3` takes ~30 calls to ~93.

## Application to this course's harnesses

| Harness | Dominant pattern | Where |
|---|---|---|
| Basic (B1) | **Graph** | pipeline plan → code → test → review → close |
| Enterprise (B2) | **Graph + Collaborative** | workflow engine + per-area experts |
| App (C) | **Graph** | fan-out of tests/E2E/a11y/navigation + join |
| RAG/Area Copilot (D) | **Graph (with context node)** | RAG is *context provider*, never orchestrator |
| Domains (E) | **Graph (same core)** | Finance/Games/Commercial provide skills and schemas |

## How to choose (the codelab tree)

```
Do SequentialAgent/ParallelAgent/LoopAgent solve it?  → use them, stop
└─ No — I need a router, join or non-agent nodes
   ├─ Can I draw it before the input?  → Graph
   └─ No
      ├─ Known team, request picks?  → Collaborative
      └─ Shape depends on the input? → Dynamic
```

## Key takeaways

1. Three patterns, one axis: who decides the next step.
2. Function for predictable; router for clear rule; agent for reasoning.
3. DEFAULT required in routers — an unknown route never dies silently.
4. Dynamic = code; therefore, the limits are yours, in code.
5. The `hard-harness` implements the Graph pattern as its core (Lesson 17) and leaves
   Collaborative/Dynamic as evolution — ADK is inspiration, not a dependency.

## Check your learning

```
"quiz me on Lesson 16"
```

**Next lesson**: [17 — Building a Hard Harness](/lectures/lecture-17).
