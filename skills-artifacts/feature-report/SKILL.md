---
name: feature-report
description: Generates a self-contained, accessible HTML report of what a feature delivered — decisions, trade-offs, verification and open questions, with every number traced to a source. Use when the user asks for a report/summary of what was just implemented.
---

# Feature report (v2 — SSTT)

A result report, not a tutorial: what was delivered, the decisions with
causal trade-offs, the verification that ran and the open questions. Every
number traceable to a diff, test or log — never silently estimated.

## Gather

- The change: read the diff and the code it touches.
- The real verification: executed commands and outputs (build, tests, e2e).
- The item context: what was declared in scope (scope-control) — the report compares delivery vs. scope.
- If a previous `reports/<same-slug>.html` exists, read it and diff what changed.

## Write

Structure (cards, always in this order):

1. **What was delivered** — result, declarative past tense. No process ("we worked").
2. **Decisions and trade-offs** — causal format: "Chose X instead of Y because Z, at the cost of W".
3. **Verification** — table: command, expected, actual. A number without a source becomes "not measured".
4. **Open questions** — real, answerable questions, not TODOs in disguise.

## Mandatory accessibility (v2)

- AA contrast: secondary/muted texts on the corresponding role colors.
- Semantic structure: one `h1` per page, `section` with `aria-label`.
- Tables with `th`; numbers in `tabular-nums`.
- No information conveyed by color alone (verdict has icon/text besides color).

## Output

- Render **whole** through the v2 assets: `../assets/system.css` (`<style>` block) and `../assets/skeleton.html` (structure + scripts copied in full — the scripts have `${...}` literals that collide with template engines; never rewrite them).
- Every element with `data-i18n` gets `data-i18n-pt` and `data-i18n-en` (the EN/PT toggle in the toolbar already works).
- Save to `reports/YYYY-MM-DD-<slug>.html` and open it.
