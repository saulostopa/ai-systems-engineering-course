#!/usr/bin/env bash
# log-event.sh — registra fricção/evento do harness (Aula 11).
# Uso: ./scripts/log-event.sh <categoria> <mensagem>
# Ex.: ./scripts/log-event.sh friction "agente travou 3x no mesmo passo"
set -uo pipefail

CAT="${1:-event}"
MSG="${2:-}"

mkdir -p .harness/logs
LOG=".harness/logs/$(date +%Y-%m).md"

[ -f "$LOG" ] || printf '# Log do harness — %s\n\n' "$(date +%Y-%m)" > "$LOG"

printf -- '- %s `%s`: %s\n' "$(date -Iseconds)" "$CAT" "$MSG" >> "$LOG"
echo "[log-event] registrado em $LOG"