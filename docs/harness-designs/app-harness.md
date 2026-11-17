---
title: App Harness — QA + agentic navigation
---

# App Harness — QA + agentic navigation

> The harness that combines the deterministic E2E test (QA layer) with
> vision-based agentic exploration (navigation layer). Two layers, one app.

## The two layers

```
┌────────────────────────────────────────────────────────┐
│ Layer 2 — Agentic navigation (C2)                      │
│ Agent starts the app, navigates, validates with vision,│
│ produces verdict + screenshots as evidence             │
├────────────────────────────────────────────────────────┤
│ Layer 1 — QA (C1)                                      │
│ E2E Playwright as a mechanical commit gate             │
│ (e2e-gate.sh) + flaky triage via trace viewer          │
├────────────────────────────────────────────────────────┤
│ Skeleton — basic harness (B1)                          │
└────────────────────────────────────────────────────────┘
```

## Layer 1 — QA (E2E as a gate)

Delivered in `app-harness/` (Scripts + templates):

- `scripts/e2e-gate.sh` — pre-commit gate: staged frontend without a corresponding E2E test → **blocks** (fail-open without config).
- `templates/.harness/config.yaml` — declaration of `frontend_paths` / `frontend_extensions` / `e2e_test_path`.
- `templates/e2e/` — Page Object Model + test with intercepted network (deterministic pattern).
- Triage protocol: `--trace=retain-on-failure` + `playwright show-trace` — flaky is a bug, not luck.

Required patterns (from the `qa-playwright-e2e` skill): semantic locators, POM,
network interception, zero fragile CSS/XPath.

## Layer 2 — Agentic navigation with vision

The layer that distinguishes the app harness from "a repo with tests". The agent:

1. **Starts the app** — build + dev server (or build preview).
2. **Navigates like a user** — via browser automation (Playwright/agent).
3. **Validates with vision** — the model *sees* the screenshots: layout, overlap,
   infinite loading, empty and error states.
4. **Produces a verdict per criterion** — accepted/rejected + screenshots as
   evidence (Lesson 09: proof, not opinion).
5. **Closes the loop** — each exploration finding becomes a new E2E test in layer 1
   (the exploratory finds; the deterministic immortalizes).

The skill that implements this protocol is in
`app-harness/skills/agentic-navigation/SKILL.md` — install it in
`.claude/skills/` (or `.agents/skills/`) of the app project and trigger it with:

```
"validate the search screen we just implemented"
```

The skill's protocol: Gather (diff + tests + acceptance criteria) → start the
app → deterministic state (interception) → walk flows and edge
states → screenshot per step → **verdict per criterion** (ACCEPTED/REJECTED
with screenshot). The verdict format is a table + findings with probable cause
— ready to become an E2E test in layer 1.

```
build → E2E (gate) → agentic navigation (vision) → findings → new E2E tests → ...
```

### Jev in App Harness: Real-Time Loop & Action Safety

Applying the [Jev decision architecture](/reference/jev) enhances agentic navigation:
1. **Real-Time Loop (~300ms)**: Browser DOM transition steps and route choices run through Jev's fast typed decisions, avoiding invoking heavy multimodal LLMs on every micro-click. The expensive vision LLM is invoked only for visual anomaly detection and layout validation checkpoints.
2. **Tool Call Guardrail**: Jev intercepts browser tool calls with `allow` / `ask` / `deny`, blocking destructive actions (e.g., checkout submissions or database truncations in live staging) or requesting operator confirmation (HITL).

## Why the two layers

| | E2E (QA) | Agentic navigation |
|---|---|---|
| Nature | Deterministic, cheap, fast | Exploratory, expensive, slow |
| Catches | Known regressions | What nobody predicted |
| When | Every commit (gate) | Before accepting/delivering |
| Evidence | Exit code + output | Screenshots + verdict per criterion |

One doesn't replace the other: E2E protects at every commit; agentic navigation
validates what the test didn't predict — including what *looks* right in the test
and is genuinely broken on the screen.

## Use in the course

- **[Project 03](/projects/project-03)** builds the app harness from scratch — this
  blueprint is the reference solution.
- **Pilot G2** ran both layers on a real app: the E2E gate blocked and allowed correctly, and the agentic navigation returned HTTP 200. Evidence in `pilots/g2-app-harness/evidence/`.

**Related**: [Basic harness](/harness-designs/basic-harness) · [Enterprise harness](/harness-designs/enterprise-harness) · [ADK + RAG + Jev](/harness-designs/adk-rag-jev-harness)

