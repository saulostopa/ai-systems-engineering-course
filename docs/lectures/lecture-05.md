---
title: Lesson 05 — Continuity in long-running tasks
---

# Lesson 05 — Continuity in long-running tasks

> Engineering tasks last days. Agent sessions last minutes. The harness is the bridge.

## The fundamental problem

An agent has a limited context window and a finite session. A real feature — from scope to deploy — spans:

- multiple sessions of the same agent;
- multiple agents (planning, coding, review, testing);
- multiple calendar days (with the agent's "mind" off in between).

Without persistent state, each session starts from scratch: the agent re-reads everything, re-decides what was already decided, and the work oscillates.

## State between sessions: the harness trio

The `webmotors-harness-factory` solves this with three complementary files:

```
feature_list.json      → WHAT exists and in what state (scope source of truth)
progress.md            → what happened in THIS session (recent work, failures, next action)
session-handoff.md     → what stays FOR the next session (verified, broken, next step)
```

The division of roles is what matters:

- **feature_list** is the *map* — changes little, it is the truth of the scope.
- **progress** is the *diary* — changes every session, documents the path.
- **handoff** is the *note* — the summary that lets the next session (agent or human) resume without re-reading everything.

## Resumption as a protocol

A good resumption follows a fixed protocol — and the harness turns it into a habit:

1. **Read the handoff** before touching any file.
2. **Re-verify** what the handoff claims (git status, tests) — never trust narration.
3. **Update the progress** with the real work of the current session.
4. **Update the handoff** before closing: what remained verified, what broke, what the next action is.
5. **Update the feature_list** with the real state of the features.

## At Webmotors — continuity in practice

A workflow engine formalizes this protocol on top of the repo: each story carries status, comments with evidence and a test trail. When the agent resumes story A2, it doesn't ask "where did we stop?" — it reads the story, the comments and the state, and continues. The file-based triad above does the same job with no engine at all; what matters is that the record is in the repository.

In practice this week: story A1 was completed in one session; the evidence (build OK, test PASSED) was recorded; when we resumed, the state was intact with no previous conversation in memory. **Continuity did not come from the agent's memory — it came from the harness.**

## What does NOT work

| Strategy | Why it fails |
|---|---|
| "Keep the conversation open" | Context window runs out; session drops; memory dies |
| Re-describing the context in every prompt | Cost, human error, divergence |
| Trusting that the agent "remembers" | There is no memory between sessions — only what is in the repo |
| Handoff in the head (not written) | Forgetting and noise guaranteed |

## Key takeaways

1. Long task ≠ long session: the work outlasts any context window.
2. Map (feature_list) + diary (progress) + note (handoff) cover the lifecycle.
3. Resuming is a protocol, not a guess: read, re-verify, update.
4. Continuity is a property of the harness, not of the model.

## Check your learning

```
"quiz me on Lesson 05"
```

**Next lesson**: [06 — Initialization as its own phase](/lectures/lecture-06).
