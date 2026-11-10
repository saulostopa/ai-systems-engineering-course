---
title: Project 07 — Enterprise harness (multi-team)
---

# Project 06 — Enterprise harness (multi-team)

> Install one orchestrator on your machine, adopt two repositories with it, and get a single view over both — without a single byte of project state leaving the repositories.

## Objective

Everything up to Project 05 lives inside one repository. This project is the
step where a **team of teams** becomes manageable: a shared flow, a gate that
runs the same way everywhere, and one report that reads across projects.

The trap to avoid is the obvious solution. The reflex is to put items, comments
and evidence in a central database — and the moment you do, the project stops
being able to explain itself. Delete the tool and the history is gone. The
[enterprise harness blueprint](/harness-designs/enterprise-harness) exists to
make the other choice concrete.

## The two layers

```
~/wm/                          ← the root that holds your projects
├── wm-harness/                ← A · orchestrator, installed once per machine
│   ├── bin/wm-harness           the CLI
│   ├── flows/                   flow definitions shared by the organization
│   └── harness-basic/           vendored layers 1-2 payload
├── catalogo/                  ← B · adopted repository
│   ├── .harness/config.yaml     13 lines: which flow, which engine version
│   └── docs/exec-plans/{active,done}
└── fipe/                      ← B · another one
```

The rule that decides where anything goes:

> **The orchestrator owns the *how*. The repository owns the *what* and the
> *what happened*.**

And the test for the cases you are unsure about:

> **If deleting the orchestrator would make a project lose information about
> itself, the piece is in the wrong layer.**

## Step by step

### 1. Install the orchestrator

It belongs **above** your project folders, because that is the directory it
scans:

```sh
cd enterprise-harness
./install.sh --prefix ~/wm/wm-harness --projects ~/wm
export PATH="$HOME/wm/wm-harness/bin:$PATH"
wm-harness doctor
```

`doctor` prints where it lives, which directory it scans, and how many
repositories it found. Zero, for now.

### 2. Adopt two repositories

Use two real small repos — or two throwaway ones, which is enough to see the
mechanism:

```sh
wm-harness adopt ~/wm/catalogo
wm-harness adopt ~/wm/fipe --flow hotfix
wm-harness list
```

Now open `~/wm/catalogo` and look at what actually landed. The skeleton, the
policies, the hooks, `docs/exec-plans/{active,done}` — and `.harness/config.yaml`,
which is the entire binding to the orchestrator. **No engine, no
`node_modules`, no database.**

### 3. Run a feature under a flow

```sh
cd ~/wm/catalogo
wm-harness plan new feature/OEM-123 "Email validation"
cat docs/exec-plans/active/feature-OEM-123.md
```

The id follows the product team branch convention — `feature/OEM-123`,
`bugfix/AC-455`, `release/EST-3445` — so the plan and the branch carry the same
name. On disk the slash is flattened to `feature-OEM-123.md`.

Read the steps and the exit criteria that appeared: they were **copied out of
the flow**. That is what separates a flow definition from a document nobody
opens — it produced the checklist you are about to work through.

Do the feature for real. Then try to archive it before filling in the evidence:

```sh
wm-harness plan done feature/OEM-123
```

It refuses. Fill in the Evidence table with a real command and its real output,
then run it again — it rewrites the status and moves the file to `done/`.

### 4. Look across both projects

```sh
wm-harness status
wm-harness check
wm-harness report
```

`check` does not carry a second copy of the rules: it runs
`scripts/validate-harness.sh` **inside each repository**. The gates a team
already trusts are the gates the organization sees.

### 5. Prove the invariant

This is the step that makes the project worth doing:

```sh
rm -rf ~/wm/wm-harness          # delete the whole orchestrator
cd ~/wm/catalogo
cat docs/exec-plans/done/feature-OEM-123.md   # the evidence is still here
bash scripts/validate-harness.sh     # the repo still validates itself
```

Nothing was lost. Reinstalling the orchestrator picks both repositories back up
by scanning — there is no registry to restore, because there was never one.

## Verification

- `wm-harness doctor` ends with `ORCHESTRATOR OK`.
- An adopted repo contains `.harness/config.yaml` and **no** orchestrator machinery.
- A plan created by `plan new` carries the steps of the flow the repo declared.
- `plan done` refuses a plan whose evidence rows are still `_pending_`.
- `check` fails a repository whose declared flow no longer exists.
- After deleting the orchestrator, every adopted repo still passes its own gate.

## Deliverable

Two adopted repositories, one feature closed with evidence in
`docs/exec-plans/done/`, and the output of `wm-harness report` showing both —
plus your written answer to: *which piece of this would you have put in a
central database, and what would it have cost you?*

::: tip The official package
`enterprise-harness/` in this repository is the reference implementation, with
`scripts/validate-enterprise-harness.sh` and 19 end-to-end tests — including one
that deletes the orchestrator and asserts the projects survive. Read the tests
before the code: they state the contract more plainly than the prose does.
:::

::: warning Where this stops
The orchestrator aggregates with a CLI report, computed live. It has no UI, no
server and no cross-machine sync — two developers see the same numbers because
they read the same repositories. If your organization needs a Kanban and
telemetry dashboards, that is a layer 3-4 engine on top, and the blueprint lists
the options.
:::

**Previous project**: [05 — Area Copilot with RAG](/projects/project-05) ·
**Blueprint**: [Enterprise harness](/harness-designs/enterprise-harness)

**You finished the projects!** Review the [Lessons](/lectures/) or explore the [Harness Designs](/harness-designs/) to see where each piece fits in the complete plan.
