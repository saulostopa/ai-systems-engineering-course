#!/usr/bin/env bash
# proposal-check.sh — valida proposta contra o briefing (comercial).
# Uso: proposal-check.sh <proposta.md> <briefing.md>
# Requisitos do briefing com marcador "- [REQ]" são comparados por palavras-chave.
set -uo pipefail

PROPOSTA="${1:-}"
BRIEFING="${2:-}"
[ -f "$PROPOSTA" ] && [ -f "$BRIEFING" ] || { echo "Uso: proposal-check.sh <proposta.md> <briefing.md>"; exit 1; }

FAILURES=0
ok()   { printf '  [ok]     %s\n' "$1"; }
fail() { printf '  [FAIL]   %s\n' "$1"; FAILURES=$((FAILURES + 1)); }
section() { printf '\n== %s ==\n' "$1"; }

# Palavras que não contam como evidência de resposta (stopwords + verbos de pedido)
STOPWORDS='^(para|com|que|este|esta|nossa|assinatura|incluir|propor|pela|pelo|rede|das|dos|uma|uma)$'

section "Requisitos do briefing (item a item)"
TOTAL_REQ=0
while IFS= read -r req; do
  TOTAL_REQ=$((TOTAL_REQ + 1))
  term=$(echo "$req" | sed -E 's/^- \[REQ\] *//' | cut -c1-60)
  KEYWORDS=$(echo "$req" | tr '[:upper:]' '[:lower:]' | grep -oE '[a-z]{4,}' | grep -vE "$STOPWORDS" || true)
  HITS=0
  for kw in $KEYWORDS; do
    grep -qi "$kw" "$PROPOSTA" && HITS=$((HITS + 1))
  done
  TOTAL_KW=$(echo "$KEYWORDS" | wc -w | tr -d ' ')
  if [ "${TOTAL_KW:-0}" -ge 2 ] && [ "${HITS:-0}" -ge 2 ]; then
    ok "requisito atendido: $term..."
  else
    fail "requisito SEM resposta clara: $term... (palavras-chave: ${HITS:-0}/${TOTAL_KW:-0})"
  fi
done < <(grep -E "^- \[REQ\]" "$BRIEFING" || true)
if [ "${TOTAL_REQ:-0}" -eq 0 ]; then
  echo "  (nenhum requisito marcado - [REQ] no briefing)"
  FAILURES=$((FAILURES + 1))
fi

section "Números com fonte"
# Um número é seguro se a linha tem FONTE, ou a linha anterior/seguinte tem.
SOLTOS=$(awk '
  { lines[NR] = $0 }
  END {
    bad = 0
    for (i = 1; i <= NR; i++) {
      if (lines[i] ~ /[0-9]/ && lines[i] !~ /FONTE:/) {
        before = (i > 1 && lines[i-1] ~ /FONTE:/) ? 1 : 0
        after  = (i < NR && lines[i+1] ~ /FONTE:/) ? 1 : 0
        if (before == 0 && after == 0) bad++
      }
    }
    print bad
  }' "$PROPOSTA")
FONTES=$(grep -c "FONTE:" "$PROPOSTA" || true)
ok "fontes citadas: $FONTES"
if [ "${SOLTOS:-0}" -gt 0 ]; then
  fail "$SOLTOS linha(s) numérica(s) sem FONTE"
else
  ok "nenhum número solto"
fi

section "Revisão cruzada"
if grep -qi "revisor\|revisad" "$PROPOSTA"; then
  ok "revisão registrada no documento"
else
  fail "sem registro de revisão cruzada — peça a um revisor independente"
fi

section "Resultado"
printf '%s — %d falha(s)\n' "$([ "$FAILURES" -eq 0 ] && echo "PROPOSTA APROVADA PARA ENVIO" || echo "PROPOSTA BLOQUEADA")" "$FAILURES"
exit "$FAILURES"