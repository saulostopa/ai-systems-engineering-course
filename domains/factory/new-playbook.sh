#!/usr/bin/env bash
# new-playbook.sh — gera o esqueleto de um playbook de domínio (EPIC E).
# O esqueleto é IGUAL para todo domínio; só o conteúdo das skills muda.
# Uso: new-playbook.sh <nome-do-dominio> [--dir domains]
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
NAME=""
DIR="domains"

for arg in "$@"; do
  case "$arg" in
    --dir) DIR_NEXT=1 ;;
    -*) printf 'Unknown option: %s\n' "$arg" >&2; exit 2 ;;
    *)
      if [ "${DIR_NEXT:-0}" = "1" ]; then DIR="$arg"; DIR_NEXT=0; else NAME="$arg"; fi
      ;;
  esac
done

[ -n "$NAME" ] || { echo "Uso: new-playbook.sh <nome> [--dir <pasta>]"; exit 1; }
NAME_LC=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
TARGET="$ROOT/$DIR/$NAME_LC"
[ -d "$TARGET" ] && { echo "ERRO: playbook já existe: $TARGET"; exit 1; }

log() { printf '[new-playbook] %s\n' "$1"; }

mkdir -p "$TARGET/skills" "$TARGET/policies" "$TARGET/scripts"
log "playbook criado em $TARGET"

# Roteador do domínio
cat > "$TARGET/AGENTS.md" <<EOF
# AGENTS.md — Playbook de domínio: $NAME

> Esqueleto multi-domínio (mesmo para games, finanças, comercial...).
> Só o conteúdo das skills muda — o processo não.

## 1. O que este playbook governa
Entregas de $NAME. A feature list abaixo é a fonte de verdade do escopo.

## 2. Como trabalhar
- UMA feature \`in_progress\` por vez (regra do harness básico).
- Skills do domínio carregam SOB DEMANDA (frontmatter name+description).
- Escopo declarado em policies/scope-control.md antes de editar.

## 3. Como verificar
- policies/definition-of-done.md: o que prova "pronto" no domínio.
- policies/evidence-required.md: evidência antes de "done" (Aula 09).
- scripts/validate-playbook.sh: saúde do playbook (Aula 11).

## 4. Onde mora o conhecimento
- skills/ — pacotes de instrução do domínio (SKILL.md).
- feature_list.json — estado de cada entrega.
- relatorios/ — artefatos gerados (com fonte citada).
EOF

# Feature list vazia
cat > "$TARGET/feature_list.json" <<'EOF'
{
  "features": []
}
EOF

# Policies (referenciam o pacote do harness básico)
for p in scope-control definition-of-done evidence-required; do
  cat > "$TARGET/policies/$p.md" <<EOF
# $p — ver o template oficial em templates/policies/$p.md (Story A4)
> Regra deste domínio: o "pronto" é o que está em policies/definition-of-done.md.
EOF
done

# Validador do playbook (estrutura obrigatória)
cat > "$TARGET/scripts/validate-playbook.sh" <<'EOF'
#!/usr/bin/env bash
# validate-playbook.sh — saúde do playbook de domínio (Aula 11)
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
FAILURES=0
ok()   { printf '  [ok]     %s\n' "$1"; }
fail() { printf '  [FAIL]   %s\n' "$1"; FAILURES=$((FAILURES + 1)); }
section() { printf '\n== %s ==\n' "$1"; }

section "Estrutura obrigatória"
for f in AGENTS.md feature_list.json policies/scope-control.md policies/definition-of-done.md policies/evidence-required.md; do
  [ -f "$f" ] && ok "existe: $f" || fail "faltando: $f"
done

section "feature_list.json"
if [ -f "feature_list.json" ] && command -v node >/dev/null 2>&1; then
  node -e "const f=require('./feature_list.json'); if(!Array.isArray(f.features)) throw new Error('sem features'); const act=f.features.filter(x=>x.status==='in_progress').length; if(act>1) throw new Error(act+' in_progress'); console.log('  [ok]     JSON válido; ' + f.features.length + ' features')" 2>&1 | head -2 \
    && : || { echo "  [FAIL]   feature_list.json inválido"; FAILURES=$((FAILURES + 1)); }
fi

section "Skills"
SKILLS=$(ls skills/*/SKILL.md 2>/dev/null | wc -l)
if [ "$SKILLS" -gt 0 ]; then
  ok "$SKILLS skill(s) encontrada(s)"
else
  fail "nenhuma skill em skills/*/SKILL.md (o playbook precisa de ao menos uma)"
fi

printf '\n%s — %d falha(s)\n' "$([ "$FAILURES" -eq 0 ] && echo "PLAYBOOK OK" || echo "PLAYBOOK QUEBRADO")" "$FAILURES"
exit "$FAILURES"
EOF
chmod +x "$TARGET/scripts/validate-playbook.sh"

log "preencha skills/ e feature_list.json; valide com scripts/validate-playbook.sh"