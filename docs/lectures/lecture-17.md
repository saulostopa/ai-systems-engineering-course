---
title: Lesson 17 — Building a Hard Harness
---

# Lesson 17 — Building a Hard Harness

> The hands-on lesson: the `hard-harness/` component of this course — executable graph,
> typed contracts, deterministic gates, database-free persistence, resumption
> and auditing. Everything executable here and now.

## The architecture on one page

```
hard-harness/
├── core/          # graph, runner, schemas, gates, events — the core
├── stores/        # FileStateStore (no database) + AgEnFKStore (adapter)
├── adapters/      # adk2 (optional inspiration) + rag (context provider)
├── agents/        # planner, coder, reviewer, evidence — reasoning only
├── examples/basic_workflow/   # the complete graph of the requirement
└── tests/         # 19 tests (transitions, gates, fan-out, limits...)
```

Golden rule in one line: **the agent proposes; the runner decides; the gate
blocks; the store records.**

## State machine

`WorkflowState` carries status (`pending → running → blocked → passed →
failed → closed`), current node, persistent data, retries, LLM calls and
errors. **Only the runner transitions** — the `_transition` method is internal.

```python
from hard_harness.core import Runner, WorkflowGraph

runner = Runner(graph, store=store, limits=Limits(max_depth=16, max_retries=2))
state = runner.run(initial={"scope": {...}})
```

## Schemas — typed contracts

`NodeInput` (immutable view) → `NodeOutput` (proposal) → the runner validates:

- `NodeOutput.proposed_next` — the agent's suggestion; the runner accepts/refuses.
- `NodeOutput.gate` — `GateResult` with failures `{check, expected, actual}`.
- `NodeOutput.evidence` — `Evidence` (command, expected, actual, passed).
- `NodeOutput.review` — `ReviewResult` (verdict + findings).

## Deterministic gates

```python
from hard_harness.core.gates import gate_from_command, gate_node_output

build = gate_node_output("build", gate_from_command("build", "npm run build", "build"))
```

The gate runs the real command; exit ≠ 0 → explicit failure; the runner **blocks the
transition** (no "it seems to work").

## Fan-out and join

```python
g.fan_out("coder_agent", ["build", "tests", "e2e", "lint"])
g.join("join", ["build", "tests", "e2e", "lint"], "router")
```

The runner fires the 4 in parallel (`MAX_CHILDREN` applied), aggregates by id and
only then executes the join. A child failure NEVER disappears: it becomes an explicit payload
(`{"error": ...}`) that the join/router decides. Fan-out without join = explicit error.

## Deterministic router with default

```python
def route_by_checks(state_data):
    return "passed" if state_data.get("join", {}).get("all_ok") else "failed"

g.router("router", route_by_checks, {"passed": "reviewer_agent", "failed": "correction_agent"}, default="correction_agent")
```

Unknown route → default takes over → **never ends silently** (ADK L2b
lesson; tested).

## Evidence

Every gate produces `Evidence`; the `evidence` node consolidates the fan-out; evidence
events are emitted and persisted. The harness's currency (Lesson 09) is now
generated and audited by the runtime.

## Database-free persistence

```
.harness/
├── state.json     # atomic snapshot (tmp + rename)
├── events.jsonl   # append-only audit trail
├── artifacts/     # node artifacts
└── locks/         # mutual exclusion (O_EXCL)
```

`StateStore` interface (read/write/events) — `FileStateStore` for now;
`AgEnFKStore` and SQLite later, with the same contract.

## Resumption and auditing

```python
store = FileStateStore("my_run")
runner = Runner(graph, store=store)
runner.bus.subscribe(lambda ev: store.append_event(ev))
state = runner.run(...)          # executes and persists at each node
state2 = runner.run(state=store.read_state())  # resumes from the checkpoint
```

Interrupted mid-way? `read_state()` + `run(state=...)` resumes from the current node.
Every transition, refused proposal and gate failure becomes an `Event` — auditable.

## Running the complete example

```sh
cd hard-harness
PYTHONPATH=. python3 examples/basic_workflow/workflow.py
PYTHONPATH=. python3 tests/test_hard_harness.py   # 19/19
```

## Key takeaways

1. Framework-agnostic core: ADK is inspiration, not a dependency.
2. Agent proposes → runner decides → gate blocks → store records.
3. Typed contracts make invalid transitions impossible to silence.
4. Limits (depth, width, retries, LLM, timeout) live in code.
5. Minimal file persistence + events = resumption and auditing without a database.

## Check your learning

```
"quiz me on Lesson 17"
```

**Back to theory**: [15 — From Markdown to runtime](/lectures/lecture-15) · [16 — ADK 2](/lectures/lecture-16)
