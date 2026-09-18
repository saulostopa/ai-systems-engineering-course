---
title: Project 01 — Baseline vs. minimal harness
---

# Project 01 — Baseline vs. minimal harness

> The first experiment of the course: the same feature, with and without a harness. Measure the difference before trusting it.

## Objective

Run a real feature **twice** — once with the "raw" agent (no harness) and once with the minimal harness — and compare:

- time to delivery;
- number of errors fixed after the first "done";
- amount of rework (fix commits);
- sense of confidence (verified vs. "it seems to work").

The result is **your** baseline: from it on, every harness you build will have a number to compare against.

## Prerequisites

- A test repository (can be a fork of a small project or a new repo).
- An installed agent (Claude Code, OpenCode, Cursor, Codex or Gemini CLI).
- The same well-delimited feature for both rounds (e.g.: "add email validation to form X").

## Step by step

### Round A — no harness (baseline)

1. Open the repo **without** any AGENTS.md, skills or rules.
2. Ask the agent: `implement email validation on form X`.
3. Note: time to the first "done", what it verified (if it verified), how many fixes came afterward.
4. Don't interfere — let the agent declare victory its own way.

### Round B — with minimal harness

1. Add to the repo:

```markdown
# AGENTS.md

## 1. What this repo is
Test project for Project 01 of the course.

## 2. How to verify
- Run `npm run build` — it must pass.
- Run `npm test` — it must pass.
- Nothing is "done" without the build and tests run and attached.

## 3. Scope
- One feature at a time.
- Don't touch anything outside the feature.
```

2. Add the state:

```json
{
  "features": [
    { "id": "f1", "title": "Email validation", "status": "in_progress" }
  ]
}
```

3. Ask the **same** task to the agent.
4. Note: time to "done" *with* build and tests, how many fixes, what it recorded as evidence.

### Comparison

| Metric | Round A (no harness) | Round B (minimal harness) |
|---|---|---|
| Time to first "done" | | |
| "Dones" that failed the build/tests | | |
| Fixes after "done" | | |
| Evidence recorded (yes/no) | | |

## Verification

- Build and tests pass in Round B (in A, note whether they passed or the agent "forgot").
- Round B's diff touches only the declared scope.
- You can point out **exactly what** the harness changed in the agent's behavior.

## Deliverable

A paragraph in your learning journal (or in the project's `session-handoff.md`):

> "Without a harness the agent [X]; with a harness it [Y]. The difference came from [files/policies]."

::: tip Tip
Keep the comparison spreadsheet — it will be the seed of the course's internal benchmark (EPIC G, metrics and evidence).
:::

**Next project**: [02 — Installable basic harness](/projects/project-02).
