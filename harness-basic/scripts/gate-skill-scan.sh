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

# Baselines e allowlist de fixtures vivem FORA da árvore escaneada, na raiz do
# projeto. Dentro do diretório da skill, os dois seriam controlados pela
# entidade que o gate deveria estar medindo.
BASELINES="${SKILL_GUARD_BASELINES:-$SCAN_ROOT/.harness/baselines}"
FIXTURES_ALLOW="${SKILL_GUARD_FIXTURES:-$SCAN_ROOT/.harness/skill-guard-fixtures}"

ok()    { printf '  [ok]     %s\n' "$1"; }
warn()  { printf '  [warn]   %s\n' "$1"; }
block() { printf '  [BLOCK]  %s\n' "$1"; }
# Sourced (pelos testes), `fail` retorna em vez de encerrar: caso contrário um
# único teste que chamasse uma função falível derrubaria o runner inteiro.
fail()  {
  printf '[skill-guard] ERRO: %s\n' "$1" >&2
  [ "${BASH_SOURCE[0]}" != "${0}" ] && return 2
  exit 2
}
section() { printf '\n== %s ==\n' "$1"; }

TMPDIR_RUN="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_RUN"' EXIT

# Os limiares entram por ambiente e vão direto para `[ -gt ]`. Um valor não
# inteiro faz o teste retornar erro, os dois ramos darem falso e o alvo cair no
# else — aprovado. Validar aqui é o que impede `SKILL_GUARD_MAX_SCORE=abc` de
# desarmar o gate em silêncio.
require_int() {
  case "$2" in
    ''|*[!0-9]*) fail "$1 precisa ser um inteiro de 0 a 100 — recebido: '$2'" ;;
  esac
  [ "$2" -le 100 ] || fail "$1 precisa ser <= 100 — recebido: '$2'"
}
require_int SKILL_GUARD_MAX_SCORE  "$MAX_SCORE"
require_int SKILL_GUARD_WARN_SCORE "$WARN_SCORE"
[ "$WARN_SCORE" -le "$MAX_SCORE" ] \
  || fail "SKILL_GUARD_WARN_SCORE ($WARN_SCORE) não pode ser maior que SKILL_GUARD_MAX_SCORE ($MAX_SCORE)"
case "$TIMEOUT" in
  ''|*[!0-9]*) fail "SKILL_GUARD_TIMEOUT precisa ser um inteiro de segundos — recebido: '$TIMEOUT'" ;;
esac

# `realpath --relative-to` é do GNU coreutils. Em BSD/macOS/busybox ele não
# existe, `rel` sairia vazio e o scan viraria `scan ./` — o repositório inteiro
# no lugar da skill, diluindo justamente o alvo que se queria medir.
command -v realpath >/dev/null 2>&1 \
  || fail "realpath ausente — o gate exige GNU coreutils"
realpath --relative-to=/ / >/dev/null 2>&1 \
  || fail "realpath sem --relative-to (não-GNU) — o gate exige GNU coreutils"

# --- motor -------------------------------------------------------------------

ensure_image() {
  if docker image inspect "$IMAGE" >/dev/null 2>&1; then
    return 0
  fi
  command -v docker >/dev/null 2>&1 \
    || { fail "docker ausente — instale o docker ou rode o skillspector nativamente"; return 2; }
  printf '[skill-guard] imagem %s ausente — construindo de %s#%s (1-2 min)\n' "$IMAGE" "$REPO_URL" "$VERSION"
  docker build -q -t "$IMAGE" "${REPO_URL}#${VERSION}" >/dev/null \
    || { fail "falha ao construir a imagem do SkillSpector"; return 2; }
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
    return 2   # `fail` só encerra quando o script é executado; sourced ele
               # retorna, e sem este `return` a função seguiria e diria
               # "pin confirmado" logo depois de detectar a divergência.
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

  # O baseline é buscado em .harness/baselines/<slug>.yaml, FORA da árvore
  # escaneada, e nunca dentro do alvo. Um baseline que mora dentro da skill é
  # controlado pela própria skill: bastaria ao autor hostil iterar o scanner
  # até escrever um YAML que suprime todos os próprios achados, e o gate
  # passaria a medir o que o atacante quer. "Fica revisável em PR" não salva —
  # o mesmo PR que traz a skill traz o baseline.
  # Ficar fora também faz o baseline valer para o alvo `<skill>/SKILL.md`, e
  # não só para o alvo diretório: a chave é o slug, não a forma do caminho.
  local slug bmount=()
  slug="$(report_slug "$1")"
  # Alvo arquivo (`<skill>/SKILL.md`) herda o baseline do diretório da skill:
  # sem isso o mesmo conteúdo teria dois vereditos, um por forma de chamar.
  [ -f "$BASELINES/$slug.yaml" ] || { [ -f "$1" ] && slug="$(report_slug "$(dirname "$1")")"; }
  if [ -f "$BASELINES/$slug.yaml" ]; then
    base=(--baseline "/baselines/$slug.yaml")
    bmount=(-v "$BASELINES:/baselines:ro")
  fi

  # `-s KILL` não é exagero, é o que faz o prazo valer. O cliente docker ignora
  # SIGTERM: com o sinal padrão o `timeout` retorna 124 no prazo mas o scan
  # segue até o fim e escreve o relatório inteiro — um prazo que não limita
  # nada. Com SIGKILL o cliente morre no segundo combinado, a saída fica vazia
  # ou truncada e o chamador bloqueia o alvo.
  # `--sig-proxy=false` evita que o sinal seja repassado ao processo dentro do
  # container em vez de ao cliente; `docker rm -f` derruba o container órfão.
  # A saída vai para arquivo, não para uma substituição de comando. Com `$(...)`
  # o gate espera o stdout FECHAR: se o cliente docker morrer no prazo deixando
  # um filho órfão com o pipe aberto, o gate pendura muito além do timeout —
  # verificado com um docker falso, que o prendeu por 600s. Lendo de arquivo, o
  # prazo vale: o que estiver escrito é o que se lê, e truncado bloqueia.
  local outf="$TMPDIR_RUN/scan.$cname.json"
  if [ -e "$target" ]; then
    # Caminho local: monta a raiz do repo e referencia o alvo relativo a ela.
    rel="$(realpath --relative-to="$SCAN_ROOT" "$target")"
    timeout -s KILL "$TIMEOUT" docker run --rm --name "$cname" --sig-proxy=false \
      -v "$SCAN_ROOT:/scan:ro" ${bmount[@]+"${bmount[@]}"} "$IMAGE" \
      scan "./$rel" --no-llm --format json ${base[@]+"${base[@]}"} >"$outf" 2>/dev/null
  else
    # URL de repo git ou zip: o scanner busca sozinho, sem montar nada.
    timeout -s KILL "$TIMEOUT" docker run --rm --name "$cname" --sig-proxy=false \
      "$IMAGE" scan "$target" --no-llm --format json >"$outf" 2>/dev/null
  fi
  rc=$?
  cat "$outf" 2>/dev/null
  rm -f "$outf" 2>/dev/null

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

# Descobre as skills do repositório, pulando as fixtures deliberadamente ruins
# (existem para provar que o gate bloqueia).
#
# A allowlist fica em .harness/skill-guard-fixtures, na RAIZ — nunca um
# marcador dentro do diretório da skill. Um marcador interno é controlado pela
# própria skill: bastaria a um PR hostil trazer `SKILL.md` + o marcador para a
# skill sumir do `--all` sem ser aprovada nem bloqueada. Dizer que o marcador é
# "revisável em PR" é circular — é o mesmo PR.
#
# Formato: um caminho relativo à raiz por linha; `#` comenta.
is_fixture() {
  local rel line
  [ -f "$FIXTURES_ALLOW" ] || return 1
  rel="${1#"$SCAN_ROOT"/}"
  while IFS= read -r line; do
    line="${line%%#*}"
    line="$(printf '%s' "$line" | tr -d '[:space:]')"
    [ -n "$line" ] || continue
    [ "$line" = "$rel" ] && return 0
  done < "$FIXTURES_ALLOW"
  return 1
}

discover_skills() {
  local dir
  find "$SCAN_ROOT" -name SKILL.md \
    -not -path '*/node_modules/*' \
    -not -path '*/.git/*' \
    -print0 | xargs -0 -n1 dirname | sort -u | while IFS= read -r dir; do
      is_fixture "$dir" || printf '%s\n' "$dir"
    done
}

# --- registro do veredito -----------------------------------------------------

# Escreve o scanVerdict da skill no skills-lock.json. Sem isto a mensagem do
# validate-harness ("rode o gate e registre o veredito") apontaria para um
# fluxo que não existe, e o lock só poderia ser editado à mão.
# Só registra skills já declaradas no lock: o gate confere veredito, não decide
# o que é dependência de terceiro.
record_verdict() {
  local target="$1" json="$2" lock="$SCAN_ROOT/skills-lock.json" name
  name="$(basename "$target")"
  [ -f "$lock" ] || { warn "$name — skills-lock.json não encontrado; veredito não registrado"; return 0; }
  LOCK_PATH="$lock" SKILL_NAME="$name" SCANNER="skillspector@$VERSION" PIN="$PINNED_SHA" \
  python3 -c '
import json, os, sys, datetime
lock_path = os.environ["LOCK_PATH"]
name = os.environ["SKILL_NAME"]
rep = json.load(sys.stdin)
with open(lock_path) as fh:
    lock = json.load(fh)
entry = lock.get("skills", {}).get(name)
if entry is None:
    sys.exit(3)  # não declarada no lock — nada a registrar
r = rep.get("risk_assessment", {})
# Mescla, não substitui: o que o scanner mede é atualizado, e o que uma pessoa
# escreveu ao triar (decision, notes, rawScore, baseline...) permanece. Um
# re-scan que apagasse a triagem destruiria a única parte auditável do veredito.
verdict = dict(entry.get("scanVerdict") or {})
verdict.update({
    "scanner": os.environ["SCANNER"],
    "scannerCommit": os.environ["PIN"],
    "mode": "static",
    "scannedAt": datetime.date.today().isoformat(),
    "score": r.get("score"),
    "severity": r.get("severity"),
    "issues": len(rep.get("issues", [])),
    "suppressed": rep.get("suppressed_count", 0),
    "coverage": rep.get("analysis_completeness", {}).get("status"),
})
entry["scanVerdict"] = verdict
with open(lock_path, "w") as fh:
    json.dump(lock, fh, indent=2, ensure_ascii=False)
    fh.write("\n")
' <<< "$json"
  case "$?" in
    0) ok "$name — scanVerdict registrado em skills-lock.json" ;;
    3) : ;;  # skill não declarada no lock: silêncio, não é erro
    *) warn "$name — falha ao registrar o scanVerdict" ;;
  esac
}

# --- principal ---------------------------------------------------------------

# Só executa quando o script é chamado; sourced, expõe as funções para o teste
# (harness-basic/tests/test_skill_guard.sh) sem disparar scan nenhum.
if [ "${BASH_SOURCE[0]}" != "${0}" ]; then
  return 0
fi

TARGETS=()
RECORD=0
ONLY_TARGETS=0   # depois de `--`, tudo é alvo (permite alvo começando com `-`)
for arg in "$@"; do
  if [ "$ONLY_TARGETS" = 1 ]; then TARGETS+=("$arg"); continue; fi
  case "$arg" in
    --)       ONLY_TARGETS=1 ;;
    --all)    while IFS= read -r d; do TARGETS+=("$d"); done < <(discover_skills) ;;
    --record) RECORD=1 ;;   # grava o scanVerdict das skills escaneadas no skills-lock.json
    -*)       fail "opção desconhecida: $arg (use \`--\` antes de um alvo que comece com hífen)" ;;
    *)        TARGETS+=("$arg") ;;
  esac
done

[ "${#TARGETS[@]}" -gt 0 ] || {
  echo "Uso: gate-skill-scan.sh <alvo> [<alvo>...] | --all"
  exit 2
}

section "SkillSpector ${VERSION} — gate de instalação de skills"
verify_pin
ensure_image
mkdir -p "$REPORTS" || fail "não consegui criar o diretório de relatórios: $REPORTS"

BLOCKED=0
WARNED=0
PASSED=0

section "Scan (${#TARGETS[@]} alvo(s), estático)"
for target in "${TARGETS[@]}"; do
  name="$(basename "$target")"
  report="$REPORTS/$(report_slug "$target").json"

  # Baseline dentro do alvo é tentativa de reescrever o próprio veredito: o
  # gate não o usa (só lê de .harness/baselines/) e bloqueia o alvo, em vez de
  # ignorá-lo em silêncio — quem o colocou ali precisa saber que foi visto.
  if [ -d "$target" ] && [ -f "$target/.skillspector-baseline.yaml" ]; then
    block "$name — baseline dentro do diretório da skill ($target/.skillspector-baseline.yaml); mova para $BASELINES/$(report_slug "$target").yaml e revise"
    BLOCKED=$((BLOCKED + 1))
    continue
  fi

  # Escanear só o SKILL.md de uma skill que tem outros arquivos mede o texto e
  # ignora os scripts que vão junto — um 0/100 aí não é "limpo", é escopo
  # menor. O gate não recusa (o contrato aceita arquivo), mas diz o que ficou
  # de fora, porque o número sozinho engana.
  if [ -f "$target" ]; then
    outros="$(find "$(dirname "$target")" -type f ! -name "$(basename "$target")" 2>/dev/null | wc -l)"
    [ "$outros" -eq 0 ] || warn "$name — alvo é um arquivo; $outros outro(s) arquivo(s) no diretório NÃO entraram no scan"
  fi

  json="$(scan_target "$target")"
  if [ -z "$json" ]; then
    block "$name — sem relatório (timeout de ${TIMEOUT}s ou falha do scanner) — bloqueado por precaução"
    BLOCKED=$((BLOCKED + 1))
    continue
  fi
  printf '%s' "$json" > "$report" \
    || warn "$name — não consegui gravar o relatório em $report (veredito abaixo continua válido)"

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

  # O registro vem depois da guarda numérica e nunca para um alvo bloqueado: o
  # lock é o registro do que foi aprovado. Gravar o veredito de uma skill
  # reprovada a faria satisfazer a checagem do validate-harness — "tem
  # scanVerdict" não pode virar sinônimo de "passou".
  [ "$RECORD" = 1 ] && [ "$score" -le "$MAX_SCORE" ] && record_verdict "$target" "$json"

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
