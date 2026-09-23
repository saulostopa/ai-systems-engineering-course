---
title: Basic harness (download)
---

# Basic harness (download)

> The package any small project downloads and runs in minutes. Versioned in
> `harness-basic/` at the root of this repository.

## Who it's for

Small and medium projects, teams of 1-5 people, without their own process
infrastructure. The basic harness delivers **the minimum that changes the agent's
behavior**: router, state, policies and two mechanical gates.

## What the package contains

```
harness-basic/
├── package.json              # metadata (private npm)
├── install.sh                # installer: copies everything + activates hooks
├── templates/                # the harness files (same base as A4)
│   ├── AGENTS.md             # router (Lesson 04)
│   ├── feature_list.json     # scope with state (Lesson 08)
│   ├── progress.md           # session diary (Lesson 05)
│   ├── session-handoff.md    # note between sessions (Lesson 05)
│   ├── policies/             # scope-control, definition-of-done, evidence
│   └── init.sh               # boot (Lesson 06)
├── scripts/
│   ├── gatekeeper.sh         # pre-commit: requires ONE in_progress feature
│   ├── validate-harness.sh   # full harness health check (Lesson 11)
│   └── log-event.sh          # friction logging (Lesson 11)
└── .githooks/
    ├── pre-commit            # runs gatekeeper.sh
    └── pre-push              # runs validate-harness.sh
```

## Installation

```sh
git clone <this repo>              # or copy the harness-basic/ folder
cd <your-project>                  # existing git repo
./harness-basic/install.sh <your-project>
./init.sh                          # validates the environment and prints next steps
```

The installer:
1. copies templates, scripts and hooks;
2. activates `git config core.hooksPath .githooks`;
3. refuses to overwrite existing files (use `--force` consciously).

## What the gates do (tested)

| Gate | When | Behavior |
|---|---|---|
| `pre-commit` (gatekeeper.sh) | every commit | **Blocks** if 0 features `in_progress` (Lesson 08) or >1 (Lesson 06/07); conscious 5-min bypass via `.harness/skip-gatekeeper` |
| `pre-push` (validate-harness.sh) | every push | Blocks if required files are missing, JSON is invalid, states are wrong or >1 `in_progress` |

The `validate-harness.sh` is the Lesson 11 "health check": 0 failures = healthy harness;
any failure = the harness broke and the push is blocked **before** publishing.

## Natural evolution

| When | Evolve to |
|---|---|
| Team grew, several teams in the same repo | [Enterprise harness (multi-team)](/harness-designs/enterprise-harness) — B2 |
| App with QA | [App Harness](/harness-designs/app-harness) — C |
| Area business context | [RAG Harness & Area Copilots](/harness-designs/rag-harness) — D |
| Specific domain (games/finance/sales) | [Domain harnesses](/harness-designs/domain-harnesses) — E |

## Guarantee

No file is decorative: each one answers an agent question (what, how, when to
stop, where it was) or a process gate (scope, done, evidence). A bloated harness
folder is debt, not rigor.
