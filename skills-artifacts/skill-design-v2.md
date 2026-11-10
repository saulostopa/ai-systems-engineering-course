# Design system v2 — Eleanor

The evolution of the artifact skills' design: the v1 principles (Carbon,
Lightning, Fluent, Material, GOV.UK, Atlassian — see v1 in
`harness-agent-skills`) now on top of the **Eleanor design system
tokens**, with accessibility as a first-class pillar.

## What changed from v1 to v2

| Dimension | v1 | v2 (Eleanor) |
|---|---|---|
| Font | Manrope + Source Sans 3 + IBM Plex Mono | **Figtree** (display + body) + IBM Plex Mono (raw data) |
| Accent | generic | **brand red `#d81f41`** (dark: `#e53858`) |
| Palette | invented | **Eleanor tokens**: gray dark 50-950, indigo, semantic |
| Accessibility | principle cited | **executable checklist**: validated AA contrast, `:focus-visible`, `prefers-reduced-motion`, `aria-live` in the result |
| Language | pt-BR only | **EN/PT toggle** (`data-i18n` + `data-i18n-pt/en` pairs) |
| Quiz | 4 fixed levels | **adaptive review mode**: wrong answers enter review automatically |

## Tokens (summary)

- **Role > value**: `--color-accent-text` instead of `--color-red` (Atlassian lesson).
- **3 variants per status/tier**: solid, `-soft`, `-text`; text always on `-text` over `-soft`.
- **Numbers**: `tabular-nums` always; delta with direction and base.
- **Dark elevation**: surface step + hairline, never shadow alone.
- **One accent only**: semantic (success/warning/danger/info) only on real verdicts.

## Mechanical rules (do not rewrite)

- `system.css` goes whole into the `<style>`; `skeleton.html` (scripts) copied in full.
- The scripts have `${...}` literals — never run them through a template engine.
- The quiz: 4 `.quiz-level` × 3 options × 1 `data-correct` + 1 traceable `.quiz-why`.
- Adaptivity and aria-live are already in the skeleton scripts — the generator does not reimplement them.

## v2 validation (done in this deliverable)

- `scripts/build-demo.py` assembles report + quiz mechanically (the same path the skill uses).
- Structure validated: 4 levels, 12 options, 4 correct, 4 explanations, CSS injected, i18n present.
