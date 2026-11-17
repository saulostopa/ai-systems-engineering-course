---
title: Backlog — production workflow for AI coding agents
---

# Backlog — production workflow for AI coding agents

Status: **backlog** · Priority: **P1** · Scope: cross-cutting course and harness capability

## Source and decision

The source post compares four ways of using coding agents in production and
concludes that the reliable setup is to align on the design first, split the
work into vertical slices, and only then let the agent implement and verify the
change. The post was supplied with the course request; the LinkedIn video was
not directly fetchable, so this backlog item is based on the published outline
and summary.

The course should adopt this as a shared **production agent workflow**, rather
than create another harness. One-shot implementation remains available for
small, reversible changes, but it must not be the default for product features.

## Workflow contract

Every feature larger than a small local change should move through explicit
states:

1. **Research** — inspect the repository, constraints, dependencies, existing
   behavior and relevant evidence.
2. **Design** — agree on the behavior, boundaries, data flow, risks and
   verification strategy before implementation.
3. **Vertical slices** — define small end-to-end increments, each with an
   observable outcome and acceptance criteria.
4. **Implement** — execute one authorized slice at a time, preserving the
   declared scope.
5. **Verify** — run proportional tests, inspect the result, record evidence and
   complete the independent review when required.

The plan must preserve the distinction between implementation, execution mode
and independent review. A design approval does not authorize unrelated work,
and a passing test does not replace evidence or review.

## Proposed feature contract

```yaml
workflow:
  mode: design_first
  phases: [research, design, vertical_slices, implement, verify]
  design:
    required: true
    path: docs/exec-plans/<feature-id>/design.md
  slices:
    required: true
    path: docs/exec-plans/<feature-id>/slices.md
  review:
    independent: true
    brief_path: docs/reviews/<feature-id>/brief.md
    report_path: docs/reviews/<feature-id>/report.json
```

The exact schema should be provider-neutral and optional for existing plans.
Existing plans remain valid until migrated. The feature must reject incomplete
plans only when they explicitly opt into `design_first`.

## Adoption matrix

| Harness | Adoption |
|---|---|
| Basic | Teach the research/design/slice contract; keep approval lightweight. |
| App | Require design and vertical slices for UI, API, auth and E2E changes. |
| RAG / Area Copilot | Require data-boundary, retrieval and citation design before implementation. |
| Domain | Require explicit business rules, invariants and acceptance examples. |
| Hard | Make design-first the default and block completion without slice evidence. |
| Enterprise | Add cross-repository dependency mapping and staged rollout design. |
| ADK + RAG + Jev | Require routing, evidence, fallback and tool-gating design before runtime changes. |

## Multi-agent scope

The “herder” idea should be treated as a later execution capability, not as a
requirement for the first version. A coordinator may dispatch independent
research, implementation or review tasks only when the plan declares their
boundaries, inputs, outputs and merge order. It must not multiply agents for a
single tightly coupled slice or allow parallel edits without ownership rules.

The first implementation should support a single agent with explicit phase
transitions and an optional fresh-context reviewer. This captures the reliable
part of the source workflow without adding orchestration complexity too early.

## Skills to evaluate

The following references should be evaluated as implementation material for this
workflow:

- [AI Hero Skills](https://www.aihero.dev/skills) presents a composable set of
  27 MIT-licensed skills that work across agents. Its main chain is
  `grill-with-docs → to-spec → to-tickets → implement → code-review → retro`.
- [Matt Pocock's skills repository](https://github.com/mattpocock/skills) is
  the source repository and documents installation paths for Codex, Claude,
  Gemini CLI, Copilot and other agents.

The strongest candidates for the course are:

| Skill | Possible harness use | Initial decision |
|---|---|---|
| `setup-matt-pocock-skills` | Bootstrap repository vocabulary, tracker and document paths | Evaluate for Basic and project harnesses |
| `grill-with-docs` | Research interview, decisions and ADR capture before implementation | Evaluate for all design-first flows |
| `to-spec` | Convert an aligned conversation into a reviewable specification | Evaluate for App, Domain and Enterprise |
| `to-tickets` | Turn a specification into vertical slices | Evaluate for Hard and Enterprise |
| `implement` + `tdd` | Test-first implementation and feedback loops | Compare with existing harness gates |
| `code-review` + `pr` | Review the diff against the plan and prepare a PR | Integrate only if evidence remains provider-neutral |
| `research` + `wayfinder` | Cited research and decision mapping for larger changes | Evaluate for ADK + RAG + Jev and Enterprise |
| `handoff` + `retro` | Preserve continuity and improve the harness after delivery | Evaluate as productivity extensions |
| `implement-spec` | Parallel implementation of a complete specification | Keep experimental until ownership and merge gates exist |

Do not install the complete collection by default. First compare each skill's
instructions with the course contracts, remove duplicated gates, and keep the
course harness as the authority for scope, permissions, evidence, tests and
completion state.

## Skill evaluation and safety gate

Before adopting a skill, inspect its source at a pinned revision and record:

- the inputs it reads and the files it writes;
- commands, network access, credentials and external services it can request;
- whether it changes feature state or claims completion without harness evidence;
- conflicts with `AGENTS.md`, course policies, Archify and independent review;
- token cost, provider compatibility and behavior with Codex, Claude and local
  agents.

Skills are untrusted instructions until reviewed. They must not receive secrets,
override repository policy, execute arbitrary model output as shell or code, or
authorize destructive and external actions. Prefer copying only selected skills
into a project, pinning the revision and validating generated files in a clean
worktree. The evaluation must include prompt-injection cases in skill content,
retrieved documents and tool output.

The output of this backlog item is a compatibility matrix and an adoption
decision, not an automatic bulk installation.

## Relationship to existing features

- Extends [execution modes and independent review](/tasks/independent-review-execution)
  with a design gate and vertical-slice contract.
- Complements [feature-archify](/skills/feature-archify) by producing the
  validated flow after design and implementation, not by treating a diagram as
  the design itself.
- Applies to [ADK + RAG + Jev](/tasks/adk-rag-jev-harness) before changing
  routing, thresholds, evidence, tools or fallbacks.
- Does not replace the RAG, CAG or KAG strategy decision in the knowledge
  strategies backlog.

## Implementation sequence

1. Define the provider-neutral plan schema for research, design and slices.
2. Add a `design_first` workflow to the Basic harness with migration-safe
   defaults.
3. Add completion gates to Hard, Enterprise and ADK + RAG + Jev.
4. Add templates and course lessons showing a feature from research through
   vertical slices and independent review.
5. Evaluate the referenced skills against the matrix and existing course gates.
6. Add an optional coordinator contract for bounded multi-agent work.
7. Evaluate the workflow on one UI feature, one backend feature and one RAG or
   ADK feature before making more harnesses enforce it by default.

## Acceptance criteria

- A feature can declare `design_first` without depending on a specific model,
  CLI or vendor.
- The plan records research findings, design decisions, vertical slices,
  acceptance criteria and verification commands.
- Each slice has a bounded scope and an observable result.
- Hard, Enterprise and ADK + RAG + Jev cannot mark an opted-in feature as
  passing without the required design, slice and review evidence.
- Existing plans remain compatible until explicitly migrated.
- Multi-agent execution records ownership, dependencies, outputs and merge
  order, and cannot silently expand scope.
- The course includes a complete worked example and explains when one-shotting
  is still appropriate.
- The selected skills have a pinned source revision, compatibility result and
  explicit residual-risk record before adoption.
- No third-party skill can bypass scope, authorization, evidence or review
  gates.

## Reference

- [Source LinkedIn post](https://www.linkedin.com/posts/pau-labarta-bajo_how-to-do-you-use-ai-coding-agents-for-production-ugcPost-7516471983887425536-cjpA/)
- [AI Hero Skills](https://www.aihero.dev/skills)
- [Matt Pocock's skills repository](https://github.com/mattpocock/skills)
