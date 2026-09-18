---
title: Lesson 08 — Feature lists as harness primitives
---

# Lesson 08 — Feature lists as harness primitives

> What the agent should do is the most basic question of the harness. The answer is a list with state.

## Why a list with state

A prompt says "implement feature X". But the real world has 40 features, 12 in progress, 5 blocked and a queue of bugs. The agent needs a structure that answers, at any moment:

- What is there to do?
- What is the state of each one?
- What is the priority?
- What is blocked and why?

That structure is the **feature list**: a versioned file (typically JSON) where each feature has an identifier, title, description, state and priority.

## The factory's `feature_list.json`

The `webmotors-harness-factory` uses exactly this pattern:

```json
{
  "status": "not_started",
  "id": "feature-001",
  "title": "Car group landing page",
  "description": "..."
}
```

States of the cycle: `not_started` → `in_progress` → `blocked` → `passing`.

And the operating rule (which we already saw in Lesson 06):

> "Only one feature can be `in_progress` at a time. Pick the highest-priority one among the `not_started`."

## Why it is a harness *primitive*

"Primitive" in the sense of fundamental building block: the feature list is to the harness what the item list is to the human workflow — **the source of truth of the scope**. From it derive:

- what initialization reads (Lesson 06);
- what verification compares against (Lesson 09 — "done" = feature in `passing`);
- what the handoff summarizes (Lesson 05);
- what telemetry measures (Lesson 11 — how long each feature took).

The feature list connects the harness to the **product**: without it, the harness is a process running empty.

## In AgEnFK: the same idea, with flow

AgEnFK generalizes the feature list into items with type (EPIC, STORY, TASK, BUG), hierarchy (parent/children), configurable per-flow status and an evidence trail. The factory's `feature_list.json` is the "file" version; AgEnFK items are the "system" version — with gates, comments and tests attached.

The lesson connecting the two: **the form doesn't matter (file, database, spreadsheet); the contract matters** — there is a queryable structure that says what to do, in what state and with what priority, and the whole harness operates on top of it.

## Feature lists for non-technical areas

This lesson extends to the course's multi-team model (EPIC E):

- **Finance**: the feature list is the list of reports to generate — each with state, data source and deadline; the overnight harness processes `in_progress` and publishes `passing` before the coffee.
- **Games**: the feature list is the game backlog — characters, narratives, mechanics; each with state up to publication on the platform.
- **Sales**: the feature list is the proposal/deck deliverables — with date, client and approval.

The structure is the same; the domain changes. That is why the feature list is a primitive: it is **domain-agnostic**.

## Key takeaways

1. Feature list = queryable source of truth of the scope: what, state, priority.
2. Explicit states (not_started → in_progress → blocked → passing) give semantics to the work.
3. One in_progress feature at a time is the focus rule.
4. The form (JSON, database, spreadsheet) is a detail; the contract is what matters.
5. The primitive scales to any domain — it is the foundation of the multi-team harness.

## Check your learning

```
"quiz me on Lesson 08"
```

**Next lesson**: [09 — Declaring victory too early](/lectures/lecture-09).
