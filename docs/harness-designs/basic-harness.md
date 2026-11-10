---
title: Basic harness (download)
---

# Basic harness (download)

> The installable control layer for a small repository. The runnable core is
> published in the [standalone harness catalog](https://github.com/saulostopa/ai-systems-engineering-harnesses/tree/main/harness-basic).

## Who it's for

Small and medium projects, teams of 1-5 people, without their own process
infrastructure. The basic harness delivers the minimum that changes agent
behavior: a short router, explicit state, scope/evidence policies, execution
plans and mechanical gates.

## Two distribution profiles

| Capability | Standalone core | Course standard distribution |
|---|---:|---:|
| Router, state and policies | yes | yes |
| Execution plans and delivery artifacts | yes | yes |
| Pre-commit/pre-push gates | yes | yes |
| Standard skills under `.agents/skills/` | no | seven bundled skills |
| Explicit in-place installation | separate target only | `./install.sh --self` |

The standalone repository remains the portable core. A derived distribution
may bundle the standard skills and manage its own package directory. Keeping
the profiles explicit prevents documentation from promising files or commands
that are not present in the selected distribution.

## Core package structure

```text
harness-basic/
├── package.json
├── install.sh                # copies the payload and activates hooks
├── templates/
│   ├── AGENTS.md             # router (Lesson 04)
│   ├── feature_list.json     # scope with state (Lesson 08)
│   ├── progress.md           # session diary (Lesson 05)
│   ├── session-handoff.md    # note between sessions (Lesson 05)
│   ├── exec-plan.md          # feature route with evidence (Lesson 13)
│   ├── policies/             # scope, Definition of Done, evidence
│   └── init.sh               # environment bootstrap (Lesson 06)
├── scripts/                  # health, gates, artifacts and skill scanning
├── tests/                    # mechanical gate tests
└── .githooks/
    ├── pre-commit
    └── pre-push
```

## Install the standalone core

From the root of the `harnesses` checkout:

```bash
./harness-basic/install.sh /absolute/path/to/project
cd /absolute/path/to/project
./init.sh
./scripts/validate-harness.sh
```

The target directory must exist. When it is a Git repository, the installer
sets `core.hooksPath=.githooks`. Existing paths are protected; `--force`
permits overwrites and must be followed by the harness health check.

## Install a derived distribution in itself

When the package directory is also the first repository it will manage, the
derived installer uses an explicit self-install contract:

```bash
git init                       # only when Git is not initialized yet
./install.sh --self
./init.sh
```

`--self` is intentionally different from `./install.sh .`: the explicit flag
is the confirmation that package and target are the same directory. The
standalone core installer expects a separate target; check the selected
distribution's README before using this mode.

## Standard course skills

The course standard distribution installs these skills in `.agents/skills/`:

| Skill | Responsibility |
|---|---|
| `feature-report` | Accessible report with evidence traced to commands and diffs |
| `feature-quiz` | Adaptive four-level quiz about the delivered feature |
| `feature-archify` | Validated diagram of the completed feature |
| `skill-guard` | Scan external skills before installation |
| `qa-playwright-e2e` | Resilient Playwright E2E coverage |
| `qa-perf-triage` | Concurrency and latency-regression diagnosis |
| `agentic-navigation` | Visual acceptance of a real application flow |

`feature-report` and `feature-quiz` share Eleanor assets in
`.agents/skills/assets/`. `feature-archify` is the course wrapper; rendering
also needs the third-party `archify` skill, installed only after
`skill-guard`. The E2E gate stays inactive until `.harness/config.yaml`
contains a `qa:` block.

## First feature checklist

1. Customize sections 1 and 7 of `AGENTS.md`.
2. Replace the examples in `feature_list.json`.
3. Mark exactly one feature `in_progress`.
4. Create its plan in `docs/exec-plans/active/`.
5. Run `./init.sh` and `./scripts/validate-harness.sh`.
6. Ask the agent to implement, test and record command → expected → actual.

## What the gates do

| Gate | When | Behavior |
|---|---|---|
| `pre-commit` | every commit | Requires exactly one feature `in_progress`; runs E2E policy when configured |
| `pre-push` | every push | Blocks missing files, invalid state, inconsistent plans or invalid skill records |
| `gate-skill-scan.sh` | before external skill installation | Runs the pinned static SkillSpector gate and records evidence |

## Natural evolution

| When | Evolve to |
|---|---|
| Several teams or repositories | [Enterprise harness](/harness-designs/enterprise-harness) |
| Application-specific QA | [App Harness](/harness-designs/app-harness) |
| Repository/business context retrieval | [RAG Harness & Area Copilots](/harness-designs/rag-harness) |
| Domain-specific knowledge | [Domain harnesses](/harness-designs/domain-harnesses) |

## Guarantee

No file is decorative: each one answers an agent question or enforces a
process boundary. If a file is not read, validated or used by a gate, it is
debt rather than rigor.
