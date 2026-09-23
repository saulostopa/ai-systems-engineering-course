---
title: Lesson 07 — Excessive autonomy and incomplete delivery
---

# Lesson 07 — Excessive autonomy and incomplete delivery

> The agent does too much, delivers too little, and notices neither.

## The agent paradox

Give an agent total autonomy and watch the pattern that repeats:

- **Overreach**: it improves what wasn't asked, refactors what didn't need it, "takes the chance" to fix ten things.
- **Under-finish**: it considers done what is half-finished — the test is missing, the doc is missing, the build wasn't run, the e2e is missing.

Both sides are the same mistake: **autonomy without limits is not power, it is loss of control**. The agent decides the scope and decides "done" — and it is terrible at both judgments.

## The antidote: declared scope and mechanical verification

### 1. Declare the scope before editing

The `webmotors-harness-factory` requires (via `policies/scope-control.md`):

> "Record your scope before implementing: **What am I changing? Why? Which files are expected? What is explicitly out of scope? How will success be verified?**"

Declaring the scope beforehand is not formality: it is the **contract** between the agent and the gate. With the scope written down, "done" stops being an opinion and becomes a comparison: did it deliver what it declared?

### 2. Enforce mechanical gates, not intentions

The factory mechanizes:

| Gate | Mechanism | When it blocks |
|---|---|---|
| Gate check | `scripts/gatekeeper.sh` (pre-commit hook) | Any edit outside the allowed flow |
| Frontend QA | `scripts/frontend-qa-gate.sh` (pre-commit) | Frontend change without E2E coverage |
| PR | `scripts/pr-hook.sh` (pre-push) | Push without PR report |

The rule is: **if the process depends on the agent's goodwill, it won't happen**. What exists as a script and hook always happens.

### 3. Define "done" as a verifiable criterion

`policies/definition-of-done.md` + `policies/evidence-required.md`:

> "Completion requires recorded evidence (commands executed, expected vs. actual). Never claim 'done' without proof."

## The gatekeeper as a living example

A workflow engine takes this to the process level. The three rules that matter, whatever implements them:

- **Mandatory active item**: edits outside an in-progress item are blocked by the gatekeeper.
- **DONE unreachable by shortcut**: there is no direct transition to DONE — only through the final step of the flow, with evidence.
- **Test as a step**: the item goes through a test state (recorded PASSED/FAILED) before completing.

We saw this in practice in story A1: the agent tried to mark DONE and the workflow **refused** — the response was to move to the correct flow, run the build, record the test and only then complete. The overreach ("I finished") was intercepted by the harness, not by common sense.

## Time scope counts too

Excessive autonomy is also **when** the agent acts. That is why the harness defines:

- at which stage it can act (flow steps);
- what it can do without asking (allowed tools, expected files);
- what requires human approval (deploys, merges, scope changes);
- what is forbidden (outside the declared scope, editing files unrelated to the feature).

## At Webmotors — the spirit, not the letter

The goal of the harness is not to stiffen — it is to give **freedom within known limits**. The QA team gains E2E gates that protect the app; the finance team gains spreadsheet validation before the report goes up; the games team gains publish validation before shipping the build to the platform. Each area declares what is "too much" and what is "half-finished" — and the harness prevents both.

## Key takeaways

1. Overreach and under-finish are the same defect: scope and "done" without a contract.
2. Scope declared before editing = verifiable delivery contract.
3. Mechanical gate > intention: if it's not a script/hook, it doesn't happen.
4. "Done" is a flow state, not a word in the conversation.

## Check your learning

```
"quiz me on Lesson 07"
```

**Next lesson**: [08 — Feature lists as harness primitives](/lectures/lecture-08).
