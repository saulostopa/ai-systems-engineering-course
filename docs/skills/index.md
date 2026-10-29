# Skills

The Webmotors ecosystem skill catalog. Skills are instruction packages
(`SKILL.md`) that the harness loads when the task matches the description —
versioned, reviewable in PR and installable in any harness that reads
`SKILL.md` (Claude Code, Cursor, Codex, Gemini, OpenCode...).

| Skill | What it does |
|-------|-----------|
| [feature-report](/skills/feature-report) | Self-contained HTML report of what was delivered in a feature. |
| [feature-quiz](/skills/feature-quiz) | Quiz graded in 4 levels about the feature — the "golden piece". |
| [feature-animation](/skills/feature-animation) | HTML animation of a datum flowing through the feature. |
| [feature-flowchart](/skills/feature-flowchart) | Compatibility route; the current validated diagram workflow is documented by feature-archify. |
| [qa-playwright-e2e](/skills/qa-playwright-e2e) | E2E tests with Playwright (Python), semantic locators. |
| [qa-perf-triage](/skills/qa-perf-triage) | Diagnosis of latency regressions under load. |
| [feature-archify](/skills/feature-archify) | Verifiable diagrams (Archify) of the completed feature — the map that teaches the flow. |
| [skill-guard](/skills/skill-guard) | **Scans a skill before installing it** (SkillSpector) — the catalog's supply-chain gate. |
| [Create a new skill](/skills/how-to-create) | The pipeline: idea → SKILL.md → test → publication. |

## Basic harness standard profile

The complete course distribution selects seven skills from this ecosystem and
installs them under `.agents/skills/`: `feature-report`, `feature-quiz`,
`feature-archify`, `skill-guard`, `qa-playwright-e2e`, `qa-perf-triage` and
`agentic-navigation` (the App Harness visual-acceptance skill). Shared Eleanor
assets live in `.agents/skills/assets/` and are support files, not another
skill.

This profile is intentionally smaller than the whole catalog. The standalone
`harness-basic` remains the core distribution; derived packages opt into the
seven-skill profile.

::: tip Status
The evolution of these skills (Eleanor design system, accessibility, adaptive quiz)
is **EPIC F** of the project. Each skill's page describes its current design.
:::

::: warning Before installing any skill from outside
A skill is instruction that the agent executes with implicit trust — 26.1% of
the skills analyzed by NVIDIA have vulnerabilities and 5.2% show signs of
malicious intent. Go through the gate first:

```sh
harness-basic/scripts/gate-skill-scan.sh <dir-or-url>
```

See [skill-guard](/skills/skill-guard).
:::
