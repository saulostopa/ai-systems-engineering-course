---
title: Lesson 10 — End-to-end tests change the outcome
---

# Lesson 10 — End-to-end tests change the outcome

> The agent that tests end-to-end delivers differently from the agent that tests "only what it touched".

## Why E2E changes the agent's behavior

It's not just about catching bugs. The most important effect of E2E is **on the behavior of the agent itself during implementation**:

- **Living specification**: the test describes the expected behavior precisely — the agent codes against a contract, not against an intuition.
- **Late feedback eliminated**: the error that would only show up in production appears in minutes.
- **Verifiable confidence**: the agent *knows* it finished because the full flow passed — not because it "seems".
- **Visible regression**: today's change breaks yesterday's flow immediately.

The E2E test transforms the harness from a "process that asks for verification" into a "process that verifies by itself".

## E2E as a mechanical gate

The `harness-factory` makes E2E **part of the commit contract**:

> "A frontend change without E2E coverage is blocked by the pre-commit hook (`scripts/frontend-qa-gate.sh`)."

In other words: it's not "don't forget to test" — it's "there is no frontend commit without a test". The `qa-playwright-e2e` skill supports this with quality discipline:

- semantic locators (`get_by_role`) instead of fragile CSS/XPath;
- Page Object Model;
- network interception for deterministic setups;
- failure triage via the trace viewer ("flaky" becomes evidence, not suspicion).

## Two worlds of verification

| | Unit test | E2E test |
|---|---|---|
| Answers | "does the function work?" | "can the user?" |
| Speed | ms | seconds/minutes |
| Cost | low | high |
| Feedback to the agent | part/piece | entire system |
| Is a commit gate? | not always | **yes, in our harness** |

The point of the lesson: the harness needs **both**, but it is E2E that closes the control loop — because it validates the whole world, not the part.

## The app harness and agentic navigation

This lesson is the gateway to the **App Harness** (EPIC C): beyond traditional E2E tests (the QA team), the app harness includes **agentic navigation** — the agent starts the app, opens the screen, navigates like a user and validates visually with the vision model. The two form the complete loop:

```
E2E (QA)          → the user flow is guaranteed by automated test
Agentic navigation → the agent sees and validates the real app, from build to acceptance
```

The e2e asks "does the flow work?"; agentic navigation asks "is the app acceptable?" — and both are gates.

## In practice — the real case

Our own ecosystem has the pattern in production: `harness-factory` blocks frontend commits without E2E; `harness-agent-skills` delivers the skill that writes and reviews those tests; the workflow records the result as a flow step (test PASSED before DONE). The entire course is built on this same loop — every lesson ends with verification, and the site only goes up if the build passes.

## Key takeaways

1. E2E changes the agent's behavior during implementation, not only in delivery.
2. Test as a mechanical gate (pre-commit) > test as intention.
3. Unit validates the part; E2E validates the world — both, always.
4. App Harness = QA E2E + agentic navigation with vision.

## Check your learning

```
"quiz me on Lesson 10"
```

**Next lesson**: [11 — Observability inside the harness](/lectures/lecture-11).
