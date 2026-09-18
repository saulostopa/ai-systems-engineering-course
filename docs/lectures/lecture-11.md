---
title: Lesson 11 — Observability inside the harness
---

# Lesson 11 — Observability inside the harness

> If you don't measure the agent's work, you don't know whether the harness works.

## The trust paradox

The harness imposes gates, verification and evidence. But who verifies the **harness itself**? Who says the gates are working, the flow is flowing, the time per feature is dropping (or rising)?

Without observability, the harness is a black box that "seems to be helping". With observability, it is a system you **can improve with data**.

## What to observe

| Dimension | Question | Data source |
|---|---|---|
| Flow | How long does each item take per step? | Workflow timestamps |
| Friction | How many retries, loops, repeated commands? | Session logs, `log-friction` |
| Cost | How many tokens per feature? Per step? | Usage telemetry |
| Quality | How many tests failed before green? How many resumptions? | Flow test trail |
| Harness health | Are gates blocking as expected? Hooks running? | Health check, harness validation |

## The factory's `log-friction`

The `webmotors-harness-factory` has a dedicated skill: **`log-friction`** — it records every friction point in the flow (agent stuck, command looping, context overflow, gate blocking something wrong). The golden rule:

> "There is no 'the harness is good' — there is 'the harness is good *so far*'. Unrecorded friction is observability debt."

And the skill comes with a decision criterion we saw in `rag-harness.md`:

> "Reopen this proposal only if: (1) the harness is in real use; (2) `log-friction` shows real context-recovery pain; (3) the agents in use don't solve it natively."

In other words: **the decision to build was postponed for lack of evidence, and the evidence would come from observability.** This is the most strategic lesson of the course — it teaches deciding with data instead of intuition.

## Telemetry in AgEnFK

AgEnFK collects token, command and adoption events, with a dedicated database and a dashboard. The questions it answers in our project:

- How much did story A1 cost in tokens? (for the EPIC G benchmark)
- How long did each phase (plan → code → verify) take?
- How many times did the gatekeeper block, and was it correct?

These numbers feed the **harness health check** — the metric we will use in EPIC G (metrics and evidence) to prove the harness's value to the C-Level.

## Observability for each domain

The principle extends to the domain harnesses (EPIC E):

- **Finance**: the overnight harness records how many spreadsheets it processed, how many validations failed, how long it took — the morning report comes with *proof*.
- **Games**: how many simulated playtests ran, how many publish builds passed.
- **Sales**: how many decks generated, time per proposal.

## The improvement loop

```
measure → detect friction → adjust the harness → measure again
```

The harness is a product like any other: without observability, you improve by guesswork. With it, you improve by evidence — which is exactly the culture this course teaches applying to its own work.

## Key takeaways

1. Who verifies the verifier? Observability is the answer.
2. Measure flow, friction, cost, quality and harness health.
3. `log-friction`: unrecorded friction is observability debt.
4. Build/adopt decisions must come from evidence, not intuition.
5. Observability feeds the harness's continuous improvement loop.

## Check your learning

```
"quiz me on Lesson 11"
```

**Next lesson**: [12 — Sessions end with clean state](/lectures/lecture-12).
