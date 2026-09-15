#!/usr/bin/env bash
# validate-hard-harness.sh — health check do núcleo (Aula 11, aplicado ao núcleo).
# Verifica estrutura, sintaxe e roda a suíte de testes.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILURES=0

ok()   { printf '  [ok]     %s\n' "$1"; }
fail() { printf '  [FAIL]   %s\n' "$1"; FAILURES=$((FAILURES + 1)); }
section() { printf '\n== %s ==\n' "$1"; }

section "Estrutura obrigatória"
for f in hard_harness/core/schemas.py hard_harness/core/graph.py hard_harness/core/runner.py \
         hard_harness/core/gates.py hard_harness/core/events.py \
         hard_harness/stores/base.py hard_harness/stores/file_store.py hard_harness/stores/agenfk_store.py \
         hard_harness/adapters/adk2.py hard_harness/adapters/rag.py \
         hard_harness/llm/providers.py \
         hard_harness/agents/base.py \
         examples/basic_workflow/workflow.py examples/app_harness/workflow.py tests/test_hard_harness.py; do
  [ -f "$ROOT/$f" ] && ok "existe: $f" || fail "faltando: $f"
done

section "Sintaxe (compileall)"
if python3 -m py_compile "$ROOT"/hard_harness/*.py "$ROOT"/hard_harness/core/*.py \
    "$ROOT"/hard_harness/stores/*.py "$ROOT"/hard_harness/adapters/*.py \
    "$ROOT"/hard_harness/agents/*.py "$ROOT"/examples/basic_workflow/*.py \
    "$ROOT"/examples/app_harness/*.py "$ROOT"/tests/*.py 2>/dev/null; then
  ok "py_compile OK"
else
  fail "erro de sintaxe"
fi

section "Suíte de testes"
if (cd "$ROOT" && PYTHONPATH=. python3 tests/test_hard_harness.py >/dev/null 2>&1     && PYTHONPATH=. OPENROUTER_API_KEY= python3 tests/test_llm_providers.py >/dev/null 2>&1); then
  ok "30 testes PASS (19 núcleo + 11 providers)"
else
  fail "testes falharam (rode os dois suites em tests/)"
fi

section "Exemplo básico (grafo completo)"
if (cd "$ROOT" && PYTHONPATH=. python3 examples/basic_workflow/workflow.py >/dev/null 2>&1); then
  ok "basic_workflow fecha com status closed"
else
  fail "basic_workflow não fechou"
fi

printf '\n%s — %d falha(s)\n' "$([ "$FAILURES" -eq 0 ] && echo "HARD HARNESS OK" || echo "HARD HARNESS QUEBRADO")" "$FAILURES"
exit "$FAILURES"