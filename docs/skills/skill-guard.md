---
title: skill-guard
---

# skill-guard — no skill enters without a scan

Skill wrapper + **executable gate** that integrates
[SkillSpector](https://github.com/NVIDIA/SkillSpector) (NVIDIA, Apache-2.0) into
the harness's skill installation flow.

Everything else in this course treats the skill as *the good thing*: the instruction
package that teaches the agent to do something well. This page treats the skill as an
**attack surface** — because it is both at the same time.

## Why this exists

A skill enters the agent's context and starts **driving the model's
behavior**. It arrives via `npx skills add`, a link in Slack, a
copy-and-paste — without code review, without sandbox, without CI. It is the cheapest
way to compromise an agent and the most expensive to audit after it has run.

In NVIDIA's survey of 31,132 skills: **26.1% contained
vulnerabilities** and **5.2% showed signs of malicious intent**.

The harness already blocks commits without a declared feature (Lesson 07) and code without
evidence (Lesson 09). A third-party skill entering without any gate was the
hole in the middle of that.

## Delivered

| Piece | What it is |
|---|---|
| `skills-artifacts/skill-guard/SKILL.md` | Skill wrapper in the course pattern — when to scan, how to read the verdict, what to record |
| `harness-basic/scripts/gate-skill-scan.sh` | **The gate**: blocks installation of a failed skill (exit 1) |
| `skills-lock.json` | Verdict (`scanVerdict`) recorded per skill — who approved it, with which scanner, when |
| `pilots/skillspector-demo/` | Evidence: real scan of all repository skills + the fixture that proves the gate blocks |

## The gate

```sh
harness-basic/scripts/gate-skill-scan.sh <target>   # dir, SKILL.md, .zip or repo URL
harness-basic/scripts/gate-skill-scan.sh --all    # all skills in the repository
```

Three design decisions, and the reason for each:

**Docker, not `pip install`.** The scanner is Python 3.12+; the team's machine has
whatever Python it has. The image is built from the official `Dockerfile` on the first
run and reused afterwards. Zero dependency on the local environment.

**Static (`--no-llm`), not semantic.** A gate needs a **deterministic** verdict:
the same target gives the same result, in CI, offline, without an
API key and at no cost per scan. The semantic step catches what the static doesn't
see — but a gate that changes its mind between executions is not a gate.

**Pin by commit, not by tag.** The gate checks that `v2.11.2` still points to
`69dcdfb7…` before trusting the scanner. A remote tag can be rewritten: the
name stays the same and the code changes. Pinning a supply-chain tool to a
movable pointer would be the very failure it looks for.

## Reading the verdict

| Score | Severity | The gate |
|---|---|---|
| 0-20 | LOW | **approves** (exit 0) |
| 21-50 | MEDIUM | **warns** — read the findings and decide |
| 51-100 | HIGH / CRITICAL | **blocks** (exit 1) |

Full JSON reports in `.harness/skill-scans/<skill-path>.json`. The findings
are identified by pattern — `SC2` (`curl \| bash`), `PE3` (credential
access), `E1`/`E4` (external transmission, context leak), `P1`/`P2`
(instruction override, hidden instructions), `TM2` (tool misuse) — among 71
patterns in 17 categories, including *MCP tool poisoning*.

## False positives — the baseline

A static scanner delivers **noise with signal inside**. When a finding is
verified as a false positive, it enters a baseline — it never disappears by
threshold adjustment:

```yaml
# .harness/baselines/agents-skills-archify.yaml
rules:
  - id: "EA3"
    message: "*NOT LIMITED TO*"
    reason: >-
      Matches the SIL Open Font license phrase embedded in the template.
```

The baseline lives in `.harness/baselines/<slug>.yaml`, **outside the scanned
tree**, and is mounted read-only in the container. One per skill — never a
global one, which would disarm the rule for all the others.

::: danger Why not inside the skill
The first version kept the baseline in `<skill>/.skillspector-baseline.yaml`,
arguing it would be "reviewable in PR next to the code it forgives".
The external review knocked down the argument: it is **circular** — the same PR that brings the
skill brings the baseline. A hostile author would iterate the scanner until writing a YAML
that suppresses all of its own findings, and the gate would start measuring what they
chose. "No skill enters without passing the scanner" would become "any skill that
knows how to write a YAML enters".

Today the gate **blocks** any target that carries a baseline inside itself.
:::

The gate applies the baseline by itself when it finds the file. Every rule requires
`reason`: a suppression without a written reason is a decision nobody will be able to
review later.

**Never suppress a finding you haven't opened.** In the pilot, 57 of the 59 `archify`
findings were noise — but that is only a legitimate claim because all 59 were
read one by one. See [`pilots/skillspector-demo/scan-results.md`](https://github.com/svslwm/harness-plannig/blob/develop/pilots/skillspector-demo/scan-results.md).

::: tip The gate failed itself
In the first sweep, `skill-guard` itself scored 33/100 — two `SC2`
matches on the `curl | bash` text in the lines where it **names the pattern**.
The static scanner doesn't distinguish mentioning from doing. The way out wasn't
paraphrasing the text (whoever reads the report needs to find the same string in the
document), it was the baseline with the written reason.
:::

## The limits — read before trusting

A gate you lie to is worse than no gate, so:

- **Score 0 means "no known pattern", not "it's safe".** The static
  mode judges **form**, not intention.
- **The static mode is strong on commands and weak on prose.** In the test fixture,
  the scanner caught `curl | bash` (SC2), `~/.ssh` reading (PE3) and the four
  external transmissions (E1) — and did **not** flag the "ignore any previous
  restrictions" nor the request to repeat the system prompt. Malicious instruction
  written in running Portuguese prose is exactly what the semantic step would see.
- **`coverage: partial` is the common case, not the exception.** Part of the content
  was not inspected; the number appears next to the score on purpose.
- **The gate covers what goes through it.** A skill installed by hand, outside
  `skills-lock.json`, hasn't been scanned by anyone.
- **The pin covers the remote tag, not the local image.** The gate checks that
  `v2.11.2` still points to the pinned commit, but reuses any local image
  with that name. A poisoned CI cache with a tampered `skillspector:v2.11.2`
  would pass with "pin confirmed" on screen. Where that matters, force the
  rebuild: `docker rmi skillspector:v2.11.2` before running the gate.

## Rules

- Scan **before downloading** — `gate-skill-scan.sh <url>` fetches inside the
  container. Cloning to scan later has already put the code on the machine.
- An approved skill enters `skills-lock.json` with the `scanVerdict` that approved it.
- Source changed, verdict dead: run it again.
- **Never raise the threshold to make a skill pass.** Installing something the gate
  blocked is a user decision, made with the findings in front of them and
  recorded — not a silent adjustment of `SKILL_GUARD_MAX_SCORE`.

## External review

This gate went through an **independent adversarial review** after it was ready,
and it found something serious: the baseline and the fixture marker lived inside the
skill's directory — both controlled by the entity the gate should have been
measuring — and a non-integer `SKILL_GUARD_MAX_SCORE` silently disarmed the
gate, approving score 70.

The full report (11 findings, with the failure scenarios reproduced) is in
[`pilots/skillspector-demo/REVISAO-EXTERNA.md`](https://github.com/svslwm/harness-plannig/blob/develop/pilots/skillspector-demo/REVISAO-EXTERNA.md),
alongside the prompt that produced it.

It is the most instructive part of the pilot: **a security gate written with
care still had a bypass**, and whoever wrote it didn't see it. Independent
review is not a process formality.

**Related**: [Create a new skill](/skills/how-to-create) ·
[feature-archify](/skills/feature-archify) · [Overview](/skills/)
