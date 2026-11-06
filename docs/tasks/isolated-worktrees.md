---
title: Feature — isolated worktree workflow
---

# Feature — isolated worktree workflow

Status: **in_progress** · Priority: **P0** · Scope: course, `harness-basic` and `adk-rag-postgres-harness`

## Decision

Make isolated Git worktrees the standard execution boundary for parallel agent
work. The main checkout is reserved for integration. Each feature receives its
own worktree and branch, and integration happens in a detached worktree created
from the current integration ref.

The course documents the provider-neutral contract. `harness-basic` installs the
contract through its generated `AGENTS.md` and policy files. The PostgreSQL RAG
harness adds the extra rule that an indexed repository and its database service
must be tied to a known revision and kept separate from the checkout receiving
updates.

## Contract

### Feature worktree

```bash
git fetch origin
git worktree add ../wt-<feature-id> -b feature/<id> origin/develop
cd ../wt-<feature-id>
```

Each worktree owns its dependency installation, caches and build outputs. Real
`.env*` files must never be copied into a worktree.

### Integration worktree

```bash
git fetch origin
git worktree add --detach ../wt-integrate origin/develop
git -C ../wt-integrate merge --no-ff feature/<id>
cd ../wt-integrate
<build and test commands>
git push origin HEAD:refs/heads/develop
```

If the branch or remote diverges, the agent stops and asks the repository owner.

### Fixed service worktree

```bash
git worktree add --detach ../wt-service <known-sha>
cd ../wt-service
<start the service with explicit test configuration and a synthetic database>
```

The service must read this pinned checkout and must not follow a different
worktree that is receiving updates.

### Cleanup and prohibited commands

```bash
git worktree list
git worktree remove ../wt-<feature-id>
git worktree prune
```

Remove orphaned worktrees without `--force`; reserve `--force` for temporary
local CI worktrees. The same branch cannot be checked out in two worktrees.

Agents must not run `reset --hard`, force pushes, `checkout -B`, `switch -C`,
`branch -f/-D`, `worktree add -B`, `clean -f`, `stash drop/clear`, rebase or
amend of a published commit. A divergence is a stop-and-ask condition.

## Implementation slices

1. Add this contract in English and Portuguese to the course backlog.
2. Add the generated Basic harness policy and router section.
3. Add the PostgreSQL RAG worktree and pinned-service section.
4. Add the provider-neutral `git-safe` command guard and pre-push fast-forward
   guard to the Basic distribution and the PostgreSQL RAG harness.
5. Validate that the current checkouts were not modified and that the new files
   contain no secrets or environment values.
6. Run the relevant structural tests in each isolated implementation worktree.

## Acceptance criteria

- A new Basic harness installs worktree instructions through its templates.
- The Basic instructions cover feature, integration and service worktrees.
- The PostgreSQL RAG README explains indexed-folder isolation and a pinned
  service database.
- Both harnesses document cleanup, branch uniqueness and the destructive Git
  command prohibition.
- The Basic and PostgreSQL RAG distributions mechanically reject destructive
  commands through `git-safe`, and their pre-push hooks reject ref deletion and
  non-fast-forward updates.
- The course links the contract to both project harnesses.
- No `.env*` value is read, copied or committed.
- The implementation remains confined to documentation and harness policies.

## Out of scope

- Automatically creating worktrees for every agent invocation.
- A provider-specific deny list that only works in one coding agent.
- Changing application code, database schema or runtime behavior.

## Current verification

- `harness-basic`: `npm run validate` passed; E2E gate passed `7/7`; Skill Guard
  structural tests passed, with two optional course-fixture cases skipped.
- `adk-rag-postgres-harness`: `uv run --with pytest --with
  'psycopg[binary]' --with tree-sitter --with tree-sitter-javascript --with
  tree-sitter-typescript pytest -q` passed with `2 passed`.
- The Git policy tests cover the destructive command list, ref deletion and
  fast-forward/non-fast-forward pre-push behavior (`17/17`).
- Both implementation worktrees passed `git diff --check`.
- The original course and harness checkouts remained clean.

## Implementation locations

- Course contract: this task and its Portuguese counterpart.
- Basic distribution: `harness-basic/templates/AGENTS.md` and
  `harness-basic/templates/policies/git-worktrees.md` in the standalone
  [harnesses repository](https://github.com/saulostopa/harnesses).
- PostgreSQL RAG distribution: `adk-rag-postgres-harness/README.md` in the
  [harnesses repository](https://github.com/saulostopa/harnesses).
