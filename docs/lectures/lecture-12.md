---
title: Lesson 12 — Sessions end with clean state
---

# Lesson 12 — Sessions end with clean state

> The end of a session is the beginning of the next one. Ending dirty is sabotaging continuity.

## What "clean state" is

A session ends clean when the next session (agent or human) can resume without having to **undo** anything you did. Dirty state is the opposite: half-edited files, `in_progress` features nobody advanced, an outdated handoff, broken tests left behind.

The classic symptom: the next agent opens the repo, runs the tests, and they fail — and it spends the whole session discovering the failure wasn't its fault, it was the previous session's.

## The factory's shutdown protocol

The `webmotors-harness-factory` defines the end of session precisely (`AGENTS.md` §8):

1. Update `feature_list.json` — real states of the features.
2. Update `claude-progress.md` — what was done, what failed, next action.
3. Update `session-handoff.md` — required header sections.
4. Run `scripts/cleanup-scanner.sh` — detect drift and forgotten artifacts.
5. Run `scripts/validate-harness.sh` — **must pass**.
6. Follow `policies/git.md` — coherent commits, no junk.

Notice the symmetry with Lesson 06 (boot): **the boot starts by reading the handoff; the shutdown writes the handoff**. If everyone writes, everyone reads something reliable.

## What is truly clean

| Artifact | Clean state | Dirty state |
|---|---|---|
| Git tree | No purposeless uncommitted changes | Orphan files, half-done merges |
| Tests | Green and stable suite | Preexisting failures "left behind" |
| Features | One coherent `in_progress`, the rest `not_started`/`passing` | Ten `in_progress`, none advanced |
| Handoff | Says exactly where it stopped and what's next | Says what happened 3 sessions ago |
| Artifacts | Reports/quizzes generated and referenced | Orphan HTMLs with no owner |

## Shutdown as a contract

AgEnFK treats shutdown as part of the flow: the item only completes after the recorded test and evidence — and the transition between phases preserves state. When a session is paused, `agenfk-pause` saves the full context; when it resumes, `agenfk-resume` restores it — "clean state" becomes mechanical, not a habit.

And in practice in this project: the session that did the scoping ended with everything committed (clean working tree), pushed and with story A2 in a coherent `IN_PROGRESS` — the following session (this one, writing the lessons) started by reading the state and continued without rework.

## "Clean state" for domain areas

- **Finance**: the overnight harness ends by publishing the report and marking the spreadsheets as processed — if the morning starts with the report ready and the state consistent, the harness slept "clean".
- **Games**: the narrative creation session ends with the design doc committed and the item advanced — never with ideas only in the conversation.
- **Sales**: the proposal is saved and versioned, with the next step recorded.

## Key takeaways

1. Clean state is what allows resumption without rework — the opposite of "task completed".
2. Shutdown mirrors boot: whoever writes the handoff guarantees the reliable read of the next session.
3. Stable green suite, coherent tree and consistent features are the minimum.
4. Mechanical clean state (pause/resume, gates) > clean state as good intention.

## Check your learning

```
"quiz me on Lesson 12"
```

**Next lesson**: [13 — From manual prompts to autonomous loops](/lectures/lecture-13).
