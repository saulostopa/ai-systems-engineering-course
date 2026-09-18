# Independent adversarial review — security gate for skill installation

You are an **independent, adversarial code reviewer**. Your job is to **find
defects**, not to praise. Be specific and skeptical, but do not invent
problems: if something is correct, say it is correct.

## Context

A harness engineering repository (course + working harnesses for Webmotors)
just gained a **security gate for skill installation**.

A "skill" is an instruction package (`SKILL.md` + scripts) that an AI agent
(Claude Code, Cursor, Codex, OpenCode) loads and **executes with implicit
trust**: it enters the context and starts steering the model's behavior, with
no code review, no sandbox, no CI.

The gate runs **NVIDIA SkillSpector** (Apache-2.0, skill security scanner) in
Docker, in static mode, before any skill is installed.

### Scanner behavior (already verified — take as given)

- `skillspector scan <target> --no-llm --format json` prints a JSON report on stdout.
- Scanner exit: `0` if score ≤ 50, `1` if score > 50, `2` on execution error. `RISK_THRESHOLD = 50`.
- The JSON has the shape:
  `{"skill":{...}, "risk_assessment":{"score":0-100,"severity":"LOW|MEDIUM|HIGH|CRITICAL","recommendation":"...","max_issue_severity":"..."}, "issues":[...], "analysis_completeness":{"status":"complete|partial",...}, "metadata":{"skillspector_version":"..."}, "suppressed":[...], "suppressed_count":N}`
- `--baseline <file.yaml>` suppresses already-triaged findings; the scanner excludes the baseline file itself from content analysis.
- The `docker` client **ignores SIGTERM** in this environment (hence the `timeout -s KILL`).

### Intended gate contract

- `gate-skill-scan.sh <target> [<target>...]` — target is a directory, `SKILL.md`, `.zip`, or a git repo URL.
- `gate-skill-scan.sh --all` — all skills in the repository.
- Output: `0` = all approved · `1` = some failed · `2` = execution error.
- Thresholds: **blocks** score > 50, **warns** score > 20, approves the rest.
- **The gate must fail CLOSED**: any doubt, error, timeout, or unreadable report must BLOCK, never approve.

## What to review, in priority order

**1. Fail-OPEN paths.** Walk every return of `scan_target` and every verdict
computation path. Is there any input or failure mode in which a dangerous
skill ends up counted in `PASSED`, or the script exits `0`, instead of being
blocked? Consider: docker absent or failing; a stale local image with the
right tag; malformed, empty, partial, or hostile JSON; the scanner writing
warnings to stdout; targets with spaces, line breaks, globs, or a leading
hyphen; symlinks; interactions with `set -uo pipefail`; the `while read`
subshell in `discover_skills` losing state; `SKILL_GUARD_MAX_SCORE=""`,
negative, or huge.

**2. Bypass.** The `.skill-guard-fixture` marker makes `--all` skip a
directory — can a malicious skill drop this file to hide itself? And the
`.skillspector-baseline.yaml` is read **from inside the very directory being
scanned**: reason carefully about this trust boundary (a hostile skill
shipping its own baseline that suppresses its own findings). Say how severe it
is and what would fix it.

**3. Shell correctness.** Quoting, word splitting, `local` with command
substitution masking the exit status, the `IFS='|' read` parse,
`${target#"$SCAN_ROOT"/}` when the target is absolute outside `SCAN_ROOT` or
relative, `realpath` failure, path traversal in the report path via a forged
target name, `timeout -s KILL` semantics, orphan container cleanup, `mkdir`
failure.

**4. Test quality.** For each test: does it exercise the script's real code
(and not a reimplementation of the logic inside the test itself)? Would it
**fail** if the corresponding behavior were reverted? Point out any test that
would pass against a broken implementation. The test file `source`s the gate —
check that this does not trigger side effects and that no helper collides
destructively (the gate defines `fail()` which terminates the process).

**5. Documentation vs. code divergence.** Any claim in the documentation that
the code does not fulfill (thresholds, exit codes, flags, paths, the pin,
what the baseline does).

## Response format

First, a **list of findings ordered from most to least severe**. For each:
`file:line`, what is wrong, a **concrete failure scenario** (specific
input/state → wrong result), and the severity.

Then, separately, **what you verified and considered correct**, so I know the
coverage of your review.

---

## File 1/3 — `harness-basic/scripts/gate-skill-scan.sh` (the gate, main focus)

```bash
#!/usr/bin/env bash
# gate-skill-scan.sh — skill installation gate (SkillSpector).
#
# Rule: no skill enters the repository without passing the scanner. A skill
# is code the agent executes with implicit trust — it is the cheapest supply
# chain surface to attack and the most expensive to audit afterwards.
#
# Engine: NVIDIA/SkillSpector (Apache-2.0), pinned by tag and run in Docker
# so it does not depend on the local Python. Static analysis only (--no-llm):
# the verdict must be deterministic, reproducible in CI, and valid offline.
#
# Usage:
#   gate-skill-scan.sh <target> [<target>...]   # directory, SKILL.md, .zip, git repo
#   gate-skill-scan.sh --all                    # all skills in the repository
#
# Output: 0 = all approved · 1 = some failed · 2 = execution error.
#
# Variables:
#   SKILL_GUARD_VERSION    SkillSpector tag (default: v2.11.2)
#   SKILL_GUARD_MAX_SCORE  maximum accepted score (default: 50 — the tool's threshold)
#   SKILL_GUARD_WARN_SCORE score from which it warns (default: 20)
#   SKILL_GUARD_REPORTS    JSON reports directory (default: .harness/skill-scans)
#   SKILL_GUARD_TIMEOUT    deadline per target, in seconds (default: 900). Exceeding it
#                          blocks the target — the gate fails closed.
set -uo pipefail

VERSION="${SKILL_GUARD_VERSION:-v2.11.2}"
# Supply chain pin: the tag above must point to this commit. A rewritten
# remote tag changes the scanner without changing the name — the gate refuses
# if they diverge.
PINNED_SHA="69dcdfb74487d361ba4c811d088cfdea2ff3a9dc"
IMAGE="skillspector:${VERSION}"
REPO_URL="https://github.com/NVIDIA/SkillSpector.git"

MAX_SCORE="${SKILL_GUARD_MAX_SCORE:-50}"
WARN_SCORE="${SKILL_GUARD_WARN_SCORE:-20}"
TIMEOUT="${SKILL_GUARD_TIMEOUT:-900}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# When installed in a target project, the scan root is the project root.
SCAN_ROOT="$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null || echo "$ROOT")"
REPORTS="${SKILL_GUARD_REPORTS:-$SCAN_ROOT/.harness/skill-scans}"

ok()    { printf '  [ok]     %s\n' "$1"; }
warn()  { printf '  [warn]   %s\n' "$1"; }
block() { printf '  [BLOCK]  %s\n' "$1"; }
fail()  { printf '[skill-guard] ERROR: %s\n' "$1" >&2; exit 2; }
section() { printf '\n== %s ==\n' "$1"; }

# --- engine ------------------------------------------------------------------

ensure_image() {
  if docker image inspect "$IMAGE" >/dev/null 2>&1; then
    return 0
  fi
  command -v docker >/dev/null 2>&1 || fail "docker missing — install docker or run skillspector natively"
  printf '[skill-guard] image %s missing — building from %s#%s (1-2 min)\n' "$IMAGE" "$REPO_URL" "$VERSION"
  docker build -q -t "$IMAGE" "${REPO_URL}#${VERSION}" >/dev/null \
    || fail "failed to build the SkillSpector image"
  ok "image built: $IMAGE"
}

# Confirms the tag still points to the pinned commit. Without network, warn
# and continue — the local image was built from a previously verified pin.
verify_pin() {
  local refs sha
  # An annotated tag resolves to refs/tags/X^{} (the commit); a lightweight tag
  # only has refs/tags/X. We ask for both and keep the peeled form when it
  # exists.
  refs="$(git ls-remote "$REPO_URL" "refs/tags/${VERSION}" "refs/tags/${VERSION}^{}" 2>/dev/null)"
  sha="$(printf '%s\n' "$refs" | awk '/\^\{\}$/ {print $1; found=1} END {exit !found}')" \
    || sha="$(printf '%s\n' "$refs" | awk 'NR==1 {print $1}')"
  if [ -z "$sha" ]; then
    warn "could not verify the pin (no network?) — using local image $IMAGE"
    return 0
  fi
  if [ "$sha" != "$PINNED_SHA" ]; then
    block "divergent pin: ${VERSION} points to ${sha}, expected ${PINNED_SHA}"
    fail "the SkillSpector tag was rewritten — review before trusting the scanner"
  fi
  ok "pin confirmed: ${VERSION} = ${PINNED_SHA:0:12}"
}

# Runs the scanner on a target and returns the JSON on stdout.
# The timeout is part of the gate, not a convenience: a large package (many
# files, examples with thousands of lines) takes minutes, and a scan that
# never returns would be a gate that never blocks. Exceeding the deadline
# fails CLOSED — whoever handles the empty output blocks the target.
scan_target() {
  local target="$1" rel cname rc base=()
  cname="skillguard-$$-${RANDOM}"

  # Baseline per skill, not global: a .skillspector-baseline.yaml inside the
  # skill directory suppresses only that skill's false positives, and stays
  # reviewable in PR next to the code it forgives. A global baseline would
  # disarm the rule for all the others — which is how a gate dies.
  if [ -e "$target" ] && [ -f "$target/.skillspector-baseline.yaml" ]; then
    base=(--baseline "./${target#"$SCAN_ROOT"/}/.skillspector-baseline.yaml")
  fi

  # `-s KILL` is not overkill, it is what makes the deadline hold. The docker
  # client ignores SIGTERM: with the default signal the `timeout` returns 124
  # at the deadline but the scan runs to the end and writes the whole report —
  # a deadline that limits nothing. With SIGKILL the client dies at the agreed
  # second, the output stays empty or truncated, and the caller blocks the
  # target.
  # `--sig-proxy=false` prevents the signal from being forwarded to the
  # process inside the container instead of the client; `docker rm -f` takes
  # down the orphan container.
  if [ -e "$target" ]; then
    # Local path: mounts the repo root and references the target relative to it.
    rel="$(realpath --relative-to="$SCAN_ROOT" "$target")"
    timeout -s KILL "$TIMEOUT" docker run --rm --name "$cname" --sig-proxy=false \
      -v "$SCAN_ROOT:/scan" "$IMAGE" scan "./$rel" --no-llm --format json ${base[@]+"${base[@]}"} 2>/dev/null
  else
    # Git repo URL or zip: the scanner fetches on its own, without mounting anything.
    timeout -s KILL "$TIMEOUT" docker run --rm --name "$cname" --sig-proxy=false \
      "$IMAGE" scan "$target" --no-llm --format json 2>/dev/null
  fi
  rc=$?

  # 124 = deadline exceeded. The container survives the dead client: kill it.
  if [ "$rc" -ge 124 ]; then
    docker rm -f "$cname" >/dev/null 2>&1
  fi
}

# --- verdict ----------------------------------------------------------------

# Reads the scanner JSON and prints: score|severity|recommendation|n_issues|complete|worst
read_verdict() {
  python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print("ERRO|%s" % e)
    sys.exit(3)
r = d.get("risk_assessment", {})
c = d.get("analysis_completeness", {})
print("|".join([
    str(r.get("score", "?")),
    str(r.get("severity", "?")),
    str(r.get("recommendation", "?")),
    str(len(d.get("issues", []))),
    str(c.get("status", "?")),
    str(r.get("max_issue_severity", "NONE")),
    str(d.get("metadata", {}).get("skillspector_version", "?")),
]))
'
}

# Report name: derived from the PATH, not the basename. .claude/skills/agenfk
# and .agents/skills/agenfk are two distinct copies of the same skill and each
# one needs its own report — with the basename, the second would overwrite the
# first. Leading dots are stripped too: the skills live in .claude/ and
# .agents/, and without that the report becomes a hidden file — an `ls` on the
# reports directory would show nothing, which is the same as having no report.
report_slug() {
  printf '%s' "${1#"$SCAN_ROOT"/}" | tr -c 'A-Za-z0-9._-' '-' | sed 's/^[.-]*//;s/[.-]*$//'
}

# --- discovery --------------------------------------------------------------

# Discovers the repository skills. A directory with the .skill-guard-fixture
# marker is skipped: they are deliberately bad fixtures used to prove the gate
# blocks. Without this explicit escape, the repository's own gate would fail
# forever — and the escape is a versioned file, reviewable in PR, not a hidden
# path inside the script.
discover_skills() {
  local dir
  find "$SCAN_ROOT" -name SKILL.md \
    -not -path '*/node_modules/*' \
    -not -path '*/.git/*' \
    -print0 | xargs -0 -n1 dirname | sort -u | while IFS= read -r dir; do
      [ -f "$dir/.skill-guard-fixture" ] || printf '%s\n' "$dir"
    done
}

# --- main -------------------------------------------------------------------

# Only runs when the script is invoked; when sourced, it exposes the functions
# to the test (harness-basic/tests/test_skill_guard.sh) without triggering any
# scan.
if [ "${BASH_SOURCE[0]}" != "${0}" ]; then
  return 0
fi

TARGETS=()
for arg in "$@"; do
  case "$arg" in
    --all) while IFS= read -r d; do TARGETS+=("$d"); done < <(discover_skills) ;;
    -*)    fail "unknown option: $arg" ;;
    *)     TARGETS+=("$arg") ;;
  esac
done

[ "${#TARGETS[@]}" -gt 0 ] || {
  echo "Usage: gate-skill-scan.sh <target> [<target>...] | --all"
  exit 2
}

section "SkillSpector ${VERSION} — skill installation gate"
verify_pin
ensure_image
mkdir -p "$REPORTS"

BLOCKED=0
WARNED=0
PASSED=0

section "Scan (${#TARGETS[@]} target(s), static)"
for target in "${TARGETS[@]}"; do
  name="$(basename "$target")"
  report="$REPORTS/$(report_slug "$target").json"

  json="$(scan_target "$target")"
  if [ -z "$json" ]; then
    block "$name — no report (timeout of ${TIMEOUT}s or scanner failure) — blocked as a precaution"
    BLOCKED=$((BLOCKED + 1))
    continue
  fi
  printf '%s' "$json" > "$report"

  verdict="$(printf '%s' "$json" | read_verdict)"
  case "$verdict" in
    ERRO*) block "$name — unreadable report: ${verdict#ERRO|}"; BLOCKED=$((BLOCKED + 1)); continue ;;
  esac

  IFS='|' read -r score severity recommendation issues complete worst _ver <<< "$verdict"

  label="$name — score ${score}/100 (${severity}), ${issues} finding(s), coverage ${complete}"

  # A non-numeric score blocks. Without this guard the `-gt` below errors
  # ("integer expression expected"), both branches return false and the target
  # falls into the else — that is, a report without a score would be APPROVED.
  # A gate must fail closed.
  case "$score" in
    ''|*[!0-9]*)
      block "$name — report without a usable score ('${score}') — blocked as a precaution"
      printf '           report: %s\n' "$report"
      BLOCKED=$((BLOCKED + 1))
      continue
      ;;
  esac

  if [ "$score" -gt "$MAX_SCORE" ]; then
    block "$label — worst finding: ${worst}"
    printf '           report: %s\n' "$report"
    BLOCKED=$((BLOCKED + 1))
  elif [ "$score" -gt "$WARN_SCORE" ]; then
    warn "$label — review before installing"
    printf '           report: %s\n' "$report"
    WARNED=$((WARNED + 1))
  else
    ok "$label"
    PASSED=$((PASSED + 1))
  fi
done

section "Result"
printf 'threshold: blocks score > %s · warns score > %s · mode: static (--no-llm)\n' "$MAX_SCORE" "$WARN_SCORE"
printf 'reports: %s\n' "$REPORTS"
printf '\n%s — %d approved, %d with warning, %d blocked\n' \
  "$( [ "$BLOCKED" -eq 0 ] && echo "SKILL GUARD OK" || echo "SKILL GUARD BLOQUEOU" )" \
  "$PASSED" "$WARNED" "$BLOCKED"

# A clean static scan is not the same as an audited skill: static mode does
# not judge intent. The verdict below covers known patterns, not semantics.
[ "$BLOCKED" -eq 0 ] || exit 1
exit 0
```

## File 2/3 — `harness-basic/tests/test_skill_guard.sh` (the tests)

```bash
#!/usr/bin/env bash
# test_skill_guard.sh — tests for the skill installation gate.
#
# The logic tests (verdict, discovery, report name) always run. The ones that
# exercise the real scanner need the Docker image and are skipped with a
# warning when it is absent — but they never pass silently.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATE="$ROOT/scripts/gate-skill-scan.sh"
REPO="$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null || echo "$ROOT")"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0; FAIL=0; SKIP=0
_pass() { printf 'PASS %s\n' "$1"; PASS=$((PASS + 1)); }
_fail() { printf 'FAIL %s — %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }
_skip() { printf 'SKIP %s — %s\n' "$1" "$2"; SKIP=$((SKIP + 1)); }

# shellcheck source=../scripts/gate-skill-scan.sh
source "$GATE"

has_image() { docker image inspect "$IMAGE" >/dev/null 2>&1; }

# --- verdict ----------------------------------------------------------------

t_read_verdict_parseia_relatorio_valido() {
  local out
  out="$(printf '%s' '{"risk_assessment":{"score":42,"severity":"MEDIUM","recommendation":"CAUTION","max_issue_severity":"HIGH"},"issues":[1,2,3],"analysis_completeness":{"status":"partial"},"metadata":{"skillspector_version":"2.11.2"}}' | read_verdict)"
  [ "$out" = "42|MEDIUM|CAUTION|3|partial|HIGH|2.11.2" ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "unexpected verdict: $out"
}

# A truncated report (timeout mid-stream) must not become an approval.
t_read_verdict_rejeita_json_truncado() {
  local out
  out="$(printf '%s' '{"risk_assessment":{"score":0,' | read_verdict)"
  case "$out" in
    ERRO*) _pass "${FUNCNAME[0]}" ;;
    *)     _fail "${FUNCNAME[0]}" "truncated JSON should become ERRO, got: $out" ;;
  esac
}

t_read_verdict_sem_campos_nao_inventa_score() {
  local out
  out="$(printf '%s' '{}' | read_verdict)"
  case "$out" in
    "?|"*) _pass "${FUNCNAME[0]}" ;;
    *)     _fail "${FUNCNAME[0]}" "expected score '?', got: $out" ;;
  esac
}

# --- discovery --------------------------------------------------------------

t_discover_pula_fixture_marcada() {
  local encontrados
  encontrados="$(discover_skills)"
  if printf '%s\n' "$encontrados" | grep -q 'fixture-reprovada'; then
    _fail "${FUNCNAME[0]}" "fixture marked with .skill-guard-fixture appeared in --all"
  else
    _pass "${FUNCNAME[0]}"
  fi
}

t_discover_acha_as_skills_do_repo() {
  local n
  n="$(discover_skills | wc -l)"
  [ "$n" -gt 10 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "expected >10 discovered skills, got $n"
}

# --- report name ------------------------------------------------------------

# .claude/skills/agenfk and .agents/skills/agenfk have the same basename: with
# the basename, the second would overwrite the first's report.
t_slug_distingue_mesmo_basename() {
  local a b
  a="$(report_slug "$SCAN_ROOT/.claude/skills/agenfk")"
  b="$(report_slug "$SCAN_ROOT/.agents/skills/agenfk")"
  if [ "$a" = "$b" ]; then
    _fail "${FUNCNAME[0]}" "slugs collided: $a"
  elif [ "$a" = "agenfk" ] || [ "$b" = "agenfk" ]; then
    _fail "${FUNCNAME[0]}" "slug fell back to basename: $a / $b"
  else
    _pass "${FUNCNAME[0]}"
  fi
}

t_slug_preserva_o_caminho_da_skill() {
  local s
  s="$(report_slug "$SCAN_ROOT/skills-artifacts/feature-quiz")"
  [ "$s" = "skills-artifacts-feature-quiz" ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "expected skills-artifacts-feature-quiz, got: $s"
}

# The skills live in .claude/ and .agents/: without stripping the leading dot
# the report becomes a hidden file and disappears from an `ls` on the
# directory.
t_slug_nao_gera_arquivo_oculto() {
  local a b
  a="$(report_slug "$SCAN_ROOT/.agents/skills/agenfk")"
  b="$(report_slug "$SCAN_ROOT/.claude/skills/agenfk")"
  case "$a$b" in
    .*) _fail "${FUNCNAME[0]}" "slug starts with a dot: $a / $b" ;;
    *)  [ "$a" != "$b" ] \
          && _pass "${FUNCNAME[0]}" \
          || _fail "${FUNCNAME[0]}" "slugs collided: $a" ;;
  esac
}

# --- exit codes -------------------------------------------------------------

t_opcao_invalida_sai_2() {
  "$GATE" --nao-existe >/dev/null 2>&1
  [ "$?" -eq 2 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "expected exit 2"
}

t_sem_alvo_sai_2() {
  "$GATE" >/dev/null 2>&1
  [ "$?" -eq 2 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "expected exit 2"
}

# --- real gate (needs the image) -------------------------------------------

t_gate_bloqueia_skill_ruim() {
  has_image || { _skip "${FUNCNAME[0]}" "image $IMAGE missing"; return; }
  SKILL_GUARD_REPORTS="$TMP/r1" "$GATE" "$REPO/pilots/skillspector-demo/fixture-reprovada" >/dev/null 2>&1
  [ "$?" -eq 1 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "bad fixture should exit 1"
}

t_gate_aprova_skill_limpa() {
  has_image || { _skip "${FUNCNAME[0]}" "image $IMAGE missing"; return; }
  SKILL_GUARD_REPORTS="$TMP/r2" "$GATE" "$REPO/skills-artifacts/feature-quiz" >/dev/null 2>&1
  [ "$?" -eq 0 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "clean skill should exit 0"
}

# The deadline exists to block, not to warn: exceeding it fails CLOSED.
t_timeout_falha_fechado() {
  has_image || { _skip "${FUNCNAME[0]}" "image $IMAGE missing"; return; }
  SKILL_GUARD_TIMEOUT=1 SKILL_GUARD_REPORTS="$TMP/r3" \
    "$GATE" "$REPO/skills-artifacts/feature-quiz" >/dev/null 2>&1
  [ "$?" -eq 1 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "timeout should block (exit 1), not approve"
}

t_gate_grava_relatorio_json() {
  has_image || { _skip "${FUNCNAME[0]}" "image $IMAGE missing"; return; }
  SKILL_GUARD_REPORTS="$TMP/r4" "$GATE" "$REPO/skills-artifacts/feature-quiz" >/dev/null 2>&1
  local f
  f="$(find "$TMP/r4" -name '*.json' | head -1)"
  if [ -n "$f" ] && python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>/dev/null; then
    _pass "${FUNCNAME[0]}"
  else
    _fail "${FUNCNAME[0]}" "JSON report was not written or is invalid"
  fi
}

# A syntactically valid report without a score: the gate must BLOCK, not fall
# into the approval branch because the numeric comparison failed.
t_score_nao_numerico_bloqueia() {
  local fake="$TMP/fakebin" out
  mkdir -p "$fake"
  # fake docker: returns a valid JSON report, but without risk_assessment
  cat > "$fake/docker" <<'SH'
#!/usr/bin/env bash
case "$1" in
  image|rm) exit 0 ;;
esac
printf '%s' '{"issues":[],"analysis_completeness":{"status":"complete"},"metadata":{}}'
SH
  chmod +x "$fake/docker"
  out="$(PATH="$fake:$PATH" SKILL_GUARD_REPORTS="$TMP/r5" \
    "$GATE" "$REPO/skills-artifacts/feature-quiz" 2>&1)"
  local rc=$?
  if [ "$rc" -eq 1 ] && printf '%s' "$out" | grep -q 'without a usable score'; then
    _pass "${FUNCNAME[0]}"
  else
    _fail "${FUNCNAME[0]}" "expected a block for missing score (exit 1), got exit $rc"
  fi
}

# --- pin --------------------------------------------------------------------

t_pin_declarado_bate_com_a_tag_remota() {
  local refs sha
  refs="$(git ls-remote "$REPO_URL" "refs/tags/${VERSION}" "refs/tags/${VERSION}^{}" 2>/dev/null)"
  [ -n "$refs" ] || { _skip "${FUNCNAME[0]}" "no network"; return; }
  sha="$(printf '%s\n' "$refs" | awk '/\^\{\}$/ {print $1; found=1} END {exit !found}')" \
    || sha="$(printf '%s\n' "$refs" | awk 'NR==1 {print $1}')"
  [ "$sha" = "$PINNED_SHA" ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "tag $VERSION = $sha, declared pin = $PINNED_SHA"
}

# --- execution --------------------------------------------------------------

for t in $(declare -F | awk '{print $3}' | grep '^t_'); do "$t"; done

printf '\n== %d/%d passed' "$PASS" "$((PASS + FAIL))"
[ "$SKIP" -gt 0 ] && printf ' (%d skipped)' "$SKIP"
printf '\n'
exit "$FAIL"
```

## File 3/3 — new snippet of `harness-basic/scripts/validate-harness.sh`

This snippet was added to an existing health check. It does NOT run the
scanner (that would be too slow): it only verifies that every skill declared
in `skills-lock.json` carries the verdict that approved it.

```bash
section "Installed skills (skill-guard)"
# Cheap check: every declared skill must carry the verdict that approved it.
# The scan itself runs in gate-skill-scan.sh — building the scanner image on
# every health check would be far too slow to use.
# When installed in a target project, the lock sits next to this directory. In
# this repo (harness-basic is a subfolder) it sits at the git root — without
# this fallback the check would go inert exactly where the skills live.
LOCK="skills-lock.json"
[ -f "$LOCK" ] || LOCK="$(git rev-parse --show-toplevel 2>/dev/null)/skills-lock.json"

if [ -f "$LOCK" ]; then
  if command -v node >/dev/null 2>&1; then
    # Node prints a single line: "OK <n>" or "SEM <names>". The names of the
    # skills without a verdict are the only actionable information in the
    # failure, so they must survive until the message — they cannot be
    # discarded.
    LOCK_OUT="$(node -e "
      const l = require(process.argv[1]);
      const skills = Object.entries(l.skills || {});
      const sem = skills.filter(([,s]) => !s.scanVerdict).map(([n]) => n);
      if (sem.length) { console.log('SEM ' + sem.join(', ')); }
      else { console.log('OK ' + skills.length); }
    " "$LOCK" 2>/dev/null)"
    case "${LOCK_OUT:-}" in
      "OK 0")  ok "no third-party skill declared" ;;
      "OK "*)  ok "${LOCK_OUT#OK } skill(s) with scanVerdict registered" ;;
      "SEM "*) fail "no scanVerdict in skills-lock.json: ${LOCK_OUT#SEM } — run scripts/gate-skill-scan.sh and register the verdict" ;;
      *)       fail "skills-lock.json unreadable or invalid" ;;
    esac
  else
    warn "node missing — scanVerdict check skipped"
  fi
else
  ok "no skills-lock.json (no third-party skill installed)"
fi
```