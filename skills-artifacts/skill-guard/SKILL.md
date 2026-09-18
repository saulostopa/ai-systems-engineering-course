---
name: skill-guard
description: Scans a skill for prompt injection, data exfiltration, privilege escalation and supply chain risk BEFORE installing it, using SkillSpector (NVIDIA). Use whenever the user asks to install, add, download, evaluate or trust a skill, plugin, agent or MCP server coming from outside the repository.
---

# Skill Guard — no skill enters without a scan

A skill is instruction the agent executes with **implicit trust**: it enters
the context and starts driving the model's behavior, without code review,
without sandbox, without CI. It is the cheapest supply chain surface to
attack and the most expensive to audit after it has already run.

NVIDIA's survey of 31,132 skills found **26.1% with vulnerabilities** and
**5.2% with signs of malicious intent**. This skill answers one question
only, before installation: **can this be installed?**

Engine: [SkillSpector](https://github.com/NVIDIA/SkillSpector) (Apache-2.0),
**pinned to tag `v2.11.2`** and run in Docker — without depending on the
local Python.

## Gather

- The skill's **origin**: git repo, URL, zip or an already downloaded directory.
- Who asked and **for what** — the declared scope is what the scan will
  contradict or confirm (a diagram skill reading `~/.ssh` is not a false positive).
- The repository's `skills-lock.json`: if the skill already has a `scanVerdict`,
  check whether the `computedHash` still matches before trusting the old verdict.

## Run — the gate

```sh
harness-basic/scripts/gate-skill-scan.sh <target>      # dir, SKILL.md, .zip or repo URL
harness-basic/scripts/gate-skill-scan.sh --all         # every skill in the repo
```

The gate builds the image on first run (1-2 min), checks the **supply chain
pin** (does the tag still point to the pinned commit?) and runs the scan in
**static** mode (`--no-llm`) — deterministic, no API key, valid in CI and
offline.

**Scan the origin before downloading.** `gate-skill-scan.sh https://github.com/x/y`
makes the scanner fetch the repo inside the container. Cloning first to scan
later has already placed the code on the machine.

## Reading the verdict

| Score | Severity | What to do |
|---|---|---|
| 0-20 | LOW | Install — record the verdict in `skills-lock.json`. |
| 21-50 | MEDIUM | **Read the findings one by one** and decide with the user. The gate warns, it does not block. |
| 51-100 | HIGH / CRITICAL | Do not install. The gate blocks (exit 1). |

Exits: `0` approved · `1` blocked · `2` execution error. Full JSON reports
live in `.harness/skill-scans/<skill-path>.json`.

Findings come identified by pattern — `SC2` (curl \| bash), `PE3`
(credential access), `E1`/`E4` (external transmission and context
leakage), `P1`/`P2` (instruction override, hidden instructions), `AR1`
(refusal suppression), `TM2` (tool misuse). Cite the **ID and the line** when
reporting, never "the scanner didn't like it".

## After the scan — record

Every approved skill enters `skills-lock.json` with the verdict that approved it:

```json
"archify": {
  "source": "tt-a1i/archify",
  "computedHash": "111f1c0b…",
  "scanVerdict": {
    "scanner": "skillspector@v2.11.2",
    "scannerCommit": "69dcdfb74487d361ba4c811d088cfdea2ff3a9dc",
    "mode": "static",
    "scannedAt": "2026-09-17",
    "score": 22, "severity": "MEDIUM", "issues": 2, "suppressed": 57,
    "rawScore": 100, "rawIssues": 59,
    "decision": "ACEITO_COM_RESSALVA",
    "baseline": ".harness/baselines/agents-skills-archify.yaml",
    "notes": "SC4 fast-uri==3.1.5 (4 CVEs, via ajv) and SC1 without pin — real, not suppressed."
  }
}
```

**Keep the raw score alongside the triaged one.** Whoever opens the file later
needs to see both, not just the comfortable one. Without this record the
verdict dies in the terminal of whoever ran it, and the next person
reinstalls blind.

## False positives — the baseline

A finding you opened, read and confirmed as a false positive goes into
`.harness/baselines/<path-slug>.yaml` — **outside the scanned tree** — with
the `reason` written out in full. The gate applies it by itself when it finds
the file, and mounts the directory read-only in the container.

**Never inside the skill directory.** A baseline that lives with the skill is
controlled by the skill itself: a hostile author would only need to iterate
the scanner until writing a YAML that suppresses all their own findings, and
the gate would start measuring what the attacker chose. "It stays reviewable
in PR" does not protect — it is the same PR that brings the skill and the
baseline. The gate **blocks** any target with a `.skillspector-baseline.yaml`
inside.

**Never suppress a finding you did not open**, and never suppress a real
finding to make the gate green — a real finding stays visible until it is
fixed.

## Local patch on a third-party skill

Sometimes the finding is real and the fix is not in your repository. Fixing
the vendored copy solves it today and creates a **silent divergence**: the
next skill update erases the patch without telling anyone.

Three steps, always all three:

1. **Apply** the minimal patch (preferably only the lockfile, without touching code).
   Verify the `integrity` against the real tarball — in a supply chain fix,
   trusting a hash someone passed along repeats the problem.
2. **Declare** it in `skills-lock.json` → `localPatches`, with a verifiable
   assertion (`verifyFile`, `verifyContains`, `verifyAbsent`), the reason and
   the measured exposure. `validate-harness.sh` checks it on every health
   check and fails if the patch vanishes.
3. **Open upstream** and record the link. Until the origin ships it, the
   patch is yours — and someone needs to know that.

Measuring exposure first is worth more than reacting to the label: "CVE HIGH"
does not say whether anyone is exposed. A dev dependency, used by a build
generator that reads local files, with versioned output and no `node_modules`
installed, has **zero** exposure — and it is still worth fixing, so the gate's
warning keeps meaning something instead of becoming noise the team learns to
ignore.

## Rules

- **Scan before downloading, not after.** Order is the control.
- **A clean static scan is not an audited skill.** Static mode judges
  *form*, not intent: it catches `curl | bash` and `~/.ssh` reads
  reliably, and is weak against malicious instruction written in prose. A
  score of 0 means "no known pattern", never "it is safe".
- **`coverage: partial` is not full approval** — part of the content was not
  inspected. Report it alongside the score; do not omit it because the score
  was 0.
- **Never raise the threshold to make a skill pass.** If the user wants to
  install something the gate blocked, that is their decision, made with the
  findings in front of them and recorded — not a silent tweak of `SKILL_GUARD_MAX_SCORE`.
- **A third-party skill is re-evaluated when it changes.** An old verdict
  with a new origin does not count; run it again.
- Scan **MCP servers** too — the scanner has MCP least-privilege and tool
  poisoning patterns, and an MCP compromises as much as a skill.
