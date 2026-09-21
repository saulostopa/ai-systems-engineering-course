---
title: feature-report
---

# feature-report — the outcome, with every number traceable

> Not a tutorial and not a changelog: what was delivered, the decisions with
> their causal trade-offs, the verification that was actually executed, and the
> questions still open. Every number points at a diff, a test or a log.

## See it first

<a href="/demos/demo-report.html" target="_blank" rel="noopener">
<strong>▶ Open the demo report</strong></a> — a real delivery, rendered by the skill.

Four sections, in this order, because the order is the argument:

1. **What was delivered** — one sentence a non-author can repeat.
2. **Decisions and trade-offs** — *chose X instead of Y because Z, at the cost of W*.
   A decision with no stated cost is a preference wearing a decision's clothes.
3. **Verification** — the table of `command → expected → actual`, with real output.
4. **Open questions** — what the delivery did *not* settle.

Try the **PT/EN toggle** and the **theme switch** in the header: the artifact
carries the Eleanor tokens, so it reads like the rest of the ecosystem, and it
works in both languages without a second file.

## How the harness calls it

The delivery owes a report, and the flow says so:

```yaml
artifacts:
  - diagram
  - report
  - quiz
```

`wm-harness plan done` refuses to archive the plan while it is missing:

```
[wm-harness] ERROR: feature/OEM-123 owes a delivery report (flow 'feature-default')
             — the feature-report skill writes docs/artifacts/feature-OEM-123-report.html
```

And the harness checks the artifact, not just its existence:

```sh
./scripts/artifacts.sh feature/OEM-123 --kind report
# [artifacts] OK — report: 5 x '<section class="card"' visible
```

::: warning What that check exists for
It counts sections that survive **outside HTML comments**. That is not
paranoia — the demo shipped in this repository for months as an 18 KB file that
rendered an empty shell, because one generated comment was never closed and
swallowed every section after it. The file size looked right. Nobody opened it.
:::

## What ships here

| Piece | What it is |
|---|---|
| `skills-artifacts/feature-report/SKILL.md` | The skill: Gather → Write → Output, with an accessibility checklist |
| `skills-artifacts/assets/system.css` | Eleanor tokens, light/dark, `:focus-visible`, AA contrast |
| `skills-artifacts/assets/skeleton.html` | Accessible shell: `aria-live`, PT/EN toggle, progress |
| `skills-artifacts/scripts/build-demo.py` | The generator — and `verify()`, which refuses to write an artifact whose content is invisible |

```sh
cd skills-artifacts && python3 scripts/build-demo.py
```

**Related**: [feature-quiz](/skills/feature-quiz) · [feature-archify](/skills/feature-archify) ·
[Create a new skill](/skills/how-to-create)
