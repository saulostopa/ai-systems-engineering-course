---
title: Lesson 06 — Initialization as its own phase
---

# Lesson 06 — Initialization as its own phase

> Before working, the agent needs to understand where it is. That is a phase — and it deserves a protocol.

## The classic mistake

The agent opens the repo and starts editing. The impression of productivity is misleading: without understanding the terrain, it:

- edits the wrong file (are there 3 similar repos?);
- follows patterns that don't exist in the project;
- breaks contracts (hooks, lint, format);
- repeats work another session already did.

**Boot is not wasted time — it is the phase that prevents rework.**

## Initialization as a protocol

The `harness-factory` defines the boot with `./init.sh`:

> "`init.sh` checks the working directory, validates the tools, runs the baseline validation and prints the recommended next commands. **Never starts long-running processes by default.**"

The healthy initialization sequence:

1. **Where am I?** — confirm the correct repo (the factory checks the working directory).
2. **What exists?** — read AGENTS.md/router, feature_list, architecture docs.
3. **Does the environment work?** — tooling present (node, python, gh), hooks installed (`git config core.hooksPath`), baseline validated.
4. **Where did we stop?** — session-handoff, progress, git status.
5. **What to do now?** — pick ONE feature in `in_progress` (never two).

## Why "one at a time" is part of the boot

The factory is explicit:

> "Only one feature can be `in_progress` at a time, unless an exception is documented. Pick the highest-priority `not_started` feature."

This is not bureaucracy: it is the protection against the agent that spreads work across ten fronts and finishes none (the symptom of Lesson 07).

## Initialization as a workflow phase

Once a project runs on a [workflow engine](/harness-designs/enterprise-harness), the boot stops being a checklist and becomes a phase of the flow: the engine reads the item, confirms the project, reads scope and architecture, **decomposes everything before any work**, and only then releases execution. Resolving the project means reading the `.harness/config.yaml` of the directory — the mechanical equivalent of "where am I?".

And the gatekeeper extends the boot into the middle of the session: on every edit, it checks whether the file is inside a managed project and whether there is an active item. **The agent cannot work "without knowing where it is"** — the harness remembers for it.

## In practice — the case of our scoping

When we scoped the workflow engine for this course, the "boot" was literally redone: we removed global rules, installed the rules **in the project** and verified that, inside `harness-plannig`, the project resolves and the workflow activates — and outside it, nothing. Correct initialization is what guarantees that every agent, in every repo, starts with the right harness.

## Boot checklist (copy to your project)

```sh
./init.sh            # or the equivalent of your harness
rtk git status       # clean tree? pending handoff?
rtk git log --oneline -5  # what was done recently?
# read: AGENTS.md, session-handoff.md, feature_list.json
# pick ONE in_progress feature (or promote the highest priority one)
# declare the scope BEFORE editing (policies/scope-control.md)
```

## Key takeaways

1. Boot is its own phase, not wasted time: it prevents rework and broken contracts.
2. Where am I → what exists → environment OK → where did we stop → what to do.
3. One in_progress feature at a time is protection against dispersion.
4. The harness must make "not knowing where you are" impossible (gatekeeper, project.json).

## Check your learning

```
"quiz me on Lesson 06"
```

**Next lesson**: [07 — Excessive autonomy and incomplete delivery](/lectures/lecture-07).
