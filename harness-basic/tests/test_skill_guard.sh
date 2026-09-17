#!/usr/bin/env bash
# test_skill_guard.sh — testes do gate de instalação de skills.
#
# Os testes de lógica (veredito, descoberta, nome de relatório) rodam sempre.
# Os que exercitam o scanner de verdade precisam da imagem Docker e são
# pulados com aviso quando ela não existe — mas nunca passam silenciosamente.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATE="$ROOT/scripts/gate-skill-scan.sh"
REPO="$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null || echo "$ROOT")"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0; FAIL=0; SKIP=0
_pass() { printf 'PASS %s\n' "$1"; PASS=$((PASS + 1)); }
_fail() { printf 'FAIL %s — %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }
_skip() { printf 'SKIP %s — %s\n' "$1" "$2"; SKIP=$((SKIP + 1)); }

# shellcheck source=../scripts/gate-skill-scan.sh
source "$GATE"

has_image() { docker image inspect "$IMAGE" >/dev/null 2>&1; }

# --- veredito ----------------------------------------------------------------

t_read_verdict_parseia_relatorio_valido() {
  local out
  out="$(printf '%s' '{"risk_assessment":{"score":42,"severity":"MEDIUM","recommendation":"CAUTION","max_issue_severity":"HIGH"},"issues":[1,2,3],"analysis_completeness":{"status":"partial"},"metadata":{"skillspector_version":"2.11.2"}}' | read_verdict)"
  [ "$out" = "42|MEDIUM|CAUTION|3|partial|HIGH|2.11.2" ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "veredito inesperado: $out"
}

# Um relatório truncado (timeout no meio do stream) não pode virar aprovação.
t_read_verdict_rejeita_json_truncado() {
  local out
  out="$(printf '%s' '{"risk_assessment":{"score":0,' | read_verdict)"
  case "$out" in
    ERRO*) _pass "${FUNCNAME[0]}" ;;
    *)     _fail "${FUNCNAME[0]}" "JSON truncado devia virar ERRO, veio: $out" ;;
  esac
}

t_read_verdict_sem_campos_nao_inventa_score() {
  local out
  out="$(printf '%s' '{}' | read_verdict)"
  case "$out" in
    "?|"*) _pass "${FUNCNAME[0]}" ;;
    *)     _fail "${FUNCNAME[0]}" "esperado score '?', veio: $out" ;;
  esac
}

# --- descoberta --------------------------------------------------------------

t_discover_pula_fixture_marcada() {
  local encontrados
  encontrados="$(discover_skills)"
  if printf '%s\n' "$encontrados" | grep -q 'fixture-reprovada'; then
    _fail "${FUNCNAME[0]}" "fixture marcada com .skill-guard-fixture apareceu no --all"
  else
    _pass "${FUNCNAME[0]}"
  fi
}

t_discover_acha_as_skills_do_repo() {
  local n
  n="$(discover_skills | wc -l)"
  [ "$n" -gt 10 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "esperado >10 skills descobertas, veio $n"
}

# --- nome do relatório -------------------------------------------------------

# .claude/skills/agenfk e .agents/skills/agenfk têm o mesmo basename: com
# basename, a segunda sobrescrevia o relatório da primeira.
t_slug_distingue_mesmo_basename() {
  local a b
  a="$(report_slug "$SCAN_ROOT/.claude/skills/agenfk")"
  b="$(report_slug "$SCAN_ROOT/.agents/skills/agenfk")"
  if [ "$a" = "$b" ]; then
    _fail "${FUNCNAME[0]}" "slugs colidiram: $a"
  elif [ "$a" = "agenfk" ] || [ "$b" = "agenfk" ]; then
    _fail "${FUNCNAME[0]}" "slug caiu no basename: $a / $b"
  else
    _pass "${FUNCNAME[0]}"
  fi
}

t_slug_preserva_o_caminho_da_skill() {
  local s
  s="$(report_slug "$SCAN_ROOT/skills-artifacts/feature-quiz")"
  [ "$s" = "skills-artifacts-feature-quiz" ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "esperado skills-artifacts-feature-quiz, veio: $s"
}

# As skills moram em .claude/ e .agents/: sem cortar o ponto inicial o
# relatório vira arquivo oculto e some de um `ls` no diretório.
t_slug_nao_gera_arquivo_oculto() {
  local a b
  a="$(report_slug "$SCAN_ROOT/.agents/skills/agenfk")"
  b="$(report_slug "$SCAN_ROOT/.claude/skills/agenfk")"
  case "$a$b" in
    .*) _fail "${FUNCNAME[0]}" "slug começa com ponto: $a / $b" ;;
    *)  [ "$a" != "$b" ] \
          && _pass "${FUNCNAME[0]}" \
          || _fail "${FUNCNAME[0]}" "slugs colidiram: $a" ;;
  esac
}

# --- códigos de saída --------------------------------------------------------

t_opcao_invalida_sai_2() {
  "$GATE" --nao-existe >/dev/null 2>&1
  [ "$?" -eq 2 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "esperado exit 2"
}

t_sem_alvo_sai_2() {
  "$GATE" >/dev/null 2>&1
  [ "$?" -eq 2 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "esperado exit 2"
}

# --- gate de verdade (precisa da imagem) -------------------------------------

t_gate_bloqueia_skill_ruim() {
  has_image || { _skip "${FUNCNAME[0]}" "imagem $IMAGE ausente"; return; }
  SKILL_GUARD_REPORTS="$TMP/r1" "$GATE" "$REPO/pilots/skillspector-demo/fixture-reprovada" >/dev/null 2>&1
  [ "$?" -eq 1 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "fixture ruim devia sair 1"
}

t_gate_aprova_skill_limpa() {
  has_image || { _skip "${FUNCNAME[0]}" "imagem $IMAGE ausente"; return; }
  SKILL_GUARD_REPORTS="$TMP/r2" "$GATE" "$REPO/skills-artifacts/feature-quiz" >/dev/null 2>&1
  [ "$?" -eq 0 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "skill limpa devia sair 0"
}

# O prazo existe para bloquear, não para avisar: estourar falha FECHADO.
t_timeout_falha_fechado() {
  has_image || { _skip "${FUNCNAME[0]}" "imagem $IMAGE ausente"; return; }
  SKILL_GUARD_TIMEOUT=1 SKILL_GUARD_REPORTS="$TMP/r3" \
    "$GATE" "$REPO/skills-artifacts/feature-quiz" >/dev/null 2>&1
  [ "$?" -eq 1 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "timeout devia bloquear (exit 1), não aprovar"
}

t_gate_grava_relatorio_json() {
  has_image || { _skip "${FUNCNAME[0]}" "imagem $IMAGE ausente"; return; }
  SKILL_GUARD_REPORTS="$TMP/r4" "$GATE" "$REPO/skills-artifacts/feature-quiz" >/dev/null 2>&1
  local f
  f="$(find "$TMP/r4" -name '*.json' | head -1)"
  if [ -n "$f" ] && python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>/dev/null; then
    _pass "${FUNCNAME[0]}"
  else
    _fail "${FUNCNAME[0]}" "relatório JSON não foi gravado ou é inválido"
  fi
}

# Relatório sintaticamente válido mas sem score: o gate tem que BLOQUEAR, não
# cair no ramo de aprovação por a comparação numérica ter falhado.
t_score_nao_numerico_bloqueia() {
  local fake="$TMP/fakebin" out
  mkdir -p "$fake"
  # docker falso: devolve um relatório válido em JSON, porém sem risk_assessment
  cat > "$fake/docker" <<'SH'
#!/usr/bin/env bash
case "$1" in
  image|rm) exit 0 ;;
esac
printf '%s' '{"issues":[],"analysis_completeness":{"status":"complete"},"metadata":{}}'
SH
  chmod +x "$fake/docker"
  out="$(PATH="$fake:$PATH" SKILL_GUARD_REPORTS="$TMP/r5" \
    "$GATE" "$REPO/skills-artifacts/feature-quiz" 2>&1)"
  local rc=$?
  if [ "$rc" -eq 1 ] && printf '%s' "$out" | grep -q 'sem score utilizável'; then
    _pass "${FUNCNAME[0]}"
  else
    _fail "${FUNCNAME[0]}" "esperado bloqueio por score ausente (exit 1), veio exit $rc"
  fi
}

# --- pin ---------------------------------------------------------------------

t_pin_declarado_bate_com_a_tag_remota() {
  local refs sha
  refs="$(git ls-remote "$REPO_URL" "refs/tags/${VERSION}" "refs/tags/${VERSION}^{}" 2>/dev/null)"
  [ -n "$refs" ] || { _skip "${FUNCNAME[0]}" "sem rede"; return; }
  sha="$(printf '%s\n' "$refs" | awk '/\^\{\}$/ {print $1; found=1} END {exit !found}')" \
    || sha="$(printf '%s\n' "$refs" | awk 'NR==1 {print $1}')"
  [ "$sha" = "$PINNED_SHA" ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "tag $VERSION = $sha, pin declarado = $PINNED_SHA"
}

# --- execução ----------------------------------------------------------------

for t in $(declare -F | awk '{print $3}' | grep '^t_'); do "$t"; done

printf '\n== %d/%d passaram' "$PASS" "$((PASS + FAIL))"
[ "$SKIP" -gt 0 ] && printf ' (%d pulados)' "$SKIP"
printf '\n'
exit "$FAIL"
