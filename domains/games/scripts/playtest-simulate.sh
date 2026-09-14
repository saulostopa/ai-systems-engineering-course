#!/usr/bin/env bash
# playtest-simulate.sh — playteste simulado de uma feature (Aula 10: o "E2E"
# do jogo). Simula variações do fluxo e pontua critérios de aceite do design doc.
# Uso: playtest-simulate.sh <design-doc.md> [--verbose]
set -uo pipefail

DOC="${1:-}"
[ -f "$DOC" ] || { echo "Uso: playtest-simulate.sh <design-doc.md>"; exit 1; }

section() { printf '\n== %s ==\n' "$1"; }
ok()   { printf '  [ok]     %s\n' "$1"; }
fail() { printf '  [FAIL]   %s\n' "$1"; FAILURES=$((FAILURES + 1)); }
FAILURES=0

section "Cenários simulados (variações de jogador)"

# Cenário 1: jogador novo (nunca viu a mecânica)
grep -qi "persona" "$DOC" && ok "persona definida — simulação de jogador novo possível" \
  || fail "sem persona no design doc — simulação cega"

# Cenário 2: loop completo (input -> regra -> feedback)
grep -qi "feedback" "$DOC" && ok "feedback descrito — loop fechado" \
  || fail "sem feedback descrito — mecânica sem fechamento"

# Cenário 3: economia (se aplicável)
if grep -qi "economia" "$DOC"; then
  NUMBERS=$(grep -oE '[0-9]{2,}' "$DOC" | wc -l)
  [ "$NUMBERS" -ge 3 ] && ok "economia com valores ($NUMBERS números) — consistência simulável" \
    || fail "economia citada mas sem valores suficientes (>=3)"
fi

# Cenário 4: critérios de aceite
grep -qiE "verificacao|aceit" "$DOC" && ok "critérios de aceite presentes — playteste tem alvo" \
  || fail "sem critérios de aceite no doc — playteste sem veredito"

section "Resultado do playteste simulado"
printf '%s — %d falha(s)\n' "$([ "$FAILURES" -eq 0 ] && echo "PLAYTESTE ACEITO" || echo "PLAYTESTE REJEITADO")" "$FAILURES"
exit "$FAILURES"