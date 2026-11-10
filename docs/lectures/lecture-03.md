---
title: Lesson 03 — The repository as system of record
---

# Lesson 03 — The repository as system of record

> The truth of agentic work lives in the repository, not in the conversation.

## The problem: conversations are volatile

When an agent works with you, the conversation contains decisions, plans and "agreements". But the conversation:

- **disappears** when the session ends;
- **is not auditable** — nobody reviews what was said;
- **is not shareable** — another agent or person can't see the context;
- **has no authority** — nothing prevents the agent from diverging from what was agreed.

If the state of the work lives only in the conversation, the work has no state.

## The principle

> Every piece of knowledge, decision and work state that matters must live in the repository, as versioned files.

This applies to:

- **What to do** → `feature_list.json`, management framework items
- **How to do it** → AGENTS.md, policies, skills
- **What was done** → commits, reports, `progress.md`
- **Where it stopped** → `session-handoff.md`
- **What was decided** → comments, ADRs, docs

When the truth lives in the repo, the agent (and any future agent, from any tool) can rebuild the full context with a simple read — and the work becomes **reviewable in PR**, like any code.

## The system of record in our ecosystem

The `harness-factory` defines the hierarchy of state files:

| File | Role | Who reads it |
|---|---|---|
| `feature_list.json` | State of each feature (not_started, in_progress, blocked, passing) | The agent decides what to do |
| `progress.md` | Recent work, current work, failures, next action | The agent resumes the session |
| `session-handoff.md` | What is verified, what is broken, next step | The next agent/person |
| `AGENTS.md` | The permanent roadmap: what to read, how to verify, how to finish | Every agent that enters the repo |

Note the factory's requirement:

> "Git is the truth: verify hand-offs with `git status`/`git diff` and by re-running tests yourself; never trust narration."

That is the system of record at work: **narration is not evidence**; the repo is.

## In practice — the A1 case

In the first story of this project (A1 — course setup), the agent scaffolded VitePress and tried to mark the story as DONE. The gatekeeper **refused**: there is no direct transition to DONE — only via `validate_progress` with evidence. What unlocked it was not the word "done" in the conversation, it was:

1. the site build running and passing;
2. the test result recorded (`log-test PASSED`);
3. the evidence documented in the story comment.

All of this became **permanent record** in the repo history and in the workflow trail. The conversation would have been forgotten; the record was not.

## Why the repo and not the database?

A workflow engine may keep items in a database, and that is fine for aggregation — but it does not change where the truth lives: the harness state files stay **in each project's repo**, and the engine manages the flow on top of them. If deleting the engine would make the project lose information about itself, the state is in the wrong place. The practical rule:

- **Process and flow** → management framework (items, gates, telemetry)
- **Context and knowledge** → files in the repo (docs, skills, policies)
- **Evidence** → command output, builds, tests, generated reports

## Key takeaways

1. The conversation is volatile; the repo is permanent, auditable and shareable.
2. Work state (what, how, how much, where it stopped) lives in versioned files.
3. Narration is not evidence: verify in the repo, not in the conversation.
4. A multi-tool harness only works if the truth lives outside each tool.

## Check your learning

```
"quiz me on Lesson 03"
```

**Next lesson**: [04 — Why a single instructions file fails](/lectures/lecture-04).
