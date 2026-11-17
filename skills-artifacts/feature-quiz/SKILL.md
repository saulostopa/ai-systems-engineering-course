---
name: feature-quiz
description: Generates an HTML quiz graded in 4 levels about a freshly implemented feature, with automatic scoring, per-level feedback, adaptive review mode (wrong questions repeated) and two-language support. Use when the user asks to be tested/assessed on a feature or material.
---

# Feature quiz (v2 — adaptive)

A quiz graded in 4 levels with **adaptive review mode**: every wrong question
automatically enters the review (repetition with the why shown) — the reader
does not "skip past" the mistake (course lesson: critical capability).

## Gather

- The feature report (`reports/<same-slug>.html`) — the quiz must agree with it on decisions and verification.
- The diff and the tests: **hard** comes from a real edge case or failure present in the diff/tests, never from an invented trick question.
- Every question must be answerable from the read material.

## Write

Four `.quiz-level` (always in this order, `data-level="tier-1..4"`, with `data-level-label` and `data-level-hint`):

1. **Basic** — surface facts (what it does, where it lives, how it is invoked). 3 questions.
2. **Intermediate** — mechanics (how it works, main flow). 3 questions.
3. **Advanced** — rationale (why this decision over the rejected one; the accepted trade-off). 3 questions.
4. **Hard** — edges and failures (what breaks, limits, interaction with other systems). 3 questions.

Each question: one `.quiz-stem`, three `.quiz-opt` (exactly one `data-correct="true"`), one `.quiz-why` with a traceable justification.

**Adaptivity (v2)** — the skeleton already implements:
- per-level scoring with `aria-live` in the result;
- wrong questions enter `#review-root` (review with the question text) — the generator only needs to assemble the 4 levels; the review mode is automatic;
- EN/PT toggle: add `data-i18n-pt`/`data-i18n-en` on every text (stem, options, hint, why).

## Output

- Render through the v2 assets (`system.css` + `skeleton.html` copied in full).
- Save `quizzes/YYYY-MM-DD-<slug>-quiz.html`, delivered **without marked answers** (one attempt per question — reload is the only retry, no answer localStorage).
