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
# Usa um docker falso que trava para sempre — com o scanner real o teste seria
# uma corrida (um scan rápido terminaria antes do prazo) e não provaria nada.
# Também confere a MENSAGEM: um gate que bloqueia por qualquer falha do docker
# passaria sem nunca exercitar o timeout.
t_timeout_falha_fechado() {
  local fake="$TMP/binto" out rc
  mkdir -p "$fake"
  cat > "$fake/docker" <<'SH'
#!/usr/bin/env bash
case "$1" in
  image|rm) exit 0 ;;
esac
sleep 600
SH
  chmod +x "$fake/docker"
  out="$(PATH="$fake:$PATH" SKILL_GUARD_TIMEOUT=2 SKILL_GUARD_REPORTS="$TMP/r3" \
    "$GATE" "$REPO/skills-artifacts/feature-quiz" 2>&1)"
  rc=$?
  if [ "$rc" -eq 1 ] && printf '%s' "$out" | grep -q 'sem relatório (timeout'; then
    _pass "${FUNCNAME[0]}"
  else
    _fail "${FUNCNAME[0]}" "esperado bloqueio por timeout (exit 1 + mensagem), veio exit $rc"
  fi
}

t_gate_grava_relatorio_json() {
  has_image || { _skip "${FUNCNAME[0]}" "imagem $IMAGE ausente"; return; }
  SKILL_GUARD_REPORTS="$TMP/r4" "$GATE" "$REPO/skills-artifacts/feature-quiz" >/dev/null 2>&1
  local rc=$? f
  f="$(find "$TMP/r4" -name '*.json' | head -1)"
  if [ "$rc" -eq 0 ] && [ -n "$f" ] \
     && python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if 'risk_assessment' in d else 1)" "$f" 2>/dev/null; then
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

# Chama a verify_pin DO GATE, não uma reimplementação: um gate que perdesse a
# verificação de pin precisa reprovar aqui.
t_verify_pin_confirma_o_commit_fixado() {
  local out
  git ls-remote "$REPO_URL" "refs/tags/${VERSION}" >/dev/null 2>&1 \
    || { _skip "${FUNCNAME[0]}" "sem rede"; return; }
  out="$(verify_pin 2>&1)"
  printf '%s' "$out" | grep -q "pin confirmado: ${VERSION} = ${PINNED_SHA:0:12}" \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "verify_pin não confirmou o pin: $out"
}

# Pin divergente tem que abortar o gate (exit 2), não seguir com um scanner
# cuja procedência não confere.
t_verify_pin_rejeita_sha_divergente() {
  local out rc
  git ls-remote "$REPO_URL" "refs/tags/${VERSION}" >/dev/null 2>&1 \
    || { _skip "${FUNCNAME[0]}" "sem rede"; return; }
  out="$(PINNED_SHA=0000000000000000000000000000000000000000 verify_pin 2>&1)"; rc=$?
  if [ "$rc" -ne 0 ] && printf '%s' "$out" | grep -q 'pin divergente'; then
    _pass "${FUNCNAME[0]}"
  else
    _fail "${FUNCNAME[0]}" "pin divergente devia abortar, veio rc=$rc: $out"
  fi
}

# --- bypass (achados da revisão externa) --------------------------------------

# CRÍTICO: um baseline dentro do diretório da skill é controlado pela própria
# skill. O gate não pode usá-lo — e não pode ignorá-lo em silêncio.
t_baseline_dentro_do_alvo_bloqueia() {
  local dir="$TMP/skillmal" out rc
  mkdir -p "$dir"
  printf -- '---\nname: mal\ndescription: x\n---\n' > "$dir/SKILL.md"
  printf 'version: 2\nrules:\n  - id: "SC2"\n    reason: "suprime tudo"\n' \
    > "$dir/.skillspector-baseline.yaml"
  out="$(SKILL_GUARD_REPORTS="$TMP/rb" "$GATE" "$dir" 2>&1)"; rc=$?
  if [ "$rc" -eq 1 ] && printf '%s' "$out" | grep -q 'baseline dentro do diretório'; then
    _pass "${FUNCNAME[0]}"
  else
    _fail "${FUNCNAME[0]}" "baseline interno devia bloquear (exit 1), veio exit $rc"
  fi
}

# ALTO: a allowlist de fixtures mora fora da árvore. Um arquivo largado dentro
# do diretório da skill não pode mais escondê-la do --all.
t_marcador_interno_nao_esconde_mais_a_skill() {
  local dir="$TMP/repo_fake/skills/evil"
  mkdir -p "$dir"
  printf -- '---\nname: evil\n---\n' > "$dir/SKILL.md"
  : > "$dir/.skill-guard-fixture"
  SCAN_ROOT="$TMP/repo_fake" FIXTURES_ALLOW="$TMP/repo_fake/.harness/skill-guard-fixtures" \
    bash -c 'source "'"$GATE"'"; SCAN_ROOT="'"$TMP"'/repo_fake"; FIXTURES_ALLOW="'"$TMP"'/nao-existe"; discover_skills' \
    2>/dev/null | grep -q 'skills/evil' \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "marcador interno ainda escondeu a skill do --all"
}

# A allowlist externa continua funcionando para as fixtures legítimas.
t_allowlist_externa_pula_a_fixture() {
  discover_skills | grep -q 'fixture-reprovada' \
    && _fail "${FUNCNAME[0]}" "fixture listada na allowlist apareceu no --all" \
    || _pass "${FUNCNAME[0]}"
}

# ALTO: limiar não-inteiro desarmava o gate (score 70 era aprovado).
t_limiar_nao_inteiro_aborta() {
  local rc
  SKILL_GUARD_MAX_SCORE=abc "$GATE" "$REPO/skills-artifacts/feature-quiz" >/dev/null 2>&1; rc=$?
  [ "$rc" -eq 2 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "MAX_SCORE=abc devia abortar com exit 2, veio $rc"
}

t_limiar_de_aviso_acima_do_de_bloqueio_aborta() {
  local rc
  SKILL_GUARD_WARN_SCORE=80 SKILL_GUARD_MAX_SCORE=50 \
    "$GATE" "$REPO/skills-artifacts/feature-quiz" >/dev/null 2>&1; rc=$?
  [ "$rc" -eq 2 ] \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "WARN > MAX devia abortar com exit 2, veio $rc"
}

t_separador_permite_alvo_com_hifen() {
  local out
  out="$("$GATE" -- -alvo-inexistente 2>&1)"
  printf '%s' "$out" | grep -q 'opção desconhecida' \
    && _fail "${FUNCNAME[0]}" "alvo após -- foi tratado como opção" \
    || _pass "${FUNCNAME[0]}"
}

# O registro do veredito não pode apagar a triagem escrita por uma pessoa.
t_record_preserva_campos_de_triagem() {
  local lock="$TMP/lockrepo/skills-lock.json"
  mkdir -p "$TMP/lockrepo"
  cat > "$lock" <<'JSON'
{"version":1,"skills":{"x":{"source":"a/b","scanVerdict":{"decision":"ACEITO_COM_RESSALVA","notes":"triagem manual","rawScore":100}}}}
JSON
  SCAN_ROOT="$TMP/lockrepo" record_verdict "$TMP/lockrepo/x" \
    '{"risk_assessment":{"score":7,"severity":"LOW"},"issues":[],"suppressed_count":3,"analysis_completeness":{"status":"partial"}}' \
    >/dev/null 2>&1
  python3 -c "
import json,sys
v=json.load(open('$lock'))['skills']['x']['scanVerdict']
sys.exit(0 if v.get('decision')=='ACEITO_COM_RESSALVA' and v.get('rawScore')==100 and v.get('score')==7 else 1)" \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "record_verdict apagou os campos de triagem"
}

# O lock registra o que foi APROVADO. Gravar o veredito de uma skill bloqueada
# faria "tem scanVerdict" virar sinônimo de "passou no gate".
t_record_nao_grava_skill_bloqueada() {
  local fake="$TMP/binrec" lock="$TMP/recrepo/skills-lock.json"
  mkdir -p "$fake" "$TMP/recrepo/evil"
  printf -- '---\nname: evil\n---\n' > "$TMP/recrepo/evil/SKILL.md"
  cat > "$lock" <<'JSON'
{"version":1,"skills":{"evil":{"source":"x/y"}}}
JSON
  # docker falso: sempre devolve um relatório CRITICAL acima do limiar
  cat > "$fake/docker" <<'SH'
#!/usr/bin/env bash
case "$1" in
  image|rm) exit 0 ;;
esac
printf '%s' '{"risk_assessment":{"score":91,"severity":"CRITICAL","max_issue_severity":"CRITICAL"},"issues":[1],"suppressed_count":0,"analysis_completeness":{"status":"complete"},"metadata":{}}'
SH
  chmod +x "$fake/docker"
  PATH="$fake:$PATH" SKILL_GUARD_REPORTS="$TMP/rr" \
    bash -c 'SCAN_ROOT="'"$TMP"'/recrepo" exec "'"$GATE"'" --record "'"$TMP"'/recrepo/evil"' >/dev/null 2>&1
  python3 -c "
import json,sys
v=json.load(open('$lock'))['skills']['evil'].get('scanVerdict')
sys.exit(1 if v else 0)" \
    && _pass "${FUNCNAME[0]}" \
    || _fail "${FUNCNAME[0]}" "veredito de skill bloqueada foi gravado no lock"
}

# --- execução ----------------------------------------------------------------

for t in $(declare -F | awk '{print $3}' | grep '^t_'); do "$t"; done

printf '\n== %d/%d passaram' "$PASS" "$((PASS + FAIL))"
[ "$SKIP" -gt 0 ] && printf ' (%d pulados)' "$SKIP"
printf '\n'
exit "$FAIL"
