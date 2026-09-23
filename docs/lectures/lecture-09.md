---
title: Lesson 09 — Declaring victory too early
---

# Lesson 09 — Declaring victory too early

> The agent says "done". The harness answers: "prove it".

## The pattern that repeats

The agent implements the feature, runs it once, sees that it "works" and declares victory. What it didn't verify:

- the edge cases (empty state, duplicate data, invalid payload);
- the existing tests (and the ones it broke);
- the full build (not just the snippet it touched);
- the effect on neighboring components (the factory calls this *neighbor effects*);
- the end-to-end integration (Lesson 10);
- the contract with hooks/gates (lint, format, e2e gate).

"It seems to work" is the most expensive form of "done" there is: the cost of finding out later is 10x the cost of verifying now.

## The mechanics of self-deception

The agent doesn't lie on purpose — it **completes the reasoning in its head** and confuses intention with result. Writing the code *produces* the feeling that the code works (the fluency bias). Against this, the harness offers a single reliable weapon: **mandatory external evidence**.

## Evidence before "done"

The `webmotors-harness-factory` turns this into policy (`policies/evidence-required.md`):

> "Completion requires recorded evidence: commands executed, expected vs. actual. Never claim 'done' without proof."

In practice, evidence is:

```
✓ build passed            (command output, not "it should pass")
✓ tests ran               (test names + counts, not "I tested")
✓ diff reviewed           (git diff: only the declared scope)
✓ gates passed            (pre-commit/pre-push hooks)
✓ artifacts generated     (report/quiz/diagram saved)
```

And the factory's subtle requirement:

> "Compare the test names before and after and confirm none were deleted, renamed, skipped or weakened — a green suite with fewer tests than you started with is a regression, not a pass."

## The flow as a teacher

A workflow that embodies this lesson has three properties:

1. advancing requires evidence with **mandatory exit criteria** per step;
2. the test is a separate step, recorded PASSED/FAILED;
3. **DONE is only reachable through the final step** — there is no "mark as done".

Story A1 went through this: the gate refused the direct DONE; the path was to run the build, record the test with the real command, and advance with evidence. "I declared victory" was converted into "I proved victory".

## The question that disarms self-deception

Before any "done", the harness asks four questions — and the answer is always an executed command, never a sentence:

| Question | Required answer |
|---|---|
| Is it built? | `build` with exit 0 (output attached) |
| Is it covered? | new tests + full suite passing, with no reduction |
| Is it in scope? | `git diff` showing only what was declared |
| Is it integrated? | E2E/gates/hooks passing |

## At Webmotors

- **Dev**: the "done" of a screen includes the `qa-playwright-e2e` e2e passing in the gate — not the agent's opinion.
- **QA**: flaky triage doesn't accept "must be the network flakiness" — it requires the trace viewer and test evidence.
- **Finance**: the overnight report is worthless without spreadsheet validation (expected vs. actual reconciled).
- **Games**: the platform build doesn't go up without publish validation.

## Key takeaways

1. "It seems to work" is the most expensive form of "done".
2. Intention ≠ result: mandatory external evidence breaks self-deception.
3. A green suite with fewer tests is a regression, not a pass.
4. "Done" is a state achieved through a flow with proof, not a word.

## Check your learning

```
"quiz me on Lesson 09"
```

**Next lesson**: [10 — End-to-end tests change the outcome](/lectures/lecture-10).
