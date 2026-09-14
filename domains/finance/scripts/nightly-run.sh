#!/usr/bin/env bash
# nightly-run.sh — pipeline noturno do Finance Harness (Aula 13: loop autônomo).
# Consulta o contexto, gera o relatório com fontes e publica — sem humano.
# Uso: ./nightly-run.sh <area_root> [--questions "pergunta 1 | pergunta 2"]
# Crontab:  0 3 * * * /caminho/domains/finance/scripts/nightly-run.sh /caminho/area_context >> /var/log/harness-finance.log 2>&1
set -uo pipefail

AREA_ROOT="${1:-}"
[ -d "$AREA_ROOT" ] || { echo "Uso: nightly-run.sh <area_root>"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAYBOOK="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../" && pwd)"
# Motor Area Copilot: adiciona os pacotes ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH:-}:$REPO_ROOT/area-copilot:$REPO_ROOT/rag-harness"
DATE="$(date +%Y-%m-%d)"
OUT="$PLAYBOOK/relatorios/$DATE-resumo.md"
mkdir -p "$PLAYBOOK/relatorios"

DEFAULT_QUESTIONS="quais os totais de meta_vendas e veiculos_vendidos do mes mais recente | existem dados faltantes nas planilhas | houve divergencia entre esperado e real"
QUESTIONS="${HARNESS_QUESTIONS:-$DEFAULT_QUESTIONS}"

echo "== nightly-run: $(date -Iseconds)"
echo "== indexando contexto..."
python3 -m area_harness index "$AREA_ROOT" --verbose 2>/dev/null || {
  echo "ERRO: indexação falhou (área_copilot acessível? pip install -e area-copilot?)"
  exit 1
}

{
  echo "# Resumo financeiro — $DATE"
  echo
  echo "Pipeline: domains/finance nightly-run.sh | Playbook OK: $([ -x "$PLAYBOOK/scripts/validate-playbook.sh" ] && "$PLAYBOOK/scripts/validate-playbook.sh" >/dev/null 2>&1 && echo sim || echo NAO)"
  echo
  IFS='|' read -ra QS <<< "$QUESTIONS"
  for q in "${QS[@]}"; do
    q="$(echo "$q" | xargs)"
    echo "## $q"
    echo
    python3 -m area_harness query "$AREA_ROOT" "$q" 2>/dev/null || echo "Sem contexto para esta pergunta."
    echo
  done
  echo "_Gerado por harness — fontes citadas no corpo._"
} > "$OUT"

echo "== relatório: $OUT"

# Critério de saída do loop (Aula 09): todo número está DENTRO de um bloco FONTE.
# awk: rastreia blocos que começam em "FONTE:" e terminam em linha em branco.
SEM_FONTE=$(awk '
  /FONTE:/ { in_fonte = 1; next }
  /^$/ { in_fonte = 0 }
  /meta_vendas|veiculos_vendidos/ && !in_fonte { bad++ }
  END { print bad + 0 }
' "$OUT")
FONTES=$(grep -c "FONTE:" "$OUT" || true)
if [ "$FONTES" -eq 0 ]; then
  echo "!! CRITÉRIO FALHOU: relatório sem nenhuma FONTE citada — não publica"
  exit 1
fi
if [ "$SEM_FONTE" -gt 0 ]; then
  echo "!! CRITÉRIO FALHOU: $SEM_FONTE trecho(s) com número fora de bloco FONTE — não publica"
  exit 1
fi
echo "== publicado: OK ($FONTES fontes citadas)"