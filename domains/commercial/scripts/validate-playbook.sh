#!/usr/bin/env bash
# validate-playbook.sh — saúde do playbook de domínio (Aula 11)
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
FAILURES=0
ok()   { printf '  [ok]     %s\n' "$1"; }
fail() { printf '  [FAIL]   %s\n' "$1"; FAILURES=$((FAILURES + 1)); }
section() { printf '\n== %s ==\n' "$1"; }

section "Estrutura obrigatória"
for f in AGENTS.md feature_list.json policies/scope-control.md policies/definition-of-done.md policies/evidence-required.md; do
  [ -f "$f" ] && ok "existe: $f" || fail "faltando: $f"
done

section "feature_list.json"
if [ -f "feature_list.json" ] && command -v node >/dev/null 2>&1; then
  node -e "const f=require('./feature_list.json'); if(!Array.isArray(f.features)) throw new Error('sem features'); const act=f.features.filter(x=>x.status==='in_progress').length; if(act>1) throw new Error(act+' in_progress'); console.log('  [ok]     JSON válido; ' + f.features.length + ' features')" 2>&1 | head -2 \
    && : || { echo "  [FAIL]   feature_list.json inválido"; FAILURES=$((FAILURES + 1)); }
fi

section "Skills"
SKILLS=$(ls skills/*/SKILL.md 2>/dev/null | wc -l)
if [ "$SKILLS" -gt 0 ]; then
  ok "$SKILLS skill(s) encontrada(s)"
else
  fail "nenhuma skill em skills/*/SKILL.md (o playbook precisa de ao menos uma)"
fi

printf '\n%s — %d falha(s)\n' "$([ "$FAILURES" -eq 0 ] && echo "PLAYBOOK OK" || echo "PLAYBOOK QUEBRADO")" "$FAILURES"
exit "$FAILURES"
