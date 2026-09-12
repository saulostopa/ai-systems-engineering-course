#!/usr/bin/env bash
# e2e-gate.sh — pre-commit gate: bloqueia arquivos de frontend staged sem
# teste E2E correspondente (Aula 10). Modelado no frontend-qa-gate.sh do factory.
# Protocolo: exit 0 = permite, exit 1 = bloqueia com mensagem.
# Fail-open: sem config .harness/config.yaml não há o que checar.
set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

CONFIG=".harness/config.yaml"
if [ ! -f "$CONFIG" ]; then
  echo "E2E-GATE: $CONFIG ausente — nada a checar (fail-open). Configure: qa.frontend_paths, qa.frontend_extensions, qa.e2e_test_path" >&2
  exit 0
fi

qa_value() {
  grep -A6 '^qa:' "$CONFIG" 2>/dev/null | grep "^[[:space:]]*$1:" | head -1 | sed -E "s/^[^:]+: *\"?([^\"]*)\"?[[:space:]]*$/\1/"
}

FRONTEND_PATHS="$(qa_value frontend_paths)"
FRONTEND_EXTS="$(qa_value frontend_extensions)"
E2E_TEST_PATH="$(qa_value e2e_test_path)"

if [ -z "$FRONTEND_PATHS" ] || [ -z "$E2E_TEST_PATH" ]; then
  echo "E2E-GATE: config incompleta em $CONFIG (frontend_paths, e2e_test_path obrigatórios)" >&2
  exit 0
fi

# 1. Arquivos de frontend staged?
STAGED=$(git diff --cached --name-only | grep -E "^($FRONTEND_PATHS)/.*\.(${FRONTEND_EXTS// /|})$" || true)
if [ -z "$STAGED" ]; then
  echo "E2E-GATE: nenhum arquivo de frontend staged — ok"
  exit 0
fi
echo "E2E-GATE: arquivos de frontend detectados:"
echo "$STAGED" | sed 's/^/  /'

# 2. Mudança correspondente na suíte E2E?
E2E_CHANGED=$(git diff --cached --name-only | grep -E "^$E2E_TEST_PATH/.*test.*\.(py|ts|js)$" || true)
if [ -z "$E2E_CHANGED" ]; then
  echo "E2E-GATE: BLOQUEADO — mudança de frontend sem teste E2E (Aula 10)." >&2
  echo "  Caminho esperado: $E2E_TEST_PATH/ (ex.: tests/e2e/)" >&2
  echo "  Use a skill qa-playwright-e2e para escrever o teste." >&2
  echo "  Bypass consciente: .harness/skip-e2e-gate (expira em 5 min)" >&2
  exit 1
fi
echo "E2E-GATE: suíte E2E alterada:"
echo "$E2E_CHANGED" | sed 's/^/  /'

# 3. (Opcional) se o pytest existir, roda a suíte tocada
if command -v pytest >/dev/null 2>&1 && [ -d "$E2E_TEST_PATH" ]; then
  echo "E2E-GATE: rodando suíte E2E..."
  if ! pytest "$E2E_TEST_PATH" -q --tb=short 2>&1 | tail -15; then
    echo "E2E-GATE: BLOQUEADO — suíte E2E falhou (use o trace viewer para triar)" >&2
    exit 1
  fi
else
  echo "E2E-GATE: pytest não disponível — só validação estrutural"
fi

echo "E2E-GATE: ok"
exit 0