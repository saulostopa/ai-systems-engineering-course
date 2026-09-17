#!/usr/bin/env bash
# validate-harness.sh — health check do harness instalado (Aula 11).
# Exits non-zero se o harness estiver quebrado. Modelado no factory.
set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
FAILURES=0
WARNINGS=0

ok()   { printf '  [ok]     %s\n' "$1"; }
warn() { printf '  [warn]   %s\n' "$1"; WARNINGS=$((WARNINGS + 1)); }
fail() { printf '  [FAIL]   %s\n' "$1"; FAILURES=$((FAILURES + 1)); }
section() { printf '\n== %s ==\n' "$1"; }
require_file() {
  if [ -f "$1" ]; then ok "existe: $1"; else fail "faltando: $1"; fi
}

section "Arquivos obrigatórios"
for f in AGENTS.md feature_list.json claude-progress.md session-handoff.md init.sh; do
  require_file "$f"
done
require_file "policies/definition-of-done.md"
require_file "policies/scope-control.md"
require_file "policies/evidence-required.md"

section "feature_list.json"
if [ -f "feature_list.json" ]; then
  if command -v node >/dev/null 2>&1; then
    node -e "
      const f = require('./feature_list.json');
      if (!Array.isArray(f.features)) throw new Error('sem array features');
      const states = ['not_started','in_progress','blocked','passing'];
      const bad = f.features.filter(x => !states.includes(x.status));
      if (bad.length) throw new Error('estados inválidos: ' + bad.map(b=>b.id).join(','));
      const act = f.features.filter(x => x.status==='in_progress').length;
      if (act > 1) throw new Error(act + ' features in_progress (máx. 1)');
      console.log('  [ok]     JSON válido; ' + f.features.length + ' features; ' + act + ' in_progress');
    " 2>/dev/null && : || { node -e "
      const f = require('./feature_list.json');
      const states = ['not_started','in_progress','blocked','passing'];
      const bad = f.features.filter(x => !states.includes(x.status));
      const act = f.features.filter(x => x.status==='in_progress').length;
      if (bad.length) console.error('estados inválidos: ' + bad.map(b=>b.id).join(','));
      if (act > 1) console.error(act + ' features in_progress');
      process.exit(1);
    " 2>&1 | sed 's/^/  [FAIL]   /'; FAILURES=$((FAILURES + 1)); }
  else
    warn "node ausente — validação de JSON pulada"
  fi
fi

section "Skills instaladas (skill-guard)"
# Checagem barata: toda skill declarada tem que carregar o veredito que a
# aprovou. O scan em si roda no gate-skill-scan.sh — construir a imagem do
# scanner a cada health check seria lento demais para ser usado.
# Instalado num projeto alvo, o lock fica ao lado deste diretório. Neste repo
# (harness-basic é subpasta) ele fica na raiz do git — sem esse fallback a
# checagem ficaria inerte justamente onde as skills moram.
LOCK="skills-lock.json"
[ -f "$LOCK" ] || LOCK="$(git rev-parse --show-toplevel 2>/dev/null)/skills-lock.json"

if [ -f "$LOCK" ]; then
  if command -v node >/dev/null 2>&1; then
    # O node imprime uma linha só: "OK <n>" ou "SEM <nomes>". Os nomes das
    # skills sem veredito são a única informação acionável da falha, então
    # precisam sobreviver até a mensagem — não podem ser descartados.
    LOCK_OUT="$(node -e "
      const l = require(process.argv[1]);
      const skills = Object.entries(l.skills || {});
      const sem = skills.filter(([,s]) => !s.scanVerdict).map(([n]) => n);
      if (sem.length) { console.log('SEM ' + sem.join(', ')); }
      else { console.log('OK ' + skills.length); }
    " "$LOCK" 2>/dev/null)"
    case "${LOCK_OUT:-}" in
      "OK 0")  ok "nenhuma skill de terceiro declarada" ;;
      "OK "*)  ok "${LOCK_OUT#OK } skill(s) com scanVerdict registrado" ;;
      "SEM "*) fail "sem scanVerdict no skills-lock.json: ${LOCK_OUT#SEM } — rode scripts/gate-skill-scan.sh e registre o veredito" ;;
      *)       fail "skills-lock.json ilegível ou inválido" ;;
    esac
  else
    warn "node ausente — verificação de scanVerdict pulada"
  fi
else
  ok "sem skills-lock.json (nenhuma skill de terceiro instalada)"
fi

section "Hooks"
HOOKS=$(git config core.hooksPath 2>/dev/null || echo "")
if [ "$HOOKS" = ".githooks" ]; then
  ok "core.hooksPath = .githooks"
else
  warn "core.hooksPath = ${HOOKS:-não configurado} (rode: git config core.hooksPath .githooks)"
fi

section "Resultado"
printf '\n%s — %d falha(s), %d aviso(s)\n' "$( [ "$FAILURES" -eq 0 ] && echo "HARNESS OK" || echo "HARNESS QUEBRADO" )" "$FAILURES" "$WARNINGS"
exit "$FAILURES"