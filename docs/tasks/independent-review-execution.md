---
title: Backlog — execution modes and independent review
---

# Backlog — execution modes and independent review

Status: **backlog** · Priority: **P1** · Scope: cross-cutting harness capability

## Decision

Add a shared **Execution and Independent Review Contract** to the course. The
capability comes from the Iris Target harness and prevents a feature from being
marked `passing` only because its implementation command succeeded.

The default mode remains `checkpointed`. A feature may opt into
`end_to_end_independent_review` when the user wants the authorized technical
cuts executed in sequence and reviewed only after the implementation is ready.

The mode does not expand authority. It still stops for external actions,
destructive changes, missing credentials or data, material scope changes, and
legal or commercial decisions.

## Contract

```json
{
  "execution": { "mode": "checkpointed" },
  "completion": {
    "independent_review": {
      "required": true,
      "fresh_context": true,
      "reviewer_must_differ_from_implementer": true,
      "brief_path": "docs/reviews/<feature-id>/brief.md",
      "report_path": "docs/reviews/<feature-id>/report.json"
    }
  }
}
```

`execution.mode` controls the delivery rhythm. `completion.independent_review`
controls the evidence required before `passing`. They must remain separate so a
feature can be executed checkpoint by checkpoint and still require an
independent final review.

## Adoption matrix

| Harness | Policy |
|---|---|
| Basic | Support both modes; checkpointed by default |
| App | Require independent review for UI, auth, API or E2E changes |
| RAG / Area Copilot | Require it for retrieval, citations, permissions or data-boundary changes |
| Domain | Require it for compliance, finance, monetization or critical business rules |
| Hard | Make it the default gate before `passing` |
| Enterprise | Require it for cross-repository and flow changes |
| ADK + RAG + Jev | Require it for routing, thresholds, fallback, evidence and runtime changes |

Small documentation-only changes may remain checkpointed without an independent
review unless the feature explicitly opts in.

## Review protocol

1. Register the mode and reserved brief/report paths before implementation.
2. Define scope, acceptance criteria, invariants and proportional checks.
3. Run an initial review in a fresh context using a different reviewer identity.
4. Record existing paths, commands, results, findings and resolutions.
5. Require a final review in a new context and from a new reviewer instance.
6. Allow `passing` only with a final `PASS` and no unresolved findings.

The report must bind the reviewed state to a commit or revision. A declared
`fresh_context` flag alone is not sufficient evidence; the harness should record
the review task/session identifier when the capability is implemented.

## Archify integration

Archify keeps its existing deterministic artifact contract:

- `validate` checks schema, geometry and composition;
- `deliver` creates the trusted artifact and records specification/artifact hashes;
- `visual-check` records automated browser evidence;
- perceptual visual review remains a separate claim.

Add an optional Archify review contract rather than making every diagram require
an agent review. A review receipt should validate:

- matching `specification_sha256` and `artifact_sha256`;
- reviewed revision and reviewer identity;
- inspected views, themes and required viewport coverage;
- findings with severity, status and resolution;
- final `PASS` for review-required deliveries.

The intended CLI shape is a separate review validation step or an explicit
`--require-review` flag on final delivery. It must never turn automated browser
evidence into a perceptual review claim.

## Implementation sequence

1. Add the provider-neutral schema and validator to `harness-basic`.
2. Add review evidence to Hard and Enterprise completion gates.
3. Integrate the contract into ADK + RAG + Jev for routing and evidence changes.
4. Add the optional review receipt and hash binding to Archify.
5. Add adversarial tests for same-reviewer reuse, stale revisions, missing
   evidence, unresolved findings and invalid paths.

## Acceptance criteria

- Existing features remain valid without an `execution` object.
- `passing` cannot bypass an explicitly required independent review.
- Reviewers, contexts, revisions, paths and commands are recorded.
- All reviewed paths stay inside the repository.
- Stale reports cannot validate a newer artifact or commit.
- The Archify receipt keeps deterministic validation, browser evidence and
  perceptual review as separate claims.

## Source decision

The feature is based on the execution modes and independent review validator
implemented in the Iris Target harness: [PR #1](https://github.com/saulostopa/iristarget/pull/1).
