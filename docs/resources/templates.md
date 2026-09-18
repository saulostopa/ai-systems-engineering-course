# Templates

**Ready-to-copy** templates — the basic harness package, versioned at the
root of this repository in `templates/`.

## Installation

```sh
cp -r templates/ <your-project>/
cd <your-project>
./init.sh          # validates the environment and prints the next steps
```

## Package contents

| File | Role | Related lesson |
|---|---|---|
| [`AGENTS.md`](https://github.com/svslwm/harness-plannig/tree/develop/templates/AGENTS.md) | Router: what to read, how to choose, how to verify, how to finish | 04 |
| `feature_list.json` | Scope source of truth (state per feature) | 08 |
| `claude-progress.md` | Current session diary | 05 |
| `session-handoff.md` | Note for the next session (required header) | 05 |
| `policies/scope-control.md` | Scope declared before editing | 07 |
| `policies/definition-of-done.md` | Verifiable "done" criteria | 09 |
| `policies/evidence-required.md` | Evidence format (command → expected → actual) | 09 |
| `init.sh` | Environment initialization | 06 |
| `README.md` | Installation and customization instructions | — |

Each file comes with comments on where to customize and the reference to the lesson
that underpins it.

## How to use in the course

1. **Project 02** builds a package like this from scratch — compare yours with the official one.
2. **Project 04** adds the domain (own skills) on top of this skeleton.
3. **Project 05** adds the area context on top of it.

::: tip Status
This package is the deliverable of Story **A4** of the course. The package with complete
mechanical gates (hooks) is Story **B1** (EPIC B).
:::
