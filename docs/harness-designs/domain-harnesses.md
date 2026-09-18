---
title: Domain harnesses (multi-team)
---

# Domain harnesses (multi-team)

> One skeleton, N playbooks. The harness doesn't change between domains — only the
> knowledge (skills) and the domain-specific verification. Games, finance,
> sales and whatever comes next.

## The principle (EPIC E)

The domain harness is the application of the multi-team model:

```
domain harness = multi-domain skeleton (E1)
               + domain skills (E2/E3/E4, on-demand SKILL.md)
               + domain feature list
               + own verification (domain definition-of-done)
               + artifacts with cited sources (artifact skills)
```

The skeleton is **identical** for all — that is what allows a single learning
curve and a single governance (EPIC B2) for completely different
areas.

## The factory (E1 — `domains/factory/new-playbook.sh`)

Generates the skeleton of a new playbook in seconds:

```sh
./domains/factory/new-playbook.sh <domain>
domains/<domain>/
├── AGENTS.md                  # domain router (process = same for all)
├── feature_list.json          # domain deliverables with state
├── policies/                  # scope, DoD, evidence
├── skills/                    # filled by the domain (E2/E3/E4)
└── scripts/validate-playbook.sh  # playbook health (Lesson 11)
```

The `validate-playbook.sh` requires the mandatory structure + **at least one skill**
+ valid JSON with at most 1 feature `in_progress`. A playbook without skills is
a broken playbook — knowledge is what differentiates domains, not process.

## The delivered playbooks

| Domain | Skills | Own verification | Artifact |
|---|---|---|---|
| [Games](/harness-designs/domain-harnesses) (E2) | game-design, roblox-publish | simulated playtest + publish validation | feature design doc |
| [Finance](/harness-designs/domain-harnesses) (E3) | spreadsheet-analysis, report-generation | expected vs. actual reconciliation | published report (overnight) |
| [Sales](/harness-designs/domain-harnesses) (E4) | deck-generation, proposal-workflow | check against briefing + cross-review | versioned deck/proposal |

## Shared golden rule

From the Area Copilot (D3) to all domains: **every artifact cites its source**.
A report number without `SOURCE: <file> (lines X-Y)` doesn't exist. The
playbook is the same — the honesty with data too.

## How to create a new domain (recipe)

1. `./domains/factory/new-playbook.sh <name>` — ready skeleton.
2. Write 2-3 skills in `skills/<name>/SKILL.md` (frontmatter + Gather/Write/Output).
3. Fill `feature_list.json` with the domain's real deliverables.
4. Define the domain's "done" in `policies/definition-of-done.md`.
5. `scripts/validate-playbook.sh` — must finish with `PLAYBOOK OK`.

**Related**: [Enterprise harness](/harness-designs/enterprise-harness) · [RAG Harness](/harness-designs/rag-harness) · [Project 04](/projects/project-04)
