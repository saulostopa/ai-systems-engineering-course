#!/usr/bin/env bash
# validate-harness.sh — health check of the installed harness (Lesson 11).
# Exits non-zero if the harness is broken. Modeled on the factory.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
FAILURES=0
WARNINGS=0

ok()   { printf '  [ok]     %s\n' "$1"; }
warn() { printf '  [warn]   %s\n' "$1"; WARNINGS=$((WARNINGS + 1)); }
fail() { printf '  [FAIL]   %s\n' "$1"; FAILURES=$((FAILURES + 1)); }
section() { printf '\n== %s ==\n' "$1"; }
require_file() {
  if [ -f "$1" ]; then ok "present: $1"; else fail "missing: $1"; fi
}

section "Required files"
for f in AGENTS.md feature_list.json claude-progress.md session-handoff.md init.sh; do
  require_file "$f"
done
require_file "policies/definition-of-done.md"
require_file "policies/scope-control.md"
require_file "policies/evidence-required.md"

section "feature_list.json"
if [ -f "feature_list.json" ]; then
  if command -v node >/dev/null 2>&1; then
    node -e "
      const f = require('./feature_list.json');
      if (!Array.isArray(f.features)) throw new Error('features array missing');
      const states = ['not_started','in_progress','blocked','passing'];
      const bad = f.features.filter(x => !states.includes(x.status));
      if (bad.length) throw new Error('invalid states: ' + bad.map(b=>b.id).join(','));
      const act = f.features.filter(x => x.status==='in_progress').length;
      if (act > 1) throw new Error(act + ' features in_progress (max 1)');
      console.log('  [ok]     valid JSON; ' + f.features.length + ' features; ' + act + ' in_progress');
    " 2>/dev/null && : || { node -e "
      const f = require('./feature_list.json');
      const states = ['not_started','in_progress','blocked','passing'];
      const bad = f.features.filter(x => !states.includes(x.status));
      const act = f.features.filter(x => x.status==='in_progress').length;
      if (bad.length) console.error('invalid states: ' + bad.map(b=>b.id).join(','));
      if (act > 1) console.error(act + ' features in_progress');
      process.exit(1);
    " 2>&1 | sed 's/^/  [FAIL]   /'; FAILURES=$((FAILURES + 1)); }
  else
    warn "node missing — JSON validation skipped"
  fi
fi

section "Installed skills (skill-guard)"
# Cheap check: every declared skill must carry the verdict that approved it.
# The scan itself runs in gate-skill-scan.sh — building the scanner image on
# every health check would be too slow to be usable.
# Installed in a target project, the lock sits next to this directory. In this
# repo (harness-basic is a subfolder) it sits at the git root — without this
# fallback the check would be inert exactly where the skills live.
# SKILL_GUARD_LOCK exists so tests can point the check at a fixture lock and
# exercise THIS script, instead of reimplementing the logic inside the test.
LOCK="${SKILL_GUARD_LOCK:-$ROOT/skills-lock.json}"
[ -f "$LOCK" ] || LOCK="$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null)/skills-lock.json"

if [ -f "$LOCK" ]; then
  if command -v node >/dev/null 2>&1; then
    # Node prints a single line: "OK <n>" or "SEM <names>". The names of the
    # skills without a verdict are the only actionable info of the failure, so
    # they must survive into the message — they cannot be discarded.
    LOCK_OUT="$(node -e "
      const l = require(process.argv[1]);
      const skills = Object.entries(l.skills || {});
      const sem = skills.filter(([,s]) => !s.scanVerdict).map(([n]) => n);
      // Presence is not enough: a verdict above the threshold recorded in the
      // lock would make has-scanVerdict a synonym of passed-the-gate.
      const MAX = Number(process.env.SKILL_GUARD_MAX_SCORE || 50);
      const ruins = skills
        .filter(([,s]) => s.scanVerdict && Number(s.scanVerdict.score) > MAX)
        .map(([n,s]) => n + ' (' + s.scanVerdict.score + '/100)');
      if (sem.length) { console.log('SEM ' + sem.join(', ')); }
      else if (ruins.length) { console.log('RUIM ' + ruins.join(', ')); }
      else { console.log('OK ' + skills.length); }
    " "$LOCK" 2>/dev/null)"
    case "${LOCK_OUT:-}" in
      "OK 0")  ok "no third-party skill declared" ;;
      "OK "*)  ok "${LOCK_OUT#OK } skill(s) with a recorded scanVerdict" ;;
      "SEM "*)  fail "no scanVerdict in skills-lock.json: ${LOCK_OUT#SEM } — run scripts/gate-skill-scan.sh --record and record the verdict" ;;
      "RUIM "*) fail "scanVerdict above the threshold in skills-lock.json: ${LOCK_OUT#RUIM } — the skill did not pass the gate" ;;
      *)       fail "skills-lock.json unreadable or invalid" ;;
    esac
  else
    warn "node missing — scanVerdict check skipped"
  fi
else
  ok "no skills-lock.json (no third-party skill installed)"
fi

section "Local patches on third-party skills"
# A local patch only counts while applied. Reinstalling the skill silently
# discards it — and without this check skills-lock.json would keep claiming a
# fix that no longer exists. Each patch declares what must be present
# (verifyContains) and what must not come back (verifyAbsent).
if [ -f "$LOCK" ] && command -v node >/dev/null 2>&1; then
  PATCH_OUT="$(node -e "
    const l = require(process.argv[1]);
    const fs = require('fs'), path = require('path');
    const root = path.dirname(process.argv[1]);
    const out = [];
    let n = 0;
    for (const [name, s] of Object.entries(l.skills || {})) {
      for (const p of (s.localPatches || [])) {
        n++;
        const f = path.join(root, p.verifyFile || '');
        if (!p.verifyFile || !fs.existsSync(f)) { out.push(name + ': file missing (' + p.verifyFile + ')'); continue; }
        const txt = fs.readFileSync(f, 'utf8');
        if (p.verifyContains && !txt.includes(p.verifyContains)) out.push(name + ': patch lost — missing ' + p.verifyContains);
        else if (p.verifyAbsent && txt.includes(p.verifyAbsent)) out.push(name + ': patch reverted — ' + p.verifyAbsent + ' is back');
      }
    }
    console.log(out.length ? 'QUEBRADO ' + out.join('; ') : 'OK ' + n);
  " "$LOCK" 2>/dev/null)"
  case "${PATCH_OUT:-}" in
    "OK 0")       ok "no local patch declared" ;;
    "OK "*)       ok "${PATCH_OUT#OK } local patch(es) still applied" ;;
    "QUEBRADO "*) fail "${PATCH_OUT#QUEBRADO } — reapply the patch and run scripts/gate-skill-scan.sh" ;;
    *)            warn "could not verify the local patches" ;;
  esac
elif [ -f "$LOCK" ]; then
  # Without node this section would go silent, and silence in a health check
  # reads as approval — the patch could vanish without anyone noticing.
  warn "node missing — local patch check skipped"
fi

section "Hooks"
HOOKS=$(git config core.hooksPath 2>/dev/null || echo "")
if [ "$HOOKS" = ".githooks" ]; then
  ok "core.hooksPath = .githooks"
else
  warn "core.hooksPath = ${HOOKS:-not configured} (run: git config core.hooksPath .githooks)"
fi

section "Result"
printf '\n%s — %d failure(s), %d warning(s)\n' "$( [ "$FAILURES" -eq 0 ] && echo "HARNESS OK" || echo "HARNESS BROKEN" )" "$FAILURES" "$WARNINGS"
exit "$FAILURES"
