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
