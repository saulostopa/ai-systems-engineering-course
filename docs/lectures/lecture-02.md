---
title: Lesson 02 — What a harness really is
---

# Lesson 02 — What a harness really is

> Precise definition, components, and the difference between harness, prompt and skill.

## Definition

A **harness** is everything that surrounds the model and turns it into an agent that works. Formally:

> **Harness** = the agent's work environment: the tools it can call, the knowledge it carries, the rules it obeys, the mechanisms that verify what it does and the state that persists between executions.

The formula of this course:

```
agent = model + harness
```

The model is replaceable (Claude, GPT, Gemini, DeepSeek, Llama...). The harness is what gives identity, predictability and reliability to the work.

## The components of a harness

| Component | What it is | Example in our ecosystem |
|---|---|---|
| **Tools** | Commands, APIs and actions the agent can execute | Bash, gh, git, Playwright, npx |
| **Knowledge** | Instructions and context loaded before the work | AGENTS.md, CLAUDE.md, docs/ |
| **Skills** | Instruction packages activated on demand (`SKILL.md`) | `feature-report`, `feature-quiz`, `qa-playwright-e2e` |
| **Rules/Gates** | Mechanisms that constrain behavior | Gatekeeper, pre-commit hooks, policies |
| **Verification** | How the agent proves it finished | Tests, `validate-harness.sh`, evidence |
| **State** | What persists across sessions | `feature_list.json`, `claude-progress.md`, `session-handoff.md` |

## Harness ≠ prompt

A prompt is an instruction that exists at the moment of the conversation. A harness is a **persistent system**: it lives in the repository, is versioned, goes through code review and keeps working even when the model changes.

Concrete example: the `feature-quiz` skill is a harness component. It is not "the quiz prompt" — it is a `SKILL.md` versioned in [harness-agent-skills](https://github.com/svslwm/harness-agent-skills) that any agent can load when the task matches the description. Swap the model and the skill is still there, identical.

## A harness is not a product; it is a layer

The `webmotors-harness-factory` is explicit about this in its `AGENTS.md`:

> "A reusable **Harness Factory**: the operating system that defines *how* agentic engineering work is executed. **It is NOT a product repository.**"

The product truth lives in the product repository; the harness lives in a separate layer that **governs the process**. That separation (harness/product isolation) is what allows the same harness to serve multiple projects — and it is the foundation of the multi-team model we will see in the domain lessons.

## The harness as a control system

A harness works like a control loop:

```
AGENT ──acts──▶ WORLD (files, tests, git)
  ▲                  │
  └────◀─verifies────┘
         (gates, tests, evidence)
```

Without the verification loop, the agent is a box that only emits text. With the loop, it is a worker that acts, observes the result and corrects — what Lesson 13 formalizes as *loop engineering*.

## At Webmotors

- **`webmotors-harness-factory`** — the process skeleton: hooks, policies, scripts.
- **`harness-agent-skills`** — the skill catalog: artifacts + QA + perf.
- **`agenfk`** — the management framework: items, flows, gatekeeper, telemetry and Kanban.
- **`harness-plannig`** — **this course**, which is a harness running on top of the other three (dogfooding).

## Key takeaways

1. Agent = model + harness; the model is swappable, the harness is the asset.
2. A prompt is volatile; a harness is persistent, versioned and reviewable.
3. Components: tools, knowledge, skills, gates, verification, state.
4. The harness governs process; the product lives in the product repo.
5. The act→verify loop is the heart of the system.

## Check your learning

```
"quiz me on Lesson 02"
```

**Next lesson**: [03 — The repository as system of record](/lectures/lecture-03).
