# Independent adversarial review — skill installation gate (SkillSpector)

> Response to `PROMPT-REVISAO-EXTERNA.md`. Reviewer: independent agent.
> Method: code analysis + empirical verification (fake docker in `/tmp`, real suite with the docker image present, 16/16 tests).
> Date: 2026-09-17.

## Executive summary

The gate is **structurally correct on the conventional failure paths** (empty/unreadable/no-score JSON blocks; timeout blocks; exit codes 0/1/2 per contract). However there are **two real bypass gaps** — the baseline and the fixture marker are read from inside the very untrusted target — and **one demonstrated fail-open** via a malformed environment variable. None of this requires exploiting the scanner: it is the gate's configuration that hands the verdict to the attacker.

---

## Findings (most to least severe)

### 1. CRITICAL — Baseline read from inside the target itself = attacker rewrites the verdict

`harness-basic/scripts/gate-skill-scan.sh:95-97`

The `--baseline` points to `.skillspector-baseline.yaml` **inside the skill directory** — exactly the untrusted entity the gate should be measuring. Since the scanner excludes the baseline from the analysis, a hostile skill ships a baseline that suppresses all of its own findings (the author iterates the scanner locally until the scan comes out clean).

**Demonstrated failure scenario** (fake docker returning score 100 CRITICAL without `--baseline` and score 5 with it):

```
$ gate-skill-scan.sh .agents/skills/archify      # directory WITH baseline
  [ok]     archify — score 5/100 (LOW) ...
SKILL GUARD OK — 1 aprovada(s) ...               # exit 0

$ gate-skill-scan.sh skills-artifacts/feature-quiz  # WITHOUT baseline
  [BLOCK]  feature-quiz — score 100/100 (CRITICAL) ...
SKILL GUARD BLOQUEOU — ...                       # exit 1
```

A single file controlled by the target inverts the verdict of the same skill.

**Real evidence in the repo**: `skills-lock.json` records archify with `rawScore: 100/100 CRITICAL, 59 findings` → baseline suppresses 57 → final score 22 → ACCEPTED. The mechanism allows all 59 to be suppressed, not just 57. Today's honest triage is courtesy of the reviewer, not a property of the gate.

**Severity**: it is the most serious flaw — the gate starts measuring what the attacker wants; "no skill enters without passing the scanner" becomes "any skill that knows how to write a YAML enters".

**What would fix it**: baselines outside the scanned tree (e.g. `$SCAN_ROOT/.harness/baselines/<slug>.yaml`, reviewable in PR next to the gate, never inside the target) and rejecting (or requiring prior registration of) any baseline found inside the skill directory.

### 2. HIGH — `.skill-guard-fixture` marker inside the skill = bypass of `--all`

`harness-basic/scripts/gate-skill-scan.sh:161-174`

`discover_skills` skips any directory that contains the file — and that file lives **inside** the directory that should be scanned. A third-party skill (or a supply-chain-corrupted skill) arrives with `SKILL.md` + `.skill-guard-fixture` → invisible to `--all`, counted neither as approved nor as blocked, `exit 0`.

**Failure scenario**: a PR that adds `skills/evil/SKILL.md` + `skills/evil/.skill-guard-fixture` → `discover_skills` does not list `skills/evil` (confirmed: `fixture-reprovada` is excluded exactly this way) → `--all` reports 0 blocked and exits 0.

The "versioned file, reviewable in PR" argument is circular: the same PR that introduces the skill introduces the marker.

**What would fix it**: an allowlist outside the tree (e.g. `.harness/skill-guard-fixtures` at the root, listing relative paths), or fixtures confined to a dedicated directory excluded by path.

### 3. HIGH — Non-numeric `SKILL_GUARD_MAX_SCORE` silently disarms the gate

`harness-basic/scripts/gate-skill-scan.sh:34-35, 241-252`

`[ "$score" -gt "$MAX_SCORE" ]` with `MAX_SCORE="abc"` returns 2 (error) → if and elif both false → falls to the `else` → `ok`, `exit 0`.

**Demonstrated failure scenario**:

```
$ SKILL_GUARD_MAX_SCORE=abc SKILL_GUARD_WARN_SCORE=abc gate-skill-scan.sh <skill-with-score-70>
  [ok]     feature-quiz — score 70/100 (HIGH) ...
SKILL GUARD OK — 1 aprovada(s) ...               # exit 0  ← should BLOCK
```

Without the variable (default 50): the same target → `[BLOCK]`, `exit 1`. The comment on lines 229-231 itself describes this fall-through into the `score` field and guards it — but the same guard does not exist for `MAX_SCORE`/`WARN_SCORE`. (`MAX_SCORE=""` is safe because of the `:-`; values like `"50.0"` also fail open — bash only tolerates spaces and leading zeros in `[ ] -gt`.)

**What would fix it**: validate `MAX_SCORE` and `WARN_SCORE` as integers before the loop and `fail` if they are not.

### 4. MEDIUM — The pin does not cover the local image; right tag with wrong content passes

`harness-basic/scripts/gate-skill-scan.sh:51-60, 64-80`

`verify_pin` checks only the **remote** tag. If a local image `skillspector:v2.11.2` with divergent content exists (poisoned CI cache, old image built from a rewritten tag), `ensure_image` uses it with no verification at all and the pin prints "pin confirmed" — the scanner that runs can be anything. Offline with a local image → warning and continue (lines 71-74), zero verification.

**Failure scenario**: CI with a docker cache populated by a build of a modified `skillspector:v2.11.2` (a scanner that reports score 0 for everything) → `docker image inspect` passes → `verify_pin` confirms the remote tag (which really does point to the pinned SHA) → the gate approves everything with "pin confirmed". The pin protects against tag rewriting, not against local content.

**What would fix it**: pin the expected image digest (next to the SHA) and verify via `docker image inspect --format '{{.Id}}'`; if divergent → rebuild or `fail`.

### 5. MEDIUM — `validate-harness.sh`: CWD-dependent lock + nonexistent "register verdict" flow

`harness-basic/scripts/validate-harness.sh:56-60, 77`

- (a) The error message says "run scripts/gate-skill-scan.sh and register the verdict" — but **no script in the repo writes `scanVerdict` into `skills-lock.json`** (the gate has not a single reference to the lock; the current lock was hand-edited). The documented flow does not exist.
- (b) `LOCK="skills-lock.json"` is relative to the invoker's **CWD**, and the fallback uses `git rev-parse --show-toplevel` without `-C "$ROOT"` (unlike the gate, line 40).

**Failure scenario**: `bash /path/harness-basic/scripts/validate-harness.sh` run from outside the repo (another project's CI) → `rev-parse` fails → `LOCK="/skills-lock.json"` → does not exist → `ok "no skills-lock.json (no third-party skill installed)"` → `exit 0` — the check goes inert precisely when the pre-push should fail. The comment on line 56 ("next to this directory") does not describe what the code does.

**What would fix it**: `LOCK="$ROOT/skills-lock.json"` with a `git -C "$ROOT"` fallback; and implement the verdict registration (or fix the message).

### 6. MEDIUM-LOW — `SKILL.md` (file) target ignores the baseline

`harness-basic/scripts/gate-skill-scan.sh:95`

`[ -f "$target/.skillspector-baseline.yaml" ]` only matches a directory target.

**Demonstrated failure scenario**: `gate .agents/skills/archify` → approved; `gate .agents/skills/archify/SKILL.md` → blocked, same skill, same scanner. The contract lists `SKILL.md` as a valid target; the verdict then depends on how the target is passed.

### 7. MEDIUM-LOW — `realpath --relative-to` is GNU-only; on failure it scans `./` (the whole repo)

`harness-basic/scripts/gate-skill-scan.sh:108-110`

On macOS/BSD and busybox, `realpath --relative-to` does not exist → `rel=""` → `scan "./"` → the specific target is not scanned in isolation; the verdict is the whole repo's, which can dilute a hostile skill. Works on the current machine (uutils coreutils 0.8.0). **What would fix it**: require GNU coreutils and `fail` if the flag is unsupported (or reimplement the relative computation in pure shell).

### 8. LOW — `t_timeout_falha_fechado` is a race and does not prove the timeout semantics

`harness-basic/tests/test_skill_guard.sh:148-155`

`TIMEOUT=1` against a real scan: on a fast machine/hot daemon the scan can finish in <1s → `exit 0` → spurious test failure (it passed today, but by a margin of seconds). And the test only checks `exit 1` — a gate that blocks on **any** docker failure passes without ever exercising the deadline. A fake docker that sleeps forever + an assertion of the "no report (timeout" message would test the real behavior.

### 9. LOW — Tests that would pass against a broken implementation

`harness-basic/tests/test_skill_guard.sh:195-204` and `157-167`

- `t_pin_declarado_bate_com_a_tag_remota` **reimplements** the gate's `ls-remote`+`awk` and never calls `verify_pin` — a gate without pin verification passes the test. The test validates the repo's pin, not the gate.
- `t_gate_grava_relatorio_json` does not check the gate's exit — a gate that always writes `{}` (valid JSON) without scanning anything passes.

### 10. LOW — The gate's `fail()` is sourced into the test runner

`harness-basic/tests/test_skill_guard.sh:21` + `harness-basic/scripts/gate-skill-scan.sh:46`

Any future test that triggers `fail()` (e.g. calling `ensure_image`) kills the entire runner with `exit 2` instead of failing a single test. Latent today (no test calls a function that can fail), fragile for evolution.

### 11. LOW — Minor items

- `gate-skill-scan.sh:185-191`: targets starting with `-` are rejected and there is no `--` separator.
- `gate-skill-scan.sh:201, 218`: `mkdir -p "$REPORTS"` and the report write are not checked — if they fail, the gate continues and can approve without writing the audit artifact (the verdict stays correct; it is loss of evidence, not fail-open).
- `read_verdict` (`gate-skill-scan.sh:128-146`): a float score (`"12.5"`) would be blocked as unreadable — fail-closed, but it would break the gate if the scanner ever emits a float (current contract says 0-100 integer).

---

## What I verified and considered correct (review coverage)

- **Exit codes 0/1/2** per contract, empirically validated (real docker: bad fixture → 1, clean skill → 0; fake docker across all branches).
- **Non-numeric score guard** (lines 232-239) works and protects the fall-through it describes — the `t_score_nao_numerico_bloqueia` test is solid (uses fake docker, runs without the image).
- **Fail-closed on failure paths**: empty JSON → block; unreadable JSON (`ERRO*`) → block; missing `python3` → empty verdict → score `""` → guard blocks; timeout exceeded → empty/truncated output → block; `MAX_SCORE=""` is safe (the `:-` applies the default — confirmed by experiment).
- **Timeout**: `-s KILL` + `rc ≥ 124` → `docker rm -f` of the orphan container; `--sig-proxy=false`; the `rc=$?` is captured before any later command — coherent.
- **`${base[@]+"${base[@]}"}`** — correct idiom for an empty array.
- **`report_slug`** (lines 155-157): no path traversal — `tr` removes separators, `sed` trims dots/dashes at the edges; an empty slug falls into an inert `.json`; absolute targets outside `SCAN_ROOT` and URLs produce inert slugs.
- **`discover_skills`**: the `while read` subshell only prints (does not accumulate state) — no state-loss risk; spaces in names survive (`read -r` + quoting in `TARGETS`); fixture excluded (confirmed by execution); `node_modules`/`.git` excluded.
- **Test suite**: 16/16 passing on the current machine with the real docker image.
- **Sourcing for tests**: the `${BASH_SOURCE[0]} != ${0}` guard (lines 180-182) works; the source triggers neither scan nor side effects; no helper collides destructively with `fail()` today.
- **`set -uo pipefail` without `set -e`** is intentional and consistent: all `scan_target` returns and all verdict computation points were mapped; those that could approve improperly block.
- **Remote pin** matches the declared commit (`t_pin_declarado_bate_com_a_tag_remota` passed with network OK).
- **Documentation vs. code divergence** checked: thresholds (50/20), exit codes, flags, and `SKILL_GUARD_REPORTS` are consistent; the real divergences are items 5, 6, and 7 above.

**Review limitation**: I did not test building the image from scratch (already present locally), nor the baseline path inside the container with the real scanner — the prompt marks that behavior as already verified and it was treated as given.