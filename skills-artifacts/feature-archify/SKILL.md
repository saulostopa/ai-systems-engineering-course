---
name: feature-archify
description: Generates verifiable diagrams (workflow, sequence, dataflow, architecture, lifecycle) of a just-completed feature, using Archify — to teach whoever uses the harness what was built and how it flows. Use when the user asks for a diagram, chart, flowchart or visual map of a feature/work that was just completed.
---

# Feature Archify — post-completion diagrams

When a piece of work is completed, the harness delivers two learning
artifacts: the `feature-report` (what was delivered) and this one — **the
diagram that teaches how what was built works**. An Archify diagram is
verifiable (validated before delivery), interactive and self-contained (one HTML).

## Gather

- The feature report (`reports/<slug>.html` from the feature-report skill) — the facts come from it.
- The diff/tests — for the right diagram type (see below).
- The Archify skill installed in `.agents/skills/archify/` (install with `npx skills add tt-a1i/archify`).

## Choose the right type

| Completed work | Diagram type |
|---|---|
| Changed a flow/pipeline (CI, approvals, gates) | `workflow` |
| Changed an interaction (API, cache, auth, async) | `sequence` |
| Changed data movement (ETL, lineage, PII) | `dataflow` |
| Changed the system (components, services, boundaries) | `architecture` |
| Changed states (retries, waits, terminals) | `lifecycle` |

## Write — the quality contract (lessons from this course)

1. **Read a schema** (`schemas/<type>.schema.json` + `common.schema.json`) and **an example** (`examples/<type>*.json`) before writing — use the example for the shape of the fields, never for the facts.
2. **New IDs, domain words, own layout** — no geometry copying.
3. **mainPath only moves forward** (col never decreases); loops and returns become `role: branch/error` edges outside mainPath.
4. **No overlap** (same lane + same col = conflict) and **no long verticals crossing the middle** — if a composition gate complains, adjust the topology (move the node lane/col, route through the last column with `fromSide/toSide: right` + `route: outside-right` like the skill example), never ignore the diagnostic.
5. **Cards** for the detail that does not fit on edges — including **what the reader should learn** from the diagram.

## Output — the mandatory cycle

```sh
node .agents/skills/archify/bin/archify.mjs validate workflow <slug>.json --quality showcase --json
# → fix ALL diagnostics (each one brings its supportedFixes) — revalidate until valid
node .agents/skills/archify/bin/archify.mjs deliver workflow <slug>.json <slug>.html --quality showcase
# → "9/9 artifact checks; composition showcase: pass" is the exit criterion
```

- Save the JSON (reproducible source) and the HTML in `flowcharts/YYYY-MM-DD-<slug>/` (JSON + HTML).
- The HTML is the artifact: interactive, light/dark theme, PNG/SVG export.
- Point the reader to the **views** (`#view=<id>`) — the happy path and the gates path.

## Rules

- Never deliver HTML without `validate --json` showing `composition: pass` — the renderer blocks bad artifacts (it is the skill's gate).
- Diagram facts come from the diff/report; no invented topology.
- If the diagram type is unclear, prefer `workflow` (the work flow) — it teaches the most.
