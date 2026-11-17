---
title: Lesson 15 — From Markdown to an executable runtime
---

# Lesson 15 — From Markdown to an executable runtime

> The evolution of this course: from the harness that *instructs* to the harness that *executes*.

## The limit of Markdown

So far, the harness was Markdown: AGENTS.md, policies, SKILL.md, templates.
They instruct the agent — and they work well for guidance. But they have a ceiling:

| Capability | Markdown | Executable code |
|---|---|---|
| Enforce step order | instruction ("do X after Y") | graph: the runner executes in order |
| Block invalid transition | gate hook (if installed) | `runner` refuses at runtime |
| Guarantee "done" only with evidence | policy | deterministic gate + schema |
| Enforce limits (retries, depth) | "do not exceed..." | `Limits` enforced in code |
| Auditability | git log + narrative | persisted event trail |
| Resumption | session-handoff.md | checkpoint + state resume |

Lesson 04's lesson still holds — **short router + routed docs** — but
now there is a second layer: what is *control* (order, gates, state, limits)
must become code; what is *knowledge* (context, explained policies,
skills) stays in Markdown.

## Instruction, policy, contract, control

Four types of rule — and four homes:

| Type | Example | Where it lives |
|---|---|---|
| **Instruction** | "read the AGENTS.md before editing" | AGENTS.md / SKILL.md |
| **Policy** | "one feature `in_progress` at a time" | `policies/*.md` (explanation) |
| **Contract** | typed `NodeInput` → `NodeOutput` | **code** (schemas) |
| **Control** | "only the runner advances status" | **code** (runner) |

Markdown **explains**; code **governs**. The executable rule has a **single source
of truth**: the schema/gate/runner — not five markdowns that diverge.

## What stays in Markdown

- **AGENTS.md**: the router (what to read, how to work) — never the flow authority.
- **SKILL.md**: on-demand knowledge (how to do X) — loaded when the task asks for it.
- **policies/**: the *reason* of the rules (the why of the DoD, of the scope) — the rule itself becomes a gate.
- **Docs and lessons**: explain the system; the system executes by itself.

## Why the agent cannot be the workflow authority

The agent reasons; the workflow **controls effects and state**. If the agent
decided when "done", we would be back to Lesson 09's self-deception — now
mechanized at scale. The ADK 2 pattern (and of this course):

> **Agents produce proposals/results; the runner controls effects and state.**

In `hard-harness`, the agent returns `NodeOutput(proposed_next=...)` — and the
runner decides whether to accept it, refuse it (with an auditable event) or follow the graph.
There is no transition API for the agent (verified by test).

## Minimal executable example

```sh
cd hard-harness
PYTHONPATH=. python3 examples/basic_workflow/workflow.py
# → boot → load_scope → planner → validate_plan → coder
#   → fan-out [build, tests, e2e, lint] → join → router → reviewer → evidence → close
```

## Key takeaways

1. Markdown instructs; code executes. Control ≠ knowledge.
2. Contract and control live in schemas/gates/runner — single source of truth.
3. Policies explain the why; gates enforce the what.
4. The agent proposes; the runner decides. State authority is never delegated.

## Check your learning

```
"quiz me on Lesson 15"
```

**Next lesson**: [16 — ADK 2 and the three orchestration patterns](/lectures/lecture-16).
