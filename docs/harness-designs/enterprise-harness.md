---
title: Enterprise harness (multi-team)
---

# Enterprise harness (multi-team)

> The harness for projects where many teams work: the basic + layers of
> governance, flow and observability. Defined by **contracts**, not by a product.

## Who it's for

Large projects, multiple teams, many agents in parallel, need for
auditing and measurement. The enterprise harness doesn't replace the basic — **it wraps it**:
each team keeps its skeleton; the enterprise layer adds flow,
gatekeepers, telemetry and reports.

## The two layers

Everything below fails in practice if you get one thing wrong: **where each piece
lives**. The enterprise harness is installed in two places, and the division is
not a matter of taste.

```
~/wm-harness/                  ← A · orchestrator: once per machine, above the projects
├── engine/                      runner, gates, CLI
├── flows/                       flow definitions shared by the organization
├── telemetry/                   cross-project aggregation
└── ui/                          kanban, dashboards

<team-repo>/                   ← B · control: in the repo, in the PR, reviewable
├── AGENTS.md
├── feature_list.json            scope and state per feature
├── progress.md · session-handoff.md
├── policies/
├── .harness/
│   ├── config.yaml              which flow, which engine version
│   ├── state.json               state of the current run
│   └── events.jsonl             append-only trail
└── docs/exec-plans/
    ├── active/                  plans in flight
    └── done/                    completed, with evidence attached
```

The rule that decides the split:

> **The orchestrator owns the *how*. The repository owns the *what* and the
> *what happened*.**

Flow definitions, gates and aggregation are shared and versioned centrally —
one learning curve for the whole organization. Scope, plans, evidence and state
live in the repo, travel in the PR and get reviewed like code.

And the test for any case you're unsure about:

> **If deleting the orchestrator from the machine would make the project lose
> information about itself, the piece is in the wrong layer.**

Every developer installs layer A once. Layer B arrives in the repo through the
orchestrator's installer and stays small on purpose: no engine, no
`node_modules`, no database — only what controls the features.

::: warning The failure this prevents
A workflow engine that keeps items, comments and evidence in a central database
*outside* the repo fails the test above: wipe the tool and the project's history
is gone. It also breaks [Lesson 03](/lectures/lecture-03) — the repository stops
being the system of record. Central storage is fine for **aggregation**
(telemetry, cross-team views); it is not fine as the **only** copy.
:::

## The capability layers

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

This layer is a **contract**, not a product. Any engine that satisfies the five
requirements below serves; the choice of implementation comes later and is
reversible.

| Requirement | What it means | Lesson |
|---|---|---|
| **Items with hierarchy and type** | EPIC → STORY → TASK/BUG; the `feature_list.json` gains parentage and flow | 08 |
| **Configurable flows** | each work type has steps with a **mandatory exit criterion** | 13 |
| **Mechanical gatekeeper** | edits only within an active item; **DONE unreachable by shortcut** | 07 |
| **Evidence as a step** | test recorded PASSED/FAILED *before* completing — self-deception becomes a flow failure | 09 |
| **Auditable trail** | status history, comments, evidence: the "who, when, why" of each item | 11 |

Writing it as a contract is what makes the layer portable. A team can start with
files and hooks, move to a shared engine later, and the other three layers never
notice.

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

## Execution plans, in the repo

Layer 3's contract needs somewhere to put the decomposition of a feature. That
somewhere is `docs/exec-plans/`, and it follows three rules.

**The directory is a context budget.** At boot the agent reads `active/` only —
a small, bounded set ([Lesson 06](/lectures/lecture-06)). Finished plans move to
`done/` so the reading never grows without limit ([Lesson 04](/lectures/lecture-04)).

**The front-matter is the truth.** The authoritative status is a field inside the
plan, never its location. Two sources that can disagree eventually will.

The id is the branch name — `feature/OEM-123`, `bugfix/AC-455`,
`release/EST-3445` — so a plan and a branch are the same thing. The file
flattens the slash, because a slash is a path separator.

```markdown
docs/exec-plans/active/feature-OEM-123.md
---
id: feature/OEM-123
status: in_progress
flow: feature-default
exit_criteria:
  - build green
  - e2e passing
---

# Steps
1. [x] scope declared
2. [ ] implementation
3. [ ] evidence recorded

# Evidence
(required before status: done)
```

**The gate reconciles the two.** `validate-harness.sh` fails when the location
diverges from the status, and when a plan marked `done` has no evidence block.
Archiving stops being a convention somebody remembers and becomes mechanical —
which is the whole argument of [Lesson 07](/lectures/lecture-07).

Each artifact keeps a distinct job, with no overlap:

| Artifact | Role | Lesson |
|---|---|---|
| `feature_list.json` | the **map** — what exists and in what state | 08 |
| `docs/exec-plans/active/` | the **route** — decomposition of the feature in flight, with exit criteria | 13, 14 |
| `docs/exec-plans/done/` | the **record** — what happened, with evidence | 09, 11 |
| `progress.md` / `session-handoff.md` | **session** continuity | 05 |

## The multi-team model

Each team = a project with its items and flows, **in the same framework**:

```
Catalog team   (project A) ──┐
Fipe team      (project B) ──┼──▶ workflow engine (shared orchestrator)
Finance team   (project C) ──┘        │
                                      ├── central aggregation (telemetry)
                                      └── per-team report
```

Benefits: a single pattern (single learning curve), telemetry
aggregates per team, and governance scales without reinventing.

Note what does **not** cross the arrow: each project's scope, plans and evidence
stay in its own repository. The orchestrator reads them to aggregate; it is not
their home.

## Scoping — the enterprise harness only where you want it

The enterprise harness needs a **scope** decision: it must only act on the
projects that opted in. The mechanics:

- the gatekeeper **checks the file path** against `.harness/config.yaml`
  and only acts inside managed projects (fail-open outside them);
- rules and skills are installed **in the project** (`.claude/skills/` or
  `.agents/skills/`, the repo's `AGENTS.md`), not globally;
- outside the project: fully independent agent; inside: complete workflow.

Installing rules globally is the common mistake: it makes every repository on
the machine inherit a workflow it never opted into. Independence between agents
on the same machine is non-negotiable.

## Implementations

The layers above are the design. Implementing them is a separate, reversible
choice — and more than one option works:

| Option | Where it fits | Trade-off |
|---|---|---|
| **Files + hooks** (extended basic harness) | small organizations, first step | zero infrastructure; cross-project aggregation is manual |
| **Issue tracker + CI** (Jira, GitHub Projects + Actions) | teams already living in the tracker | reuses existing tooling; gates depend on CI discipline |
| **Dedicated engine** | many teams, need for telemetry | strongest enforcement; one more service to run |

::: tip Internal reference — AgEnFK
`agenfk` is an engine built by the Car Sales team that covers layers 3 and 4
(items, flows, gatekeeper, evidence, telemetry, Kanban UI). If you are at
Webmotors and want a ready implementation, it is worth a look.

It is a **reference, not a requirement**: no harness in this course depends on
it, and none of the lessons require it. Two things to check against the rule
above before adopting it: its state lives in a central SQLite outside the
repository, and its initialization expects Claude Code installed.
:::

## Maturity — what exists today

This page is a **blueprint**. Part of it is code you can install right now; part
is still a contract waiting for an implementation. Reading it as a finished
product would be a mistake, so here is the honest state:

| Layer | State today | Where |
|---|---|---|
| A · Orchestrator | **Ready and installable** — `wm-harness` CLI: adopt, status, check, plan, report | `enterprise-harness/install.sh` |
| 1 · Skeleton | **Ready and installable** | `harness-basic/install.sh` |
| 2 · Governance | **Ready** — commit gate, health check, pre-commit/pre-push hooks | `harness-basic/scripts/`, `.githooks/` |
| 3 · Workflow engine | **Working, file-based**: flows drive the plans, the gate reconciles location and status | `enterprise-harness/flows/`, `docs/exec-plans/` |
| 4 · Observability | **Partial** — friction logging and cross-project aggregation work; there is no UI or historical series | `wm-harness report`, `log-event.sh` |

## Starting today

Install the orchestrator once, in a root folder above your projects, then adopt
the repositories that opted in:

```sh
enterprise-harness/install.sh --prefix ~/wm/wm-harness --projects ~/wm
wm-harness adopt ~/wm/catalogo
wm-harness status
```

[Project 06](/projects/project-06) walks through the whole cycle, including the
step that matters most: deleting the orchestrator and watching the projects keep
working.

For a single small repository none of this is needed — `harness-basic/install.sh`
delivers layers 1 and 2 on its own.

What is still missing: there is no UI, no server and no cross-machine sync.
Aggregation is a CLI report computed live from the repositories, and historical
series are not kept anywhere. Those are the reasons to reach for a dedicated
engine, not reasons to wait before starting.

::: info About the EPIC G pilots
The pilots ran on 2026-09-12 and are recorded in `pilots/`: **G1** installed the
basic harness in a real repo (`pricing-cli`), **G2** validated the app harness
QA layer, **G3** put the Area Copilot to work on finance, and **G4** consolidated
the metrics. None of them exercised layer 3 with an engine — which is exactly
the gap this page describes.
:::

## Decision and Routing Gateway with Jev

In a multi-team enterprise setup, unconstrained LLM calls across dozens of adopted repositories quickly explode costs and introduce latency variance. Layer A (`~/wm-harness/`) integrates the [Jev decision architecture](/reference/jev) as an operational gateway:

- **Enterprise Model Router**: Dispatches developer and agent requests to Small ($), Medium ($$), or Large ($$$) models based on task complexity, preserving organizational budget.
- **Tool Call & Security Guardrails**: Intercepts tool calls across workflows with deterministic `allow`, `ask` (HITL), or `deny` policies, preventing destructive deployments or secret leaks.
- **Mass Labeling & Compliance Triage**: Batch-scores and tags repository compliance, test coverage trends, and commit hygiene across all adopted teams without heavy LLM costs.

**Related**: [Basic harness](/harness-designs/basic-harness) ·
[App Harness](/harness-designs/app-harness) · [Domain harnesses](/harness-designs/domain-harnesses) ·
[ADK + RAG + Jev](/harness-designs/adk-rag-jev-harness)

