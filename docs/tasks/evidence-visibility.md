---
title: Backlog — evidence visibility in the ADK Dev UI
---

# Backlog — evidence visibility in the ADK Dev UI

Status: **backlog** · Priority: **P2** · Scope: ADK + RAG + Jev harness

## Goal

Make routing evidence visible without requiring the learner to expand the raw
`run_workflow` function response in the Events panel.

## Proposed experience

- show route, confidence, collection and strategy in a compact evidence card;
- show each source, score and excerpt with a clear citation boundary;
- distinguish `direct`, `retrieved`, `clarify` and `blocked` states;
- expose the same evidence bundle in Events, Artifacts and the final response;
- show the reason and missing evidence when the workflow blocks or asks for clarification.

## Guardrails

- the UI is a projection of the typed workflow result;
- it must not infer evidence from the model's prose;
- source references remain attached to every excerpt;
- redaction and size limits apply before displaying user-controlled content;
- traces continue to show timing and token data separately.

## Acceptance criteria

- a learner can identify the route and source without opening raw JSON;
- a blocked or clarification result explains why no evidence was returned;
- Events and Artifacts display the same structured evidence bundle;
- the visual layer does not change workflow decisions.
