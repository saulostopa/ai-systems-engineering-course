# Revisão adversarial independente — gate de segurança para instalação de skills

Você é um **revisor de código independente e adversarial**. Seu trabalho é
**encontrar defeitos**, não elogiar. Seja específico e cético, mas não invente
problemas: se algo está correto, diga que está correto.

## Contexto

Um repositório de engenharia de harness (curso + harnesses funcionais para a
Webmotors) acabou de ganhar um **gate de segurança para instalação de skills**.

Uma "skill" é um pacote de instrução (`SKILL.md` + scripts) que um agente de IA
(Claude Code, Cursor, Codex, OpenCode) carrega e **executa com confiança
implícita**: entra no contexto e passa a dirigir o comportamento do modelo, sem
revisão de código, sem sandbox, sem CI.

O gate roda o **NVIDIA SkillSpector** (Apache-2.0, scanner de segurança de
skills) em Docker, em modo estático, antes de qualquer skill ser instalada.

### Comportamento do scanner (já verificado — pode tomar como dado)

- `skillspector scan <alvo> --no-llm --format json` imprime um relatório JSON no stdout.
- Saída do scanner: `0` se score ≤ 50, `1` se score > 50, `2` em erro de execução. `RISK_THRESHOLD = 50`.
- O JSON tem a forma:
  `{"skill":{...}, "risk_assessment":{"score":0-100,"severity":"LOW|MEDIUM|HIGH|CRITICAL","recommendation":"...","max_issue_severity":"..."}, "issues":[...], "analysis_completeness":{"status":"complete|partial",...}, "metadata":{"skillspector_version":"..."}, "suppressed":[...], "suppressed_count":N}`
- `--baseline <arquivo.yaml>` suprime achados já triados; o scanner exclui o próprio arquivo de baseline da análise de conteúdo.
- O cliente `docker` **ignora SIGTERM** neste ambiente (por isso o `timeout -s KILL`).

### Contrato pretendido do gate

- `gate-skill-scan.sh <alvo> [<alvo>...]` — alvo é diretório, `SKILL.md`, `.zip` ou URL de repo git.
- `gate-skill-scan.sh --all` — todas as skills do repositório.
- Saída: `0` = todas aprovadas · `1` = alguma reprovada · `2` = erro de execução.
- Limiares: **bloqueia** score > 50, **avisa** score > 20, aprova o resto.
- **O gate tem que falhar FECHADO**: qualquer dúvida, erro, timeout ou relatório ilegível deve BLOQUEAR, nunca aprovar.

## O que revisar, em ordem de prioridade

**1. Caminhos de falha ABERTA.** Percorra todo retorno de `scan_target` e todo
caminho de cálculo do veredito. Existe alguma entrada ou modo de falha em que
uma skill perigosa termina contada em `PASSED`, ou o script sai `0`, em vez de
bloqueada? Considere: docker ausente ou falhando; imagem local obsoleta com a
tag certa; JSON malformado, vazio, parcial ou hostil; o scanner escrevendo
avisos no stdout; alvos com espaços, quebras de linha, globs ou hífen inicial;
symlinks; interações com `set -uo pipefail`; o subshell do `while read` em
`discover_skills` perdendo estado; `SKILL_GUARD_MAX_SCORE=""`, negativo ou
gigante.

**2. Bypass.** O marcador `.skill-guard-fixture` faz o `--all` pular um
diretório — uma skill maliciosa pode soltar esse arquivo para se esconder? E o
`.skillspector-baseline.yaml` é lido **de dentro do próprio diretório sendo
escaneado**: raciocine com cuidado sobre essa fronteira de confiança (uma skill
hostil trazendo o próprio baseline que suprime os próprios achados). Diga o
quão grave é e o que resolveria.

**3. Correção de shell.** Aspas, word splitting, `local` com substituição de
comando mascarando o exit status, o parse `IFS='|' read`,
`${target#"$SCAN_ROOT"/}` quando o alvo é absoluto fora de `SCAN_ROOT` ou
relativo, falha de `realpath`, path traversal no caminho do relatório via nome
de alvo forjado, semântica do `timeout -s KILL`, limpeza do container órfão,
falha de `mkdir`.

**4. Qualidade dos testes.** Para cada teste: ele exercita o código real do
script (e não uma reimplementação da lógica dentro do próprio teste)? Ele
**falharia** se o comportamento correspondente fosse revertido? Aponte qualquer
teste que passaria contra uma implementação quebrada. O arquivo de teste dá
`source` no gate — verifique se isso não dispara efeito colateral e se nenhum
helper colide de forma destrutiva (o gate define `fail()` que encerra o
processo).

**5. Divergência entre documentação e código.** Qualquer afirmação da
documentação que o código não cumpre (limiares, códigos de saída, flags,
caminhos, o pin, o que o baseline faz).

## Formato da resposta

Primeiro, uma **lista de achados ordenada do mais grave para o menos grave**.
Para cada um: `arquivo:linha`, o que está errado, um **cenário concreto de
falha** (entrada/estado específico → resultado errado) e a severidade.

Depois, separadamente, **o que você verificou e considerou correto**, para eu
saber a cobertura da sua revisão.

---

## Arquivo 1/3 — `harness-basic/scripts/gate-skill-scan.sh` (o gate, foco principal)

```bash
#!/usr/bin/env bash
# gate-skill-scan.sh — gate de instalação de skills (SkillSpector).
#
# Regra: nenhuma skill entra no repositório sem passar pelo scanner. Uma skill
# é código que o agente executa com confiança implícita — é a superfície de
# supply chain mais barata de atacar e a mais cara de auditar depois.
#
# Motor: NVIDIA/SkillSpector (Apache-2.0), fixado por tag e rodado em Docker
# para não depender do Python local. Só análise estática (--no-llm): o veredito
# precisa ser determinístico, reproduzível em CI e válido offline.
#
# Uso:
#   gate-skill-scan.sh <alvo> [<alvo>...]   # diretório, SKILL.md, .zip, repo git
#   gate-skill-scan.sh --all                # todas as skills do repositório
#
# Saída: 0 = todas aprovadas · 1 = alguma reprovada · 2 = erro de execução.
#
# Variáveis:
#   SKILL_GUARD_VERSION    tag do SkillSpector (default: v2.11.2)
#   SKILL_GUARD_MAX_SCORE  score máximo aceito (default: 50 — o limiar do tool)
#   SKILL_GUARD_WARN_SCORE score a partir do qual avisa (default: 20)
#   SKILL_GUARD_REPORTS    diretório dos relatórios JSON (default: .harness/skill-scans)
#   SKILL_GUARD_TIMEOUT    prazo por alvo, em segundos (default: 900). Estourar
#                          bloqueia o alvo — o gate falha fechado.
set -uo pipefail

VERSION="${SKILL_GUARD_VERSION:-v2.11.2}"
# Pin de supply chain: a tag acima deve apontar para este commit. Uma tag
# remota reescrita muda o scanner sem mudar o nome — o gate recusa se divergir.
PINNED_SHA="69dcdfb74487d361ba4c811d088cfdea2ff3a9dc"
IMAGE="skillspector:${VERSION}"
REPO_URL="https://github.com/NVIDIA/SkillSpector.git"

MAX_SCORE="${SKILL_GUARD_MAX_SCORE:-50}"
WARN_SCORE="${SKILL_GUARD_WARN_SCORE:-20}"
TIMEOUT="${SKILL_GUARD_TIMEOUT:-900}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Quando instalado num projeto alvo, a raiz do scan é a raiz do projeto.
SCAN_ROOT="$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null || echo "$ROOT")"
REPORTS="${SKILL_GUARD_REPORTS:-$SCAN_ROOT/.harness/skill-scans}"

ok()    { printf '  [ok]     %s\n' "$1"; }
warn()  { printf '  [warn]   %s\n' "$1"; }
block() { printf '  [BLOCK]  %s\n' "$1"; }
fail()  { printf '[skill-guard] ERRO: %s\n' "$1" >&2; exit 2; }
section() { printf '\n== %s ==\n' "$1"; }

# --- motor -------------------------------------------------------------------

ensure_image() {
  if docker image inspect "$IMAGE" >/dev/null 2>&1; then
    return 0
  fi
  command -v docker >/dev/null 2>&1 || fail "docker ausente — instale o docker ou rode o skillspector nativamente"
  printf '[skill-guard] imagem %s ausente — construindo de %s#%s (1-2 min)\n' "$IMAGE" "$REPO_URL" "$VERSION"
  docker build -q -t "$IMAGE" "${REPO_URL}#${VERSION}" >/dev/null \
    || fail "falha ao construir a imagem do SkillSpector"
  ok "imagem construída: $IMAGE"
}

# Confirma que a tag ainda aponta para o commit fixado. Sem rede, avisa e segue
# — a imagem local já foi construída de um pin verificado anteriormente.
verify_pin() {
  local refs sha
  # Tag anotada resolve em refs/tags/X^{} (o commit); tag lightweight só tem
  # refs/tags/X. Pedimos as duas e ficamos com a forma peeled quando existir.
  refs="$(git ls-remote "$REPO_URL" "refs/tags/${VERSION}" "refs/tags/${VERSION}^{}" 2>/dev/null)"
  sha="$(printf '%s\n' "$refs" | awk '/\^\{\}$/ {print $1; found=1} END {exit !found}')" \
    || sha="$(printf '%s\n' "$refs" | awk 'NR==1 {print $1}')"
  if [ -z "$sha" ]; then
    warn "não foi possível verificar o pin (sem rede?) — usando a imagem local $IMAGE"
    return 0
  fi
  if [ "$sha" != "$PINNED_SHA" ]; then
    block "pin divergente: ${VERSION} aponta para ${sha}, esperado ${PINNED_SHA}"
    fail "a tag do SkillSpector foi reescrita — revise antes de confiar no scanner"
  fi
  ok "pin confirmado: ${VERSION} = ${PINNED_SHA:0:12}"
}

# Roda o scanner num alvo e devolve o JSON no stdout.
# O timeout é parte do gate, não uma conveniência: um pacote grande (muitos
# arquivos, exemplos de milhares de linhas) leva minutos, e um scan que nunca
# retorna seria um gate que nunca bloqueia. Estourar o prazo falha FECHADO —
# quem trata a saída vazia bloqueia o alvo.
scan_target() {
  local target="$1" rel cname rc base=()
  cname="skillguard-$$-${RANDOM}"

  # Baseline por skill, não global: um .skillspector-baseline.yaml dentro do
  # diretório da skill suprime só os falsos positivos daquela skill, e fica
  # revisável em PR ao lado do código que ele perdoa. Um baseline global
  # desarmaria a regra para todas as outras — que é como um gate morre.
  if [ -e "$target" ] && [ -f "$target/.skillspector-baseline.yaml" ]; then
    base=(--baseline "./${target#"$SCAN_ROOT"/}/.skillspector-baseline.yaml")
  fi

  # `-s KILL` não é exagero, é o que faz o prazo valer. O cliente docker ignora
  # SIGTERM: com o sinal padrão o `timeout` retorna 124 no prazo mas o scan
  # segue até o fim e escreve o relatório inteiro — um prazo que não limita
  # nada. Com SIGKILL o cliente morre no segundo combinado, a saída fica vazia
  # ou truncada e o chamador bloqueia o alvo.
  # `--sig-proxy=false` evita que o sinal seja repassado ao processo dentro do
  # container em vez de ao cliente; `docker rm -f` derruba o container órfão.
  if [ -e "$target" ]; then
    # Caminho local: monta a raiz do repo e referencia o alvo relativo a ela.
    rel="$(realpath --relative-to="$SCAN_ROOT" "$target")"
    timeout -s KILL "$TIMEOUT" docker run --rm --name "$cname" --sig-proxy=false \
      -v "$SCAN_ROOT:/scan" "$IMAGE" scan "./$rel" --no-llm --format json ${base[@]+"${base[@]}"} 2>/dev/null
  else
    # URL de repo git ou zip: o scanner busca sozinho, sem montar nada.
    timeout -s KILL "$TIMEOUT" docker run --rm --name "$cname" --sig-proxy=false \
      "$IMAGE" scan "$target" --no-llm --format json 2>/dev/null
  fi
  rc=$?

  # 124 = prazo estourado. O container sobrevive ao cliente morto: derrube-o.
  if [ "$rc" -ge 124 ]; then
    docker rm -f "$cname" >/dev/null 2>&1
  fi
}

# --- veredito ----------------------------------------------------------------

# Lê o JSON do scanner e imprime: score|severity|recommendation|n_issues|complete|worst
read_verdict() {
  python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print("ERRO|%s" % e)
    sys.exit(3)
r = d.get("risk_assessment", {})
c = d.get("analysis_completeness", {})
print("|".join([
    str(r.get("score", "?")),
    str(r.get("severity", "?")),
    str(r.get("recommendation", "?")),
    str(len(d.get("issues", []))),
    str(c.get("status", "?")),
    str(r.get("max_issue_severity", "NONE")),
    str(d.get("metadata", {}).get("skillspector_version", "?")),
]))
'
}

# Nome do relatório: derivado do CAMINHO, não do basename. .claude/skills/agenfk
# e .agents/skills/agenfk são duas cópias distintas da mesma skill e cada uma
# precisa do seu relatório — com basename, a segunda sobrescrevia a primeira.
# Os pontos iniciais caem junto: as skills moram em .claude/ e .agents/, e sem
# isso o relatório vira arquivo oculto — um `ls` no diretório de relatórios não
# mostraria nada, que é o mesmo que não ter relatório.
report_slug() {
  printf '%s' "${1#"$SCAN_ROOT"/}" | tr -c 'A-Za-z0-9._-' '-' | sed 's/^[.-]*//;s/[.-]*$//'
}

# --- descoberta --------------------------------------------------------------

# Descobre as skills do repositório. Um diretório com o marcador
# .skill-guard-fixture é pulado: são fixtures deliberadamente ruins, usadas
# para provar que o gate bloqueia. Sem essa saída explícita, o gate do próprio
# repositório reprovaria para sempre — e a saída é um arquivo versionado e
# revisável em PR, não um caminho escondido no script.
discover_skills() {
  local dir
  find "$SCAN_ROOT" -name SKILL.md \
    -not -path '*/node_modules/*' \
    -not -path '*/.git/*' \
    -print0 | xargs -0 -n1 dirname | sort -u | while IFS= read -r dir; do
      [ -f "$dir/.skill-guard-fixture" ] || printf '%s\n' "$dir"
    done
}

# --- principal ---------------------------------------------------------------

# Só executa quando o script é chamado; sourced, expõe as funções para o teste
# (harness-basic/tests/test_skill_guard.sh) sem disparar scan nenhum.
if [ "${BASH_SOURCE[0]}" != "${0}" ]; then
  return 0
fi

TARGETS=()
for arg in "$@"; do
  case "$arg" in
    --all) while IFS= read -r d; do TARGETS+=("$d"); done < <(discover_skills) ;;
    -*)    fail "opção desconhecida: $arg" ;;
    *)     TARGETS+=("$arg") ;;
  esac
done

[ "${#TARGETS[@]}" -gt 0 ] || {
  echo "Uso: gate-skill-scan.sh <alvo> [<alvo>...] | --all"
  exit 2
}

section "SkillSpector ${VERSION} — gate de instalação de skills"
verify_pin
ensure_image
mkdir -p "$REPORTS"

BLOCKED=0
WARNED=0
PASSED=0

section "Scan (${#TARGETS[@]} alvo(s), estático)"
for target in "${TARGETS[@]}"; do
  name="$(basename "$target")"
  report="$REPORTS/$(report_slug "$target").json"

  json="$(scan_target "$target")"
  if [ -z "$json" ]; then
    block "$name — sem relatório (timeout de ${TIMEOUT}s ou falha do scanner) — bloqueado por precaução"
    BLOCKED=$((BLOCKED + 1))
    continue
  fi
  printf '%s' "$json" > "$report"

  verdict="$(printf '%s' "$json" | read_verdict)"
  case "$verdict" in
    ERRO*) block "$name — relatório ilegível: ${verdict#ERRO|}"; BLOCKED=$((BLOCKED + 1)); continue ;;
  esac

  IFS='|' read -r score severity recommendation issues complete worst _ver <<< "$verdict"

  label="$name — score ${score}/100 (${severity}), ${issues} achado(s), cobertura ${complete}"

  # Score não-numérico bloqueia. Sem esta guarda o `-gt` abaixo erra ("integer
  # expression expected"), os dois ramos retornam falso e o alvo cai no else —
  # ou seja, um relatório sem score seria APROVADO. Gate tem que falhar fechado.
  case "$score" in
    ''|*[!0-9]*)
      block "$name — relatório sem score utilizável ('${score}') — bloqueado por precaução"
      printf '           relatório: %s\n' "$report"
      BLOCKED=$((BLOCKED + 1))
      continue
      ;;
  esac

  if [ "$score" -gt "$MAX_SCORE" ]; then
    block "$label — pior achado: ${worst}"
    printf '           relatório: %s\n' "$report"
    BLOCKED=$((BLOCKED + 1))
  elif [ "$score" -gt "$WARN_SCORE" ]; then
    warn "$label — revise antes de instalar"
    printf '           relatório: %s\n' "$report"
    WARNED=$((WARNED + 1))
  else
    ok "$label"
    PASSED=$((PASSED + 1))
  fi
done

section "Resultado"
printf 'limiar: bloqueia score > %s · avisa score > %s · modo: estático (--no-llm)\n' "$MAX_SCORE" "$WARN_SCORE"
printf 'relatórios: %s\n' "$REPORTS"
printf '\n%s — %d aprovada(s), %d com aviso, %d bloqueada(s)\n' \
  "$( [ "$BLOCKED" -eq 0 ] && echo "SKILL GUARD OK" || echo "SKILL GUARD BLOQUEOU" )" \
  "$PASSED" "$WARNED" "$BLOCKED"

# Um scan estático limpo não é o mesmo que uma skill auditada: o modo estático
# não julga intenção. O veredito abaixo cobre padrão conhecido, não semântica.
[ "$BLOCKED" -eq 0 ] || exit 1
exit 0
```

## Arquivo 2/3 — `harness-basic/tests/test_skill_guard.sh` (os testes)

```bash
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
```

## Arquivo 3/3 — trecho novo de `harness-basic/scripts/validate-harness.sh`

Este trecho foi acrescentado a um health check já existente. Ele NÃO roda o
scanner (seria lento demais): só confere que toda skill declarada no
`skills-lock.json` carrega o veredito que a aprovou.

```bash
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
```
