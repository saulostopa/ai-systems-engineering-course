# Create a new skill

The skill pipeline: **idea → SKILL.md → test → publication**.

1. **Idea** — check `ideas/BACKLOG.md` of `harness-agent-skills` before starting; your idea may already be proposed.
2. **SKILL.md** — frontmatter with only `name` and `description`; the body in `Gather → Write → Output` (the pattern validated by `feature-report` and `explain`).
3. **Test** — load the skill into a real harness (Claude Code, OpenCode) and run the use case end-to-end.
4. **Publication** — PR to `harness-agent-skills`; once approved, it becomes a folder at the root, in the same format as the others.

And the reverse path — **installing** a skill that came from outside:

```sh
harness-basic/scripts/gate-skill-scan.sh <dir-or-url-of-repo>
```

Scan **before downloading** and record the verdict in `skills-lock.json`.
See [skill-guard](/skills/skill-guard).

::: tip Golden rule
"Build mechanically, don't re-type" — the skill must assemble artifacts from
what was read/verified, never recreate content from memory.
:::
