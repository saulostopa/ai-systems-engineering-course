#!/usr/bin/env bash
# install.sh — instala o harness básico num projeto alvo.
# Uso: install.sh <repo-alvo> [--force]
# Modelado em webmotors-harness-factory/scripts/bootstrap-project.sh
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET=""
FORCE=0

for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    -*) printf 'Unknown option: %s\n' "$arg" >&2; exit 2 ;;
    *) TARGET="$arg" ;;
  esac
done

[ -n "$TARGET" ] || { echo "Uso: install.sh <repo-alvo> [--force]"; exit 1; }
[ -d "$TARGET" ] || { echo "ERRO: diretório não existe: $TARGET"; exit 1; }

log() { printf '[harness-basic] %s\n' "$1"; }
fail() { printf '[harness-basic] ERROR: %s\n' "$1" >&2; exit 1; }

copy() {
  local src="$1" dst="$2"
  if [ -e "$dst" ] && [ "$FORCE" != "1" ]; then
    fail "recusando sobrescrever: $dst (use --force)"
  fi
  mkdir -p "$(dirname "$dst")"
  cp -r "$src" "$dst"
  log "instalado: $dst"
}

log "Instalando harness básico em: $TARGET"

# 1. Templates
for f in AGENTS.md feature_list.json claude-progress.md session-handoff.md; do
  copy "$ROOT/templates/$f" "$TARGET/$f"
done
copy "$ROOT/templates/policies" "$TARGET/policies"
copy "$ROOT/templates/init.sh" "$TARGET/init.sh"

# 2. Scripts de validação
copy "$ROOT/scripts" "$TARGET/scripts"

# 3. Hooks mecânicos
if git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1; then
  copy "$ROOT/.githooks" "$TARGET/.githooks"
  git -C "$TARGET" config core.hooksPath .githooks
  log "hooks ativados (core.hooksPath = .githooks)"
else
  warn() { printf '[harness-basic] aviso: %s\n' "$1"; }
  warn "não é um repo git — hooks não instalados (rode git init e re-execute)"
fi

chmod +x "$TARGET/init.sh" "$TARGET/scripts/"*.sh 2>/dev/null

log "Instalação completa. Próximos passos:"
log "  1. edite AGENTS.md (seção 1 e 7) e feature_list.json"
log "  2. rode ./init.sh"
log "  3. commit inicial (o pre-commit vai validar o harness)"