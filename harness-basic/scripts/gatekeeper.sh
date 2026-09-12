#!/usr/bin/env bash
# gatekeeper.sh — pre-commit: bloqueia commits sem feature in_progress.
# Regra (Aula 07): uma feature in_progress por vez; nada de "commit solto".
# Bypass consciente: toque em .harness/skip-gatekeeper (expira em 5 min).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

FLAG=".harness/skip-gatekeeper"
if [ -f "$FLAG" ]; then
  AGE=$(( $(date +%s) - $(stat -c %Y "$FLAG") ))
  if [ "$AGE" -lt 300 ]; then
    echo "[gatekeeper] bypass temporário ativo ($(( 300 - AGE ))s restantes)"
    exit 0
  fi
  rm -f "$FLAG"
fi

[ -f "feature_list.json" ] || { echo "[gatekeeper] BLOQUEADO: feature_list.json ausente — rode ./init.sh"; exit 1; }

ACTIVE=$(node -e "const f=require('./feature_list.json').features;const a=f.filter(x=>x.status==='in_progress');console.log(a.length)" 2>/dev/null || echo "?")

if [ "$ACTIVE" = "?" ]; then
  echo "[gatekeeper] AVISO: não consegui ler feature_list.json (node ausente?) — permitindo, mas valide na mão"
  exit 0
fi

if [ "$ACTIVE" -eq 1 ]; then
  echo "[gatekeeper] OK: 1 feature in_progress"
  exit 0
elif [ "$ACTIVE" -gt 1 ]; then
  echo "[gatekeeper] BLOQUEADO: $ACTIVE features in_progress — mantenha UMA (Aula 06/07)"
  exit 1
else
  echo "[gatekeeper] BLOQUEADO: nenhuma feature in_progress — declare a feature em feature_list.json antes de commitar (Aula 08)"
  exit 1
fi