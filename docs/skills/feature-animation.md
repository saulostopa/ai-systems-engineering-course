---
title: feature-animation
---

# feature-animation — one real trip, one stage at a time

> A diagram shows you the shape of a system. An animation walks you through
> **one concrete journey** — one commit, one request, one record — with the real
> value it carries at each step. It is the artifact for "but what actually
> happens?"

## See it first

<a href="/demos/demo-animation.html" target="_blank" rel="noopener">
<strong>▶ One commit travelling through the gates</strong></a> — press **Step** and
watch a change to `price-tag.tsx` meet each gate in turn.

<a href="/demos/demo-consent-journey.html" target="_blank" rel="noopener">
<strong>▶ From consent to identity</strong></a> — a visitor answers the Fuse CMP banner and
becomes an AdFixus `acid` that reaches GAM as the PPID. Five stages, drawn from
`ignition-adfixus-tag-docs`.

The second one is worth opening for the card underneath it rather than the
animation: it records that for a Brazilian visitor the journey **never leaves
stage 1**, because the CMP reports `gdprApplies: false` and the `tcloaded` /
`useractioncomplete` events the bridge filters on never arrive. An animation
that showed only the happy path would have been a pleasant lie.

Four stages, and every value in them is real:

| Stage | What it carries |
|---|---|
| `git commit` | `src/components/price-tag.tsx` — staged, nothing verified yet |
| `gatekeeper.sh` | `1 in_progress ✓` — the scope was declared before the edit |
| `e2e-gate.sh` | `e2e/test_price.py ✓` — the test came in the same commit |
| `commit` | `a1b2c3d feature/OEM-123` |

The caption is `aria-live`, so a screen reader is told which stage is active
instead of being expected to notice a border change colour. And autoplay is
opt-out by preference: `prefers-reduced-motion` stops it before it starts.

## What the skill got wrong, and it was not the skill

The page you are reading was a nine-line stub, so it was fair to wonder whether
the skill had been lost. It had not — `harness-agent-skills/animations/` held a
working artifact from 2026-08-21, with real playback. What happened is more
specific, and worth knowing if you write skills:

`feature-animation` is told to splice in `system.css` and `skeleton.html` from
`feature-report`. When those assets were rewritten for Eleanor, **report and
quiz were carried across and the animation styles were not**. The v1 stylesheet
had eight `.flow-*` rules; the v2 had zero. The skill kept pointing at a design
system that could no longer style what it produced.

So the old artifact still looked right — it was generated before the migration —
while anything generated after it would have come out unstyled. **A skill that
depends on shared assets breaks silently when those assets move on.**

Two defects came with it, both now fixed:

- **The accent was `#2554c7` blue.** Every other artifact in the catalog had
  moved to Eleanor red. Ported: the demo above measures `rgb(216, 31, 65)`.
- **The track scrolled horizontally.** At 1440px the row was 1355px wide inside
  a 1040px box, so the last stage sat off-screen on load — a stage the reader
  never knew existed. Stages now share the row instead of demanding a width
  from it, and on a phone the track becomes a column.

## Choosing the stages

Three to six. Fewer does not earn an animation; more does not fit the row, and
the fix for "more" is grouping adjacent stages that belong to the same concern —
not shrinking the boxes.

The rule that decides whether a stage is real: **you can name the function,
endpoint or script it stands for, and the example value is something that could
actually appear there.** `Stage 2` with `example data` is a placeholder wearing a
diagram's clothes.

## Where it sits among the others

| Artifact | Answers |
|---|---|
| [feature-report](/skills/feature-report) | what was delivered, and what proves it |
| [feature-archify](/skills/feature-archify) | how the built system is wired |
| **feature-animation** | what one real trip through it looks like |
| [feature-quiz](/skills/feature-quiz) | whether the reader understood any of it |

It is **not** demanded by the default flow. The diagram already carries the
delivery's explanation, and requiring both would tax every merge to cover a case
most features do not have. Add `animation` to a flow's `artifacts:` list when
the feature is one people will need walked through.

```sh
cd skills-artifacts && python3 scripts/build-demo.py
```

**Related**: [feature-archify](/skills/feature-archify) · [feature-report](/skills/feature-report) ·
[Create a new skill](/skills/how-to-create)
