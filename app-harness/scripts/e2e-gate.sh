#!/usr/bin/env bash
# e2e-gate.sh — pre-commit gate: blocks staged frontend files without a
# corresponding E2E test (Lesson 10). Modeled on the factory frontend-qa-gate.sh.
# Protocol: exit 0 = allow, exit 1 = block with message.
# Fail-open: without a .harness/config.yaml there is nothing to check.
set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

CONFIG=".harness/config.yaml"
if [ ! -f "$CONFIG" ]; then
  echo "E2E-GATE: $CONFIG missing — nothing to check (fail-open). Configure: qa.frontend_paths, qa.frontend_extensions, qa.e2e_test_path" >&2
  exit 0
fi

qa_value() {
  grep -A6 '^qa:' "$CONFIG" 2>/dev/null | grep "^[[:space:]]*$1:" | head -1 | sed -E "s/^[^:]+: *\"?([^\"]*)\"?[[:space:]]*$/\1/"
}

FRONTEND_PATHS="$(qa_value frontend_paths)"
FRONTEND_EXTS="$(qa_value frontend_extensions)"
E2E_TEST_PATH="$(qa_value e2e_test_path)"

if [ -z "$FRONTEND_PATHS" ] || [ -z "$E2E_TEST_PATH" ]; then
  echo "E2E-GATE: incomplete config in $CONFIG (frontend_paths, e2e_test_path required)" >&2
  exit 0
fi

# 1. Staged frontend files?
STAGED=$(git diff --cached --name-only | grep -E "^($FRONTEND_PATHS)/.*\.(${FRONTEND_EXTS// /|})$" || true)
if [ -z "$STAGED" ]; then
  echo "E2E-GATE: no frontend files staged — ok"
  exit 0
fi
echo "E2E-GATE: frontend files detected:"
echo "$STAGED" | sed 's/^/  /'

# 2. Corresponding change in the E2E suite?
E2E_CHANGED=$(git diff --cached --name-only | grep -E "^$E2E_TEST_PATH/.*test.*\.(py|ts|js)$" || true)
if [ -z "$E2E_CHANGED" ]; then
  echo "E2E-GATE: BLOCKED — frontend change without an E2E test (Lesson 10)." >&2
  echo "  Expected path: $E2E_TEST_PATH/ (e.g. tests/e2e/)" >&2
  echo "  Use the qa-playwright-e2e skill to write the test." >&2
  echo "  Conscious bypass: .harness/skip-e2e-gate (expires in 5 min)" >&2
  exit 1
fi
echo "E2E-GATE: E2E suite changed:"
echo "$E2E_CHANGED" | sed 's/^/  /'

# 3. (Optional) if pytest exists, runs the touched suite
if command -v pytest >/dev/null 2>&1 && [ -d "$E2E_TEST_PATH" ]; then
  echo "E2E-GATE: running E2E suite..."
  if ! pytest "$E2E_TEST_PATH" -q --tb=short 2>&1 | tail -15; then
    echo "E2E-GATE: BLOCKED — E2E suite failed (use the trace viewer to triage)" >&2
    exit 1
  fi
else
  echo "E2E-GATE: pytest not available — structural validation only"
fi

echo "E2E-GATE: ok"
exit 0
