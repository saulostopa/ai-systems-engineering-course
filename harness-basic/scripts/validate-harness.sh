#!/usr/bin/env bash
# validate-harness.sh — health check do harness instalado (Aula 11).
# Exits non-zero se o harness estiver quebrado. Modelado no factory.
set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
FAILURES=0
WARNINGS=0

ok()   { printf '  [ok]     %s\n' "$1"; }
warn() { printf '  [warn]   %s\n' "$1"; WARNINGS=$((WARNINGS + 1)); }
fail() { printf '  [FAIL]   %s\n' "$1"; FAILURES=$((FAILURES + 1)); }
section() { printf '\n== %s ==\n' "$1"; }
require_file() {
  if [ -f "$1" ]; then ok "existe: $1"; else fail "faltando: $1"; fi
}

section "Arquivos obrigatórios"
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
      if (!Array.isArray(f.features)) throw new Error('sem array features');
      const states = ['not_started','in_progress','blocked','passing'];
      const bad = f.features.filter(x => !states.includes(x.status));
      if (bad.length) throw new Error('estados inválidos: ' + bad.map(b=>b.id).join(','));
      const act = f.features.filter(x => x.status==='in_progress').length;
      if (act > 1) throw new Error(act + ' features in_progress (máx. 1)');
      console.log('  [ok]     JSON válido; ' + f.features.length + ' features; ' + act + ' in_progress');
    " 2>/dev/null && : || { node -e "
      const f = require('./feature_list.json');
      const states = ['not_started','in_progress','blocked','passing'];
      const bad = f.features.filter(x => !states.includes(x.status));
      const act = f.features.filter(x => x.status==='in_progress').length;
      if (bad.length) console.error('estados inválidos: ' + bad.map(b=>b.id).join(','));
      if (act > 1) console.error(act + ' features in_progress');
      process.exit(1);
    " 2>&1 | sed 's/^/  [FAIL]   /'; FAILURES=$((FAILURES + 1)); }
  else
    warn "node ausente — validação de JSON pulada"
  fi
fi

section "Hooks"
HOOKS=$(git config core.hooksPath 2>/dev/null || echo "")
if [ "$HOOKS" = ".githooks" ]; then
  ok "core.hooksPath = .githooks"
else
  warn "core.hooksPath = ${HOOKS:-não configurado} (rode: git config core.hooksPath .githooks)"
fi

section "Resultado"
printf '\n%s — %d falha(s), %d aviso(s)\n' "$( [ "$FAILURES" -eq 0 ] && echo "HARNESS OK" || echo "HARNESS QUEBRADO" )" "$FAILURES" "$WARNINGS"
exit "$FAILURES"