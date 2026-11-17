---
title: Project 04 — Domain harness
---

# Project 04 — Domain harness

> The same harness skeleton, skill packs per area: games, finance or sales. Pick yours.

## Objective

Build a **domain playbook**: the basic harness (Project 02) + the skills and policies package **of your domain**. It is the essence of the multi-team model (EPIC E): the skeleton doesn't change; the knowledge changes.

## The universal recipe

```
domain harness = basic harness (Project 02)
               + domain skills (on-demand SKILL.md)
               + domain verification (own gates)
               + domain artifacts (what gets delivered)
```

## Three domains to choose from

### 🎮 Games (e.g.: game creation up to publication on Roblox)

| Piece | Content |
|---|---|
| Skills | `game-design` (persona, narrative, storytelling), `asset-pipeline`, `roblox-publish` (Luau, Rojo, platform validation) |
| Feature list | Characters, mechanics, narratives — each with state |
| Verification | Simulated playtest: generate variations → simulate → measure → iterate; monetization config validation before publish |
| Artifact | HTML design doc of the feature (via `feature-report`), playtest report |

### 💰 Finance (e.g.: spreadsheet analysis)

| Piece | Content |
|---|---|
| Skills | `spreadsheet-analysis` (pandas/openpyxl), `reconciliation` (expected vs. actual), `report-generation` |
| Feature list | Reports to generate — source, deadline, state |
| Verification | Formula validation, totals check, guard against missing data |
| Artifact | HTML report published (overnight → coffee) |

### 📈 Sales (e.g.: presentations and proposals)

| Piece | Content |
|---|---|
| Skills | `deck-generation`, `proposal-draft` (briefing + CRM context), `sales-review` |
| Feature list | Proposal/deck deliverables — client, date, approval |
| Verification | Check against briefing requirements; cross-review before sending |
| Artifact | Versioned deck/proposal + feature report |

## Step by step

### 1. Define the domain and the feature list

Pick ONE domain. List 3-5 real features with state (Lesson 08).

### 2. Write 2-3 domain skills

Each skill is a `SKILL.md` with frontmatter (`name`, `description`) and a `Gather → Write → Output` body (see [create a new skill](/skills/how-to-create)). Minimal example:

```markdown
---
name: spreadsheet-analysis
description: Analyzes spreadsheets (Excel/CSV) with pandas: validates totals, detects
  missing data and generates a summary. Use when the user asks for spreadsheet analysis.
---

# Spreadsheet analysis

## Gather
- Read the file; list columns, types and totals.

## Write
- Validate: do the totals add up? missing data? outliers?

## Output
- Summary with expected vs. actual + evidence (output lines).
```

### 3. Define the domain verification

What does "done" mean **in your domain**? (Games: validated publish; Finance: reconciled report; Sales: proposal approved by review.) Write it in the domain's `definition-of-done.md`.

### 4. Run a feature end-to-end

From the feature list to the artifact, with recorded evidence — like Project 02, now with the domain skills loading on demand.

## Verification

- The same skeleton as Project 02, zero process changes.
- The domain skills were triggered **on demand** (description matching the task), not all at boot.
- The domain artifact was produced and versioned.

## Deliverable

Your versioned domain playbook: skeleton + skills + verification + 1 example artifact.

::: tip Status
The official playbooks (Games with Roblox, Finance with nightly execution, Sales with CRM) are **EPIC E** of the course.
:::

**Next project**: [05 — Area Copilot with RAG](/projects/project-05).
