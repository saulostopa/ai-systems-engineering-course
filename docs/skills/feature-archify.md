---
title: feature-archify
---

# feature-archify — post-completion diagrams

Skill wrapper that integrates **Archify** ([tt-a1i/archify](https://github.com/tt-a1i/archify), MIT, 62k stars) into the course's artifact flow: when work is completed, in addition to the `feature-report` and the `feature-quiz`, the harness generates the **verifiable diagram** that teaches how what was built works.

## Delivered

| Piece | What it is |
|---|---|
| `skills-artifacts/feature-archify/SKILL.md` | Skill wrapper in the course pattern (Gather/Write/Output) — type choice, quality contract and the validate→deliver cycle |
| `.agents/skills/archify/` | The complete Archify skill (v2.17, MIT) — functional package: schemas, renderers, Node binary |
| `pilots/archify-demo/harness-basic-pipeline.json` | Reproducible source of the demo diagram |
| `pilots/archify-demo/harness-basic-pipeline.html` | **Delivered diagram**: 9/9 artifact checks, composition showcase **PASS** — the basic harness pipeline with gates |

## The demo diagram (open in your browser)

`pilots/archify-demo/harness-basic-pipeline.html` — the basic harness workflow:
person/agent → init → feature_list → implementation → **gatekeeper** (with the
"no feature — declare one" return) → build/tests → validate-harness →
commit+push. With 2 views (`#view=happy-path` and `#view=gates`) and 3 cards,
including what the reader should learn and the G1 pilot finding.

## Why it is "verifiable"

Archify doesn't render by opinion: the typed JSON goes through **atomic
validators** (schema, layout, routes, clearance) and only an artifact that passes
`composition: showcase` is delivered — every failure comes with a diagnosis and
supported correction. In this integration, the validator caught real
topology and routing errors in 8 iterations until the pass — exactly the discipline
the course teaches (evidence before "done", applied to the diagram itself).

## Install in another project

```sh
npx skills add tt-a1i/archify -g          # or --agent opencode --copy
```

## Usage

```
"generate the flow diagram of the feature we just delivered"
```

**Related**: [feature-report](/skills/feature-report) · [feature-quiz](/skills/feature-quiz) · [Create a new skill](/skills/how-to-create)
