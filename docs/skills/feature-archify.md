---
title: feature-archify
---

# feature-archify — the diagram the delivery owes

> A feature that only leaves code behind forces the next person to read the diff
> to understand it. This skill makes the delivery explain itself — with a diagram
> that is **validated before it ships**, not drawn by opinion.

It wraps **Archify** ([tt-a1i/archify](https://github.com/tt-a1i/archify), MIT)
into the harness: when a feature closes, the agent writes a typed description of
what was built, and the harness renders and verifies it.

## See it first

<a href="/demos/feature-branch-lifecycle.html" target="_blank" rel="noopener">
<strong>▶ feature/OEM-123 — from ticket to production</strong></a> — the branch lifecycle
you actually live: commit gate, CI, review, deploy, and the three ways each one
sends you back to the keyboard.

<a href="/demos/harness-basic-pipeline.html" target="_blank" rel="noopener">
▶ The basic harness pipeline</a> — the same skill applied to the harness itself.

It is one self-contained HTML file. Things to try once it is open:

- **Switch views** — `#view=happy-path` and `#view=gates` are two readings of the
  same graph, not two drawings that can drift apart.
- **Follow the gatekeeper's return edge** — the "no feature — declare one" loop
  back to `feature_list`. That failure path is why the diagram is a workflow and
  not a flowchart.
- **Read the cards** — one states what the reader should learn, another records
  the finding from the G1 pilot.

## Why "verifiable" is the whole point

Most diagrams rot because nothing can tell you they are wrong. Archify takes
typed JSON through **atomic validators** — schema, layout, routing, clearance,
readability — and refuses to deliver an artifact that fails any of them.

That is not theoretical. While preparing this page the demo stopped passing:

```
composition/desktop-readability
  text: "feature passing — report + quiz generated"
  projectedFontPx: 5.64   minimumProjectedFontPx: 6
```

A label had grown long enough to render below the legible floor at 1440×900. No
human review would have caught 5.64 versus 6. The fix was shortening the label to
`feature passing`, and the artifact went back to `showcase` — **0 errors, 9/9
checks**. Evidence before "done", applied to the diagram itself (Lesson 09).

## How the harness calls it

The split matters: **the agent authors, the harness verifies**. No script can
infer a diagram from a diff — and nobody should be trusted to remember to
validate one.

```bash
# 1. the agent writes the source: a typed description of what was built
#    docs/artifacts/feature-OEM-123.json

# 2. the harness renders and validates it
./scripts/artifacts.sh feature/OEM-123
# [artifacts] OK — docs/artifacts/feature-OEM-123.html passed at showcase quality
```

And it is not optional where it matters. The `feature-default` flow declares it:

```yaml
artifacts:
  - diagram
```

So `wm-harness plan done` refuses to archive the plan without it:

```
[wm-harness] ERROR: feature/OEM-123 owes a delivery diagram
             (flow 'feature-default') — run: ./scripts/artifacts.sh feature/OEM-123
```

The `hotfix` flow declares `artifacts: []` on purpose — an incident should not
wait on a diagram, and the follow-up improvement item is where the explaining
gets done.

## The Webmotors palette

Archify has no theming field: `visual_preset` offers four fixed looks and
`brandMark` is a per-node logo. What it *does* expose is 38 CSS custom
properties in the delivered HTML, so `scripts/eleanor-theme.css` overrides them
after `archify deliver` — geometry untouched, which matters because geometry is
what the validator approved.

Two details cost a round of debugging each:

- Archify scopes its palette as `[data-preset="signal-flow"][data-theme="light"]`,
  which **outranks a bare `:root`**. The first attempt looked applied and changed
  nothing.
- Eleanor is a two-mode system and the artifact has a working light/dark toggle,
  so shipping only the dark palette would have turned that toggle into a no-op.

Contrast is not inherited from a brand, it is measured:
`scripts/check-contrast.py` walks both blocks and fails below floor — 4.5:1 for
text (WCAG 1.4.3), 3:1 for strokes (1.4.11). It caught three tokens the first
pass got wrong, one of them at 2.7:1.

```sh
python3 scripts/check-contrast.py scripts/eleanor-theme.css
# 28 token(s) checked, 0 below floor
```

## Choosing the type

| Type | Use when the question is |
|---|---|
| `workflow` | how does the process run, including the failure paths |
| `sequence` | who calls whom, in what order |
| `dataflow` | where does the data come from and where does it land |
| `architecture` | what are the pieces and how are they wired |
| `lifecycle` | what states does this thing move through |

The wrong type produces a valid diagram that answers a question nobody asked.
Pick from the reader's question, not from the code's shape.

## Install

```sh
npx skills add tt-a1i/archify --agent opencode --copy
```

::: warning Run it through the gate first
A skill is instruction the agent executes with implicit trust. Archify is in the
catalog because it went through [skill-guard](/skills/skill-guard) — scanned,
triaged one finding at a time, with a local patch recorded in `skills-lock.json`.
Do the same for anything you add.
:::

## What ships in this repository

| Piece | What it is |
|---|---|
| `skills-artifacts/feature-archify/SKILL.md` | The wrapper, in the course pattern (Gather / Write / Output) |
| `.agents/skills/archify/` | Archify itself (MIT), scanned and pinned in `skills-lock.json` |
| `harness-basic/scripts/artifacts.sh` | The render-and-validate step, installed into every adopted repo |
| `pilots/archify-demo/*.json` | The demo source — reproducible, one command |

**Related**: [feature-report](/skills/feature-report) · [feature-quiz](/skills/feature-quiz) ·
[skill-guard](/skills/skill-guard) · [Create a new skill](/skills/how-to-create)
