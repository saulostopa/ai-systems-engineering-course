---
title: feature-report (v2)
---

# feature-report (v2 — Eleanor)

Outcome report, not tutorial: what was delivered, decisions with causal
trade-offs, verification executed and open questions — every number traceable to a
diff, test or log.

## Deliverable F1

The evolution is in `skills-artifacts/` (at the root of this repo):

| Piece | What it is |
|---|---|
| `skills-artifacts/feature-report/SKILL.md` | v2 skill: Gather → Write → Output, with a mandatory accessibility checklist |
| `skills-artifacts/feature-quiz/SKILL.md` | v2 skill: 4-level quiz + **adaptive review mode** (wrong answers enter the review) |
| `skills-artifacts/assets/system.css` | CSS with **Eleanor tokens** (Figtree, red `#d81f41`, gray dark, indigo), light/dark, `:focus-visible`, `prefers-reduced-motion`, AA contrasts |
| `skills-artifacts/assets/skeleton.html` | Accessible skeleton: `aria-live` on the result, EN/PT toggle (`data-i18n`), progress, review |
| `skills-artifacts/scripts/build-demo.py` | Mechanical generator (the same path as the skill) — produces the demos |
| `skills-artifacts/reports/demo-report.html` | Rendered report demo (evidence) |
| `skills-artifacts/quizzes/demo-quiz.html` | Rendered quiz demo: 4 levels, 12 questions, structural validation OK |
| `skills-artifacts/skill-design-v2.md` | The evolution of the v1 → Eleanor design system, item by item |

## What changed (summary)

- **Eleanor**: Figtree font, brand red `#d81f41` as the only accent, the real gray/indigo token palette.
- **Executable accessibility**: visible focus ring, reduced motion, `aria-live` on the quiz result, AA contrast, no information conveyed by color alone.
- **Multi-language**: working EN/PT toggle in the toolbar (`data-i18n-pt/en` pairs).
- **Adaptive quiz**: wrong answers automatically enter review mode — the reader doesn't gloss over the error.

## How to use

```
"generate the report for this feature"      → v2 skill (if installed from this repo)
"quiz me with a 4-level quiz"
```

To regenerate the demos:

```sh
cd skills-artifacts && python3 scripts/build-demo.py
```

**Related**: [feature-quiz](/skills/feature-quiz) · [Create a new skill](/skills/how-to-create)
