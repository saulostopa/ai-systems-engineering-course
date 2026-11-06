---
title: Backlog — CLI decision providers
---

# Backlog — CLI decision providers

Status: **backlog** · Priority: **P2** · Scope: ADK + RAG + Jev harness

## Goal

Add optional decision-provider adapters for locally authenticated CLI agents:

- `HARNESS_DECISION_PROVIDER=cli-agy`;
- `HARNESS_DECISION_PROVIDER=cli-codex`;
- `HARNESS_DECISION_PROVIDER=cli-claude`.

The adapters would let the harness compare typed routing decisions from the
installed CLIs without changing the ADK workflow or the provider-neutral
`DecisionProvider` contract.

## Proposed contract

Each adapter must run one non-interactive request and return the same typed
`DecisionResult` used by Jev and the OpenAI-compatible providers. The request
must include the current state, the bounded questions and a strict JSON Schema
for `Noul`, `Choice` and `Score` answers.

The implementation should use the CLIs' print/non-interactive modes:

| Provider | Candidate mode | Required controls |
|---|---|---|
| Agy | `--print --output-format json` | disable slash commands; no workspace tools |
| Codex | `exec --ephemeral --sandbox read-only --output-schema` | no edits, no worktree, no persistent session |
| Claude | `-p --output-format json --json-schema` | no tools; deny permission prompts |

Flags must be configurable because CLI versions can change. The adapter must
never run an unrestricted interactive session inside `run_workflow`.

## Guardrails

- read-only execution by default;
- no shell, file-write, browser or MCP tools;
- timeout and process termination;
- maximum output size;
- strict JSON parsing and schema validation;
- no API keys or raw CLI output in logs;
- provider failures fail closed through the existing workflow;
- CLI decisions remain advisory and cannot authorize irreversible actions;
- separate evals for each CLI and model version.

## Evaluation plan

Run the golden prompts for direct, retrieved, clarification and blocked cases.
Compare route, confidence calibration, collection, strategy, evidence and
latency against `ollama` and official Jev when available. Record the
CLI version and command configuration with every result.

## Acceptance criteria

- Each CLI provider passes the shared `DecisionProvider` contract tests.
- Malformed, truncated and out-of-schema output is rejected.
- A hung or unavailable CLI reaches the deterministic fallback.
- The default provider remains `ollama`; enabling a CLI is explicit.
- The integration does not modify the workspace or create persistent sessions.
