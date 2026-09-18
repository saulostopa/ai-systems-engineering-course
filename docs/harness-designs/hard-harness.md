---
title: Hard Harness — executable orchestration
---

# Hard Harness — executable orchestration

> The `hard-harness/` component of this course: executable graph, typed
> contracts, deterministic gates and specialized agents — framework-
> agnostic, with ADK 2 as a conceptual reference (not a dependency).

## The core in one sentence

**Agent proposes → runner decides → gate blocks → store records.**

```
hard-harness/
├── core/          # schemas, graph, runner, gates, events
├── stores/        # FileStateStore (no database) + AgEnFKStore (adapter)
├── adapters/      # adk2 (inspiration), rag (context provider)
├── agents/        # planner, coder, reviewer, evidence (reasoning only)
├── examples/
│   ├── basic_workflow/    # complete pipeline (the 1st consumer)
│   └── app_harness/       # QA fan-out + join (C integration)
└── tests/         # 19 unit tests
```

Lessons: [15](/lectures/lecture-15) · [16](/lectures/lecture-16) · [17](/lectures/lecture-17).

## Running

```sh
cd hard-harness
PYTHONPATH=. python3 examples/basic_workflow/workflow.py   # complete pipeline
PYTHONPATH=. python3 tests/test_hard_harness.py            # 19/19
```

## Integration with the five harnesses

### 1 · Basic harness (B) — the first real consumer

The `examples/basic_workflow` is the `plan → code → test → review → close` workflow
that the basic harness always documented — now **executable**:

```
boot → load_scope → planner_agent → validate_plan (gate) → coder_agent
  → fan-out [build, tests, e2e, lint] → join → router
      ├─ passed → reviewer_agent → evidence → close
      └─ failed → correction_agent → coder_agent (limited retry)
```

The B1 gates (`gatekeeper.sh`, `validate-harness.sh`) remain in the hooks;
what changed is that **order and state** now belong to the graph, not the instruction.

### 2 · Enterprise harness (B2) — AgEnFK adapter

`stores/agenfk_store.py` implements the `StateStore` interface against AgEnFK:
reads item/status, records progress (`verify`) and evidence (`log-test`) when
available. If AgEnFK is unavailable, the store **stops and informs** —
never bypasses. Hierarchy, evidence, gatekeeper and telemetry remain
AgEnFK's; the runner only talks to it through the interface.

### 3 · App harness (C) — QA fan-out + join

`examples/app_harness/` demonstrates the App Harness pattern: one node fires in
parallel **unit tests, E2E, accessibility and exploratory navigation**,
and the `join` consolidates the results before the router decides. One core,
four verifications — no engine per verification.

### 4 · RAG / Area Copilot (D) — RAG as a context node

`adapters/rag.py` wraps the rag-harness `AgentController` with a minimal
contract: `provide_context(question) → typed context`. The workflow *asks* for
context (`context` node), RAG **doesn't decide transitions** — it doesn't receive the
runner and never proposes the next node. Retrieval separated from orchestration.

```python
rag = RagContextProvider(rag_harness_root=".../rag-harness", index_dir=".../.rag_index")
g.add_node(Node("context", NodeKind.DETERMINISTIC, rag.as_node()))
```

### 5 · Domain harnesses (E) — skills and schemas on the same core

Finance, Games and Commercial **don't create their own engines**: they provide the core with
1) skills (the domain knowledge), 2) schemas (typed contracts of their
artifacts) and 3) gates (their verifications — reconciliation, playtest,
proposal-check). The `domains/` remains the knowledge library; the
`hard-harness` is the only engine.

## LLM providers — OpenRouter (default), Ollama (optional)

The core agents receive an injectable provider
(`hard_harness/llm/providers.py`). Selection by environment, no network surprises:

```sh
# default (same flow as this session):
OPENROUTER_API_KEY=... PYTHONPATH=. python3 examples/basic_workflow/workflow.py

# optional — local:
OLLAMA_API_URL=http://localhost:11434 PYTHONPATH=. python3 examples/basic_workflow/workflow.py

# no env: deterministic stub (clear warning), perfect for tests/offline
```

- **OpenRouterProvider** — OpenAI-compatible API (stdlib urllib), default
  model `deepseek/deepseek-v4-flash-0731` (the same as this session), usage captured.
- **OllamaProvider** — local `/v1/chat/completions` endpoint, availability probe.
- **Cost in the runner** — the provider attaches `llm_cost` (usage in k-tokens) to
  the agent payload; the runner applies `Limits.llm_budget` on top of the real cost.
- **Living evidence**: the complete workflow ran with real OpenRouter — the planner
  generated a plan (1.157 k-tokens), the reviewer asked for changes on the stub diff
  (real reasoning), evidence synthesized; 4 calls, 19 events, status closed.

## Architecture decisions (and honest limits)

| Decision | Why |
|---|---|
| Framework-agnostic core | ADK 2 is inspiration/adapter; own orchestration doesn't depend on a provider |
| Agents only reason | state authority is never delegated (tested) |
| Router with mandatory default | unknown route never ends silently (ADK L2b lesson) |
| File-first persistence | `.harness/` (state.json + events.jsonl + artifacts + locks) — database later |
| Limits in code | MAX_DEPTH/CHILDREN/RETRIES/LLM_CALLS/timeout/budget in the runner |
| RAG = context, never orchestrator | retrieval separated from orchestration (course requirement) |
| No database in this version | `FileStateStore` today; `AgEnFKStore`/SQLite via the same interface |

**Limitations**: agents are stubs (LLM provider to inject); Collaborative and
Dynamic (ADK 2) are declared evolution, not implemented in the core — the graph
already supports runtime fan-out via `run_fanout` with `MAX_CHILDREN`.

**Related**: [Lesson 16 (ADK 2)](/lectures/lecture-16) · [Basic harness](/harness-designs/basic-harness) · [Enterprise harness](/harness-designs/enterprise-harness) · [App Harness](/harness-designs/app-harness) · [RAG](/harness-designs/rag-harness)
