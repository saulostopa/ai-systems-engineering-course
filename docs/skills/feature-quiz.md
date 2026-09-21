---
title: feature-quiz
---

# feature-quiz — the artifact that finds out whether you understood

> A report tells you what happened. A quiz finds out whether it landed. Four
> levels, and every wrong answer goes into a review list automatically — the
> reader does not get to skim past the thing they missed.

## See it first

<a href="/demos/demo-quiz.html" target="_blank" rel="noopener">
<strong>▶ Open the demo quiz</strong></a> — answer it before reading on; it takes a minute.

Notice what does **not** happen when it loads: nothing is highlighted. Pick your
answers, press **Check answers**, and only then does each option turn green or
red, each justification appears, and the wrong ones collect in the review.

::: warning The bug worth knowing about
Until this page was written, the correct option was styled unconditionally —
every answer was green from page load. The quiz shipped with its own answer key
visible. One CSS rule now gates the reveal on `.quiz-level[data-checked="true"]`,
which the script sets only after you submit.
:::

## The four levels

| Level | Asks for | Fails when |
|---|---|---|
| **Basic** | recall — surface facts | the reader never read the report |
| **Intermediate** | mechanics — the main flow | they read it but did not follow it |
| **Advanced** | rationale — the trade-off accepted over the rejected alternative | they know *what*, not *why* |
| **Hard** | edges — real failures from the diff and tests | they never looked at the limits |

Each question: a stem, three options with exactly one correct, and a
`quiz-why` justification traceable to the material. **Hard never means a trick
question** — an invented gotcha teaches nothing and costs trust.

## Adaptivity

The shell already implements it: per-level scoring announced through
`aria-live`, and every wrong item copied into `#review-root` automatically. The
generator only assembles the levels — it never reimplements the logic, which is
why a quiz cannot ship with a broken scoring loop.

## How the harness calls it

```yaml
artifacts:
  - diagram
  - report
  - quiz
```

```
[wm-harness] ERROR: feature/OEM-123 owes a delivery quiz (flow 'feature-default')
             — the feature-quiz skill writes docs/artifacts/feature-OEM-123-quiz.html
```

```sh
./scripts/artifacts.sh feature/OEM-123 --kind quiz
# [artifacts] OK — quiz: 25 x 'quiz-opt' visible
```

The check counts options that survive **outside HTML comments** — bytes on disk
are not evidence that a browser will show anything.

**Related**: [feature-report](/skills/feature-report) · [feature-archify](/skills/feature-archify) ·
[Create a new skill](/skills/how-to-create)
