---
title: Lesson 13 — From manual prompts to autonomous loops
---

# Lesson 13 — From manual prompts to autonomous loops

> The quality leap doesn't come from better prompts; it comes from loops that self-correct.

## From prompt to loop

**Prompting** is a conversation: you speak, the model responds, you speak again. The agent doesn't act — it emits text.

**Loop engineering** is a cycle: the agent **acts** (edits, runs, tests), **observes** the result (exit codes, outputs, diffs) and **decides** the next step — repeating until the exit criterion.

```
PROMPT:   human → model → text → human → model → ...
LOOP:     human → agent → action → observation → decision → action → ... → exit criterion
```

The prompt asks; the loop **works**. The harness is what makes the loop safe: without gates and verification, an autonomous loop is an avalanche.

## The four components of a safe loop

1. **Action** — the agent executes tools (edit, build, test, git). The harness controls which.
2. **Observation** — the agent reads the real result (exit code, output, diff, test). The harness ensures it doesn't skip this step.
3. **Decision** — the agent decides the next step based on what was observed (fix, continue, stop).
4. **Exit criterion** — the verifiable condition that ends the loop. The harness enforces it (Definition of Done, gates).

Without component 4, the loop doesn't end or ends too early — which ties together Lessons 07 and 09.

## Loop vs. multi-loop flow

An agent can run a single loop: do → verify → repeat. But a real harness orchestrates **several loops in sequence**, each with its own criterion:

```
scope loop      → understand what to do (boot, reading, decomposition)
code loop       → implement until build+tests pass
review loop     → review the diff until the gates pass
evidence loop   → generate artifacts until the report/quiz close
```

Each loop has its own tools, its own gates and a verifiable output. The harness defines **when one loop ends and the next begins** — that is what Lesson 14 formalizes as graphs.

## In our ecosystem

- **AgEnFK**: each flow phase (plan → code → test → review → close) is a loop with an exit criterion — `verify` requires evidence to *advance* the item, not just "continue".
- **Factory**: `init.sh` is the scope loop; the pre-commit hooks close the code loop; `pr-hook.sh` closes the delivery loop.
- **Artifact skills**: `feature-report` runs the evidence loop — read the diff/tests, synthesize, generate the HTML.

And the entire course is a loop: each lesson ends with the quiz (observation), and the reader decides the next step (decision).

## Autonomous loops in domains

- **Finance**: the overnight harness runs the report loop: read spreadsheets → validate → process → publish → record. No human until the coffee.
- **Games**: the simulated playtest loop: generate variations → simulate → measure engagement → iterate.
- **Sales**: the proposal loop: read briefing + CRM → draft → validate against requirements → finalize.

The same loop skeleton — what changes are the actions and the exit criteria.

## Key takeaways

1. The prompt asks; the loop works. The leap is from conversation to action cycle.
2. Action, observation, decision and exit criterion are the four components.
3. The harness makes the loop safe: without gates, autonomy is an avalanche.
4. A complete flow is a sequence of loops, each with its own verifiable output.

## Check your learning

```
"quiz me on Lesson 13"
```

**Next lesson**: [14 — From single loops to graph engineering](/lectures/lecture-14).
