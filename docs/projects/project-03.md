---
title: Project 03 — App Harness with QA
---

# Project 03 — App Harness with QA

> The harness that combines the QA team's E2E test with agentic navigation — the agent opening the app, navigating and validating with vision.

## Objective

Assemble the **App Harness** in two layers:

1. **QA layer** — E2E tests with Playwright as a mechanical gate (the `qa-playwright-e2e` skill from `harness-agent-skills`).
2. **Agentic layer** — the agent starts the app, navigates like a user and validates visually (screenshots + vision model), from build to acceptance.

It is EPIC C of the course — here you build a functional version of it.

## Prerequisites

- An app (can be a team app repo or a test app) with `npm run dev`/build working.
- Playwright installed (the skill uses Python + Playwright).
- An agent with vision capability (Claude, GPT-4o, Gemini).

## Step by step

### Layer 1 — E2E as a gate

1. Install the `qa-playwright-e2e` skill (see the [Library](/resources/) for the install command).
2. Ask the agent:

```
"write the E2E tests for this screen with Playwright"
```

3. Require the skill's standards:
   - semantic locators (`get_by_role`) — never fragile CSS/XPath;
   - Page Object Model;
   - network interception for deterministic setups;
   - tests that genuinely fail if the screen breaks.

4. Make E2E a commit gate:

```bash
# pre-commit (simplified example)
#!/bin/bash
# runs E2E for changed frontend files
if git diff --cached --name-only | grep -qE '^src/.*\.(tsx|vue|jsx)$'; then
  pytest tests/e2e -q || { echo "E2E failed — commit blocked"; exit 1; }
fi
```

### Layer 2 — Agentic navigation with vision

1. Start the app: `npm run dev` (or build + preview).
2. Give the agent the navigation mission:

```
"start the app, navigate to screen X like a user and validate:
 1. the complete flow works;
 2. there is no visual breakage (layout, overlap, infinite loading);
 3. the empty and error states are acceptable.
 Take screenshots as evidence and tell me what you found."
```

3. The agent must produce **visual evidence** (screenshots) + verdict per criterion.
4. Learn from what it finds: each finding becomes a new E2E test in Layer 1 — **the loop closes**: agentic navigation finds, E2E immortalizes.

## The complete loop

```
build → E2E (gate) → agentic navigation (vision) → findings → new E2E tests → ...
```

The app harness is not "QA or agent" — it is **QA and agent**, each catching what the other doesn't: E2E is deterministic and cheap; agentic navigation is exploratory and sees what the test doesn't predict.

## Verification

- A frontend change **without** an E2E test is blocked by the hook.
- Agentic navigation produces screenshots + verdict per criterion (accepted/rejected).
- At least 1 navigation finding became a new E2E test.

## Deliverable

The working E2E hook in the repo + the E2E tests + the record of an agentic navigation round with screenshots and verdicts.

::: tip Status
The official version with failure triage, perf and full integration is **EPIC C** of the course.
:::

**Next project**: [04 — Domain harness](/projects/project-04).
