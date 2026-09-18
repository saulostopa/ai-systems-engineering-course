---
title: Enterprise harness (multi-team)
---

# Enterprise harness (multi-team)

> The harness for projects where many teams work: the basic + layers of
> governance, flow and observability. Implementation reference: AgEnFK.

## Who it's for

Large projects, multiple teams, many agents in parallel, need for
auditing and measurement. The enterprise harness doesn't replace the basic — **it wraps it**:
each team keeps its skeleton; the enterprise layer adds flow,
gatekeepers, telemetry and reports.

## The layers

```
┌─────────────────────────────────────────────────────┐
│ 4. Observability  (telemetry, log-friction,         │
│    dashboards, harness health check)                │
├─────────────────────────────────────────────────────┤
│ 3. Workflow engine  (items, flows, gatekeeper,      │
│    evidence, DONE only with validation)             │
├─────────────────────────────────────────────────────┤
│ 2. Governance       (policies, mechanical gates,    │
│    hooks, cross-review)                             │
├─────────────────────────────────────────────────────┤
│ 1. Skeleton         (basic harness per project:     │
│    AGENTS.md, feature list, policies)               │
└─────────────────────────────────────────────────────┘
```

### Layer 1 — Skeleton (per project)

The [basic harness](/harness-designs/basic-harness). Each team has its own, with
its area's feature list. Nothing changes here when you scale up.

### Layer 2 — Governance

What the basic already has (commit gatekeeper, validation) becomes an
**organizational contract**:

| Mechanism | Basic | Enterprise |
|---|---|---|
| Commit gate | ONE in_progress feature | + mandatory declared scope (policies/scope-control.md) |
| Push gate | Healthy harness | + mandatory PR report, CI with validation |
| Verification | Build + tests | + E2E gate for frontend (factory: `frontend-qa-gate.sh`) + cross-review per flow |
| Exception | Conscious local bypass | Recorded and auditable bypass (log + reason) |

The governance rule: **if the process depends on goodwill, it doesn't happen**
(Lesson 07). Everything becomes a script, hook or flow step.

### Layer 3 — Workflow engine

This is where AgEnFK comes in as the implementation reference. What it solves:

- **Items with hierarchy and type** (EPIC → STORY → TASK/BUG) — the `feature_list.json`
  becomes a system with parentage and flow.
- **Configurable flows** — each work type has steps with mandatory
  exit criteria (Lesson 13: loops with verifiable criteria).
- **Mechanical gatekeeper** — edits only within an active item; **DONE unreachable
  by shortcut** (only via `validate_progress` in the final step, with evidence).
- **Evidence and test as steps** — `log-test PASSED/FAILED` before completing;
  Lesson 09's self-deception becomes a flow failure.
- **Auditable trail** — status history, comments, evidence: the "who,
  when, why" of each item.

### Layer 4 — Observability

The layer that distinguishes a harness from a bureaucratic process as a continuous
improvement system (Lesson 11):

| Metric | Source |
|---|---|
| Time per step/item | workflow timestamps |
| Friction (retries, loops, stalls) | `log-friction` / `log-event.sh` |
| Cost per feature | token telemetry |
| Harness health | `validate-harness.sh` + layer 3 health check |
| Quality | tests failing before green, resumptions |

Golden rule: **unrecorded friction is observability debt**. Every
friction point becomes a log entry — and every log entry is a candidate for
harness improvement.

## The multi-team model

Each team = a project with its items and flows, **in the same framework**:

```
Catalog team   (project A) ──┐
Fipe team      (project B) ──┼──▶ AgEnFK (shared workflow engine)
Finance team   (project C) ──┘        │
                                       ├── central telemetry
                                       └── per-team report
```

Benefits: a single pattern (single learning curve), telemetry
aggregates per team, and governance scales without reinventing.

## Scoping — the enterprise harness only where you want it

The enterprise harness needs a **scope** decision: it must only act on the
projects that opted in. The mechanics:

- the gatekeeper **checks the file path** against `.agenfk/project.json`
  and only acts inside managed projects (fail-open outside them);
- rules and skills are installed **in the project** (`.claude/skills/`, the repo's
  `AGENTS.md`), not globally;
- outside the project: fully independent agent; inside: complete workflow.

That is exactly what we did in this course when scoping AgEnFK for
`harness-plannig` — independence between agents on the machine is non-negotiable.

## Relationship with the factory and AgEnFK

| Repository | Role in the enterprise harness |
|---|---|
| `webmotors-harness-factory` | Layers 1-2: skeleton, policies, hooks, validation scripts |
| `agenfk` | Layers 3-4: items, flows, gatekeeper, evidence, telemetry, UI |
| `harness-agent-skills` | Shared skills: artifacts, QA, perf (EPIC F) |
| `harness-plannig` | The course + this blueprint (dogfooding) |

## Next steps for this project

The complete enterprise harness (documented and demonstrated) materializes in the
EPIC G pilots — when the basic harness and the workflow engine run together in a real
repo with recorded metrics.

**Related**: [Basic harness](/harness-designs/basic-harness) ·
[App Harness](/harness-designs/app-harness) · [Domain harnesses](/harness-designs/domain-harnesses)
