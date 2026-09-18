---
title: Lesson 04 — Why a single instructions file fails
---

# Lesson 04 — Why a single instructions file fails

> The natural instinct is to pile everything into one giant AGENTS.md. It is the worst instinct there is.

## The temptation of the single file

It is seductive: a single file that says **everything** — context, rules, commands, policies, examples, reminders. A "complete manual". The problem is that this file fails on five fronts at once:

1. **Context cost**: every token in the file is paid for on every load. A 5,000-line file steals context from the real work.
2. **Contradiction**: long instructions contradict each other, and the agent follows the last one or the most specific one — unpredictable.
3. **Obsolescence**: nobody reviews a giant file; it rots in silence.
4. **Irrelevance**: 90% of the instructions do not apply to the current task, but the agent can't filter.
5. **Dilution**: what is critical (gate, verification) gets lost among what is decorative.

## The pattern that works: routing

Instead of a single manual, a short **router** points to specific documents, loaded on demand:

```
AGENTS.md (router — short, stable)
├── What this repo is
├── What to read first (links)
├── How to pick a task (feature_list.json)
├── How to verify (policies/definition-of-done.md)
└── Where the documentation lives (route table)
```

The agent loads the router, and then **fetches** the right page when it needs it — exactly like a person using a README, not like someone memorizing a bible.

## Evidence from our ecosystem

The `webmotors-harness-factory/AGENTS.md` is an exemplary router: 9 short sections, with a "Where deeper documentation lives" table pointing to `docs/architecture/`, `docs/operations/`, `skills/<name>/SKILL.md`, `policies/*.md`. No copied content — just routes.

`harness-agent-skills` follows the same pattern at the skill level: each skill is a short `SKILL.md` with frontmatter (`name` + `description`), and the body in `Gather → Write → Output`. The description is the loading trigger: the skill is only read **when the task matches** — on demand, not at boot.

And AgEnFK itself distributes rules per platform (`clauderules/`, `codexrules/`, `cursorrules/`, `geminirules/`) instead of a single universal file — each harness gets the format it understands.

## Practical rule: the 10% file

A well-formed instructions file should be cuttable to ~10% without losing any critical rule. If you need to read 300 lines to know how to verify the work, the roadmap is wrong.

| Symptom | Diagnosis |
|---|---|
| AGENTS.md over ~150 lines | Likely a bloated router; extract to docs/ |
| Instructions duplicated in 2+ places | Contradiction and divergence coming |
| "Remember to..." at the end of the file | An instruction that will be forgotten; turn it into a policy or skill |
| Manual table of contents | Sign that the file is already a book; break it up |

## At Webmotors — the course as an example

This course is a knowledge harness, and it follows the same principle: the home page and the section pages are **routers** (links to lessons, projects, library); each lesson is a small document with a single scope; each skill is a package loaded on demand. When the template library (A4) is delivered, the ready-made templates will follow the same format — short router + routed docs.

## Key takeaways

1. Giant single file = cost, contradiction, obsolescence, irrelevance, dilution.
2. Short router + on-demand documents is the pattern that scales.
3. Skills with a triggering `description` are the on-demand loading mechanism.
4. If you can't cut 90% of the file without losing a critical rule, the routing is wrong.

## Check your learning

```
"quiz me on Lesson 04"
```

**Next lesson**: [05 — Continuity in long-running tasks](/lectures/lecture-05).
