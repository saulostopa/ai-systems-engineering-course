---
title: Lesson 01 — Why capable agents still fail
---

# Lesson 01 — Why capable agents still fail

> The first question this course answers: if the models are so good, why do agents still get things wrong so often?

## The model is not the product

The language model solves the *cognitive* problem: it reasons, writes, reads and decides. But an agent that actually works needs much more than cognition. It needs:

- **To know what exists** — which files, which services, what the business rule is.
- **To know what to do** — which feature, in what order, with what definition of done.
- **To know when to stop** — how to verify it finished without declaring victory too early.
- **To remember where it was** — what was done when one session ends and another begins.

When one of these four is missing, the agent fails — even when it is "capable". And here is the key insight of this course:

> **The failure is almost never in the model. It is in the environment around it.**

## The thought experiment

Take the same person (or the same model) and put them in two environments:

1. **Environment A**: a desk with an unordered pile of papers, vague oral instructions, no definition of "done", no way to verify one's own work, and interruptions every 10 minutes.
2. **Environment B**: a desk with the goal written down, a delimited scope, organized materials, an acceptance checklist and a mirror to check the result.

The same person produces dramatically different results. The model is the same; the **harness** is what changes.

## At Webmotors

Our own course repository is a living example. In `harness-plannig`, the `.claude/CLAUDE.md`, the `AGENTS.md` and the AgEnFK `feature_list.json` are "Environment B" for the agent building the course with us. When the gatekeeper blocked story A1 from going to DONE without a build and evidence, it was correcting exactly the symptom of this lesson: **the agent felt ready; the environment demanded proof**.

And in `webmotors-harness-factory`, the same principle appears mechanized: pre-commit hooks that block, `scripts/validate-harness.sh` that verifies, `policies/definition-of-done.md` that defines acceptance. None of these files make the model smarter — they make the work more reliable.

## What a harness does (summary)

| Agent's need | What the harness provides |
|---|---|
| Know what exists | AGENTS.md, docs, feature_list, skills |
| Know what to do | Items/flows, declared scope, priority |
| Know when to stop | Definition of Done, tests, gatekeeper |
| Remember where it was | progress.md, session-handoff.md, state in the repo |

## Key takeaways

1. Agent = model + harness. The model reasons; the harness makes the work happen.
2. Agent errors are symptoms of the environment, not of intelligence.
3. The harness does not "improve" the model — it **constitutes the work system** in which the model operates.
4. Everything you will build in this course exists to answer: "how does the agent know, act, verify and remember?"

## Check your learning

Ask an agent to generate the quiz for this lesson with the `feature-quiz` skill:

```
"quiz me on Lesson 01 with the 4 levels"
```

If you don't have the skill installed yet, go back to the [Library](/resources/) and install the `harness-agent-skills` package.

**Next lesson**: [02 — What a harness really is](/lectures/lecture-02).
