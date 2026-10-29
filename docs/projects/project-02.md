---
title: Project 02 — Installable basic harness
---

# Project 02 — Installable basic harness

> Package the minimal harness from Project 01 into something any small project downloads and runs in 5 minutes.

## Objective

Build the **basic harness package**: an installer that delivers AGENTS.md
(router), feature state, progress/handoff, essential policies, execution plans
and mechanical validation to any small repository. The course standard profile
also bundles seven reusable skills under `.agents/skills/`.

This is literally Story **B1** of our plan — and this project teaches you to build it before the course delivers the official one.

## Package structure

```
harness-basico/
├── init.sh                    # validates environment, prints next steps
├── AGENTS.md                  # short router (Lesson 04)
├── feature_list.json          # scope source of truth (Lesson 08)
├── progress.md                # session diary (Lesson 05)
├── session-handoff.md         # note for the next session (Lesson 05)
├── policies/
│   ├── scope-control.md       # scope before editing (Lesson 07)
│   ├── definition-of-done.md  # verifiable "done" (Lesson 09)
│   └── evidence-required.md   # evidence before "done" (Lesson 09)
├── scripts/                   # validation, gates, artifacts and skill scan
├── .githooks/                 # pre-commit and pre-push enforcement
└── .agents/skills/            # standard profile (seven course skills)
```

## Step by step

### 1. Write the `init.sh`

The `webmotors-harness-factory`'s `init.sh` is the model:

```bash
#!/bin/bash
# init.sh — initializes the basic harness in a project
set -e
echo "Checking directory..."
[ -f "AGENTS.md" ] || echo "⚠️  AGENTS.md missing — copy the package to the root"
node --version && npm --version
echo "Next steps:"
echo "  1. Read AGENTS.md"
echo "  2. Pick ONE feature in feature_list.json"
echo "  3. Run the project tests"
```

### 2. Write the policies (2-5 lines each)

`definition-of-done.md`:

```markdown
# Definition of Done
A feature is done when:
1. The build passes (output attached).
2. The tests pass, with no reduction in the suite.
3. The diff contains only the declared scope.
4. The evidence is recorded (command + result).
```

### 3. Add the state files

Use the [Library](/resources/templates) templates: `feature_list.json` with 3-5 example features, `progress.md` and `session-handoff.md` with the required headers (Lesson 05).

### 4. Install in a real repo

Use an explicit target instead of copying files by hand:

```bash
./install.sh /absolute/path/to/project
cd /absolute/path/to/project
./init.sh
./scripts/validate-harness.sh
```

The installer must protect existing files and require `--force` for a
conscious replacement. When the target is a Git repository it configures
`core.hooksPath=.githooks`.

### 5. Support an explicit self-install mode in derived packages

If the package directory itself will be managed by the harness, make the
intent explicit:

```bash
git init
./install.sh --self
```

Never make `./install.sh .` silently overwrite package state. `--self` is the
separate contract for a derived distribution; the standalone core can keep
requiring another target.

### 6. Bundle the standard skill profile

Install these under `.agents/skills/`: `feature-report`, `feature-quiz`,
`feature-archify`, `skill-guard`, `qa-playwright-e2e`, `qa-perf-triage` and
`agentic-navigation`. Keep shared Eleanor assets under
`.agents/skills/assets/` and validate that every skill has a `SKILL.md` with
matching frontmatter.

## Verification

- `./init.sh` runs without errors and prints the next steps.
- `./scripts/validate-harness.sh` validates the core and all seven standard skills.
- A clean install, overwrite refusal and `--force` reinstall are covered by tests.
- A derived package's `--self` mode is tested separately from normal installation.
- A fresh agent, with no context, can: read the AGENTS.md → pick the feature → implement → prove (build+test) → update the states.
- The handoff written by one session lets another resume without asking anything.

## Deliverable

Your package versioned in a repository, installer tests, the standard skill
profile (when selected) and evidence from the first feature executed with it.

::: tip Status
The official package, with complete hook scripts and validation, is Story **B1** of the course (EPIC B). This project gives you the foundation to review the official one with a critical eye.
:::

**Next project**: [03 — App Harness with QA](/projects/project-03).
