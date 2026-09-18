---
title: feature-quiz (v2)
---

# feature-quiz (v2 — adaptive)

Quiz graded in 4 levels about the just-implemented feature, with automatic scoring, per-level feedback and an **adaptive review mode**: every wrong answer automatically enters the review — the reader doesn't gloss over the error.

## Deliverable F1

The evolution is in `skills-artifacts/` (root of this repo): v2 SKILL.md, assets (Eleanor system.css + skeleton with aria-live and EN/PT toggle), build-demo.py and the rendered `quizzes/demo-quiz.html` as evidence (4 levels × 3 questions, validated structure).

## The 4 levels

1. **Basic** — surface facts (recall).
2. **Intermediate** — mechanics (main flow).
3. **Advanced** — rationale (trade-off accepted over the rejected alternative).
4. **Hard** — edges and real failures of the diff/tests (never an invented trick question).

Each question: stem + 3 options (one correct) + `quiz-why` with a justification traceable to the read material.

## Adaptivity

The skeleton already implements: per-level scoring with `aria-live`, and wrong questions enter `#review-root` automatically. The generator only assembles the levels — it doesn't reimplement the logic.

**Related**: [feature-report](/skills/feature-report) · [Create a new skill](/skills/how-to-create)
