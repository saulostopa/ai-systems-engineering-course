# Revisão adversarial independente — gate de instalação de skills (SkillSpector)

> Resposta ao `PROMPT-REVISAO-EXTERNA.md`. Revisor: agente independente.
> Método: análise do código + verificação empírica (docker falso em `/tmp`, suíte real com a imagem docker presente, 16/16 testes).
> Data: 2026-09-17.

## Resumo executivo

O gate está **estruturalmente correto nos caminhos de falha convencionais** (JSON vazio/ilegível/sem score bloqueiam; timeout bloqueia; códigos de saída 0/1/2 conforme contrato). Porém há **duas brechas de bypass reais** — o baseline e o marcador de fixture são lidos de dentro do próprio alvo não confiável — e **um fail-open demonstrado** por variável de ambiente malformada. Nada disso exige explorar o scanner: é a configuração do gate que entrega o veredito ao atacante.

---

## Achados (do mais grave para o menos grave)

### 1. CRÍTICO — Baseline lido de dentro do próprio alvo = reescrita do veredito pelo atacante

`harness-basic/scripts/gate-skill-scan.sh:95-97`

O `--baseline` aponta para `.skillspector-baseline.yaml` **dentro do diretório da skill** — exatamente a entidade não confiável que o gate deveria medir. Como o scanner exclui o baseline da análise, uma skill hostil traz um baseline que suprime todos os próprios achados (o autor itera o scanner localmente até o scan sair limpo).

**Cenário de falha demonstrado** (docker falso retornando score 100 CRITICAL sem `--baseline` e score 5 com):

```
$ gate-skill-scan.sh .agents/skills/archify      # diretório COM baseline
  [ok]     archify — score 5/100 (LOW) ... 
SKILL GUARD OK — 1 aprovada(s) ...               # exit 0

$ gate-skill-scan.sh skills-artifacts/feature-quiz  # SEM baseline
  [BLOCK]  feature-quiz — score 100/100 (CRITICAL) ...
SKILL GUARD BLOQUEOU — ...                       # exit 1
```

Um único arquivo controlado pelo alvo inverte o veredito da mesma skill.

**Evidência real no repo**: `skills-lock.json` registra archify com `rawScore: 100/100 CRITICAL, 59 achados` → baseline suprime 57 → score final 22 → ACEITO. O mecanismo permite que os 59 sejam suprimidos, não só 57. A triagem honesta de hoje é cortesia do revisor, não propriedade do gate.

**Grau de gravidade**: é a falha mais grave — o gate passa a medir o que o atacante quer; "nenhuma skill entra sem passar pelo scanner" vira "entra qualquer skill que saiba escrever um YAML".

**O que resolveria**: baselines fora da árvore escaneada (ex.: `$SCAN_ROOT/.harness/baselines/<slug>.yaml`, revisáveis em PR ao lado do gate, nunca dentro do alvo) e rejeitar (ou exigir registro prévio) qualquer baseline encontrado dentro do diretório da skill.

### 2. ALTO — Marcador `.skill-guard-fixture` dentro da skill = bypass do `--all`

`harness-basic/scripts/gate-skill-scan.sh:161-174`

`discover_skills` pula qualquer diretório que contenha o arquivo — e esse arquivo mora **dentro** do diretório que deveria ser escaneado. Uma skill de terceiros (ou uma skill corrompida no supply chain) chega com `SKILL.md` + `.skill-guard-fixture` → invisível ao `--all`, contada nem como aprovada nem como bloqueada, `exit 0`.

**Cenário de falha**: PR que adiciona `skills/evil/SKILL.md` + `skills/evil/.skill-guard-fixture` → `discover_skills` não lista `skills/evil` (confirmado: `fixture-reprovada` é excluída exatamente assim) → `--all` reporta 0 bloqueadas e sai 0.

O argumento "arquivo versionado e revisável em PR" é circular: o mesmo PR que introduz a skill introduz o marcador.

**O que resolveria**: allowlist fora da árvore (ex.: `.harness/skill-guard-fixtures` na raiz, listando caminhos relativos), ou fixtures confinadas a um diretório dedicado excluído por caminho.

### 3. ALTO — `SKILL_GUARD_MAX_SCORE` não-numérico desarma o gate silenciosamente

`harness-basic/scripts/gate-skill-scan.sh:34-35, 241-252`

`[ "$score" -gt "$MAX_SCORE" ]` com `MAX_SCORE="abc"` retorna 2 (erro) → if e elif falsos → cai no `else` → `ok`, `exit 0`.

**Cenário de falha demonstrado**:

```
$ SKILL_GUARD_MAX_SCORE=abc SKILL_GUARD_WARN_SCORE=abc gate-skill-scan.sh <skill-com-score-70>
  [ok]     feature-quiz — score 70/100 (HIGH) ...
SKILL GUARD OK — 1 aprovada(s) ...               # exit 0  ← deveria BLOQUEAR
```

Sem a variável (default 50): o mesmo alvo → `[BLOCK]`, `exit 1`. O próprio comentário das linhas 229-231 descreve esse fall-through para o campo `score` e o corrige — mas a mesma guarda não existe para `MAX_SCORE`/`WARN_SCORE`. (`MAX_SCORE=""` é seguro por causa do `:-`; valores como `"50.0"` também falham aberto — bash só tolera espaços e zeros à esquerda em `[ ] -gt`.)

**O que resolveria**: validar `MAX_SCORE` e `WARN_SCORE` como inteiros antes do loop e `fail` se não forem.

### 4. MÉDIO — O pin não cobre a imagem local; tag certa com conteúdo errado passa

`harness-basic/scripts/gate-skill-scan.sh:51-60, 64-80`

`verify_pin` confere apenas a tag **remota**. Se existir localmente uma imagem `skillspector:v2.11.2` com conteúdo divergente (cache de CI envenenado, imagem antiga construída de tag reescrita), `ensure_image` a usa sem nenhuma verificação e o pin imprime "pin confirmado" — o scanner que roda pode ser qualquer coisa. Offline com imagem local → aviso e segue (linhas 71-74), zero verificação.

**Cenário de falha**: CI com cache docker populado por um build de `skillspector:v2.11.2` modificado (scanner que reporta score 0 para tudo) → `docker image inspect` passa → `verify_pin` confirma a tag remota (que realmente aponta para o SHA fixado) → gate aprova tudo com "pin confirmado". O pin protege contra reescrita da tag, não contra o conteúdo local.

**O que resolveria**: fixar o digest esperado da imagem (ao lado do SHA) e conferir via `docker image inspect --format '{{.Id}}'`; divergiu → rebuild ou `fail`.

### 5. MÉDIO — `validate-harness.sh`: lock dependente de CWD + fluxo de "registrar veredito" inexistente

`harness-basic/scripts/validate-harness.sh:56-60, 77`

- (a) A mensagem de erro manda "rode scripts/gate-skill-scan.sh e registre o veredito" — mas **nenhum script do repo escreve `scanVerdict` no `skills-lock.json`** (o gate não tem uma única referência ao lock; o lock atual foi editado à mão). O fluxo documentado não existe.
- (b) `LOCK="skills-lock.json"` é relativo ao **CWD** do invocador, e o fallback usa `git rev-parse --show-toplevel` sem `-C "$ROOT"` (diferente do gate, linha 40).

**Cenário de falha**: `bash /caminho/harness-basic/scripts/validate-harness.sh` rodado de fora do repo (CI de outro projeto) → `rev-parse` falha → `LOCK="/skills-lock.json"` → não existe → `ok "sem skills-lock.json (nenhuma skill de terceiro instalada)"` → `exit 0` — a checagem fica inerte justamente quando o pre-push deveria falhar. O comentário da linha 56 ("ao lado deste diretório") não descreve o que o código faz.

**O que resolveria**: `LOCK="$ROOT/skills-lock.json"` com fallback `git -C "$ROOT"`; e implementar o registro do veredito (ou corrigir a mensagem).

### 6. MÉDIO-BAIXO — Alvo `SKILL.md` (arquivo) ignora o baseline

`harness-basic/scripts/gate-skill-scan.sh:95`

`[ -f "$target/.skillspector-baseline.yaml" ]` só casa alvo-diretorio.

**Cenário de falha demonstrado**: `gate .agents/skills/archify` → aprovado; `gate .agents/skills/archify/SKILL.md` → bloqueado, mesma skill, mesmo scanner. O contrato lista `SKILL.md` como alvo válido; o veredito passa a depender da forma como o alvo é passado.

### 7. MÉDIO-BAIXO — `realpath --relative-to` é GNU-only; falha → varre `./` (o repo inteiro)

`harness-basic/scripts/gate-skill-scan.sh:108-110`

Em macOS/BSD e busybox, `realpath --relative-to` não existe → `rel=""` → `scan "./"` → o alvo específico não é escaneado isoladamente; o veredito é o do repo inteiro, que pode diluir a skill hostil. Funciona na máquina atual (uutils coreutils 0.8.0). **O que resolveria**: exigir GNU coreutils e `fail` se a flag não for suportada (ou reimplementar o relativo em shell puro).

### 8. BAIXO — `t_timeout_falha_fechado` é corrida e não prova a semântica do timeout

`harness-basic/tests/test_skill_guard.sh:148-155`

`TIMEOUT=1` contra scan real: em máquina rápida/daemon quente o scan pode terminar em <1s → `exit 0` → teste falha espúrio (hoje passou, mas por margem de segundos). E o teste só verifica `exit 1` — um gate que bloqueia por **qualquer** falha do docker passa sem nunca exercitar o prazo. Um docker falso que dorme para sempre + assert da mensagem "sem relatório (timeout" testaria o comportamento de verdade.

### 9. BAIXO — Testes que passariam contra implementação quebrada

`harness-basic/tests/test_skill_guard.sh:195-204` e `157-167`

- `t_pin_declarado_bate_com_a_tag_remota` **reimplementa** o `ls-remote`+`awk` do gate e nunca chama `verify_pin` — um gate sem verificação de pin passa no teste. O teste valida o pin do repo, não o gate.
- `t_gate_grava_relatorio_json` não confere o exit do gate — um gate que grava `{}` (JSON válido) sempre, sem escanear nada, passa.

### 10. BAIXO — `fail()` do gate é sourced no runner de testes

`harness-basic/tests/test_skill_guard.sh:21` + `harness-basic/scripts/gate-skill-scan.sh:46`

Qualquer teste futuro que dispare `fail()` (ex.: chamar `ensure_image`) mata o runner inteiro com `exit 2` em vez de falhar um único teste. Latente hoje (nenhum teste chama função que pode falhar), frágil para evolução.

### 11. BAIXO — Menores

- `gate-skill-scan.sh:185-191`: alvos iniciados em `-` são rejeitados e não há separador `--`.
- `gate-skill-scan.sh:201, 218`: `mkdir -p "$REPORTS"` e a gravação do relatório não são checados — se falharem, o gate segue e pode aprovar sem gravar o artefato de auditoria (o veredito continua correto; é perda de evidência, não fail-open).
- `read_verdict` (`gate-skill-scan.sh:128-146`): um score float (`"12.5"`) seria bloqueado como ilegível — fail-closed, mas quebraria o gate se o scanner um dia emitir float (contrato atual diz 0-100 inteiro).

---

## O que verifiquei e considerei correto (cobertura da revisão)

- **Códigos de saída 0/1/2** conforme contrato, validados empiricamente (docker real: fixture ruim → 1, skill limpa → 0; docker falso em todos os ramos).
- **Guarda do score não-numérico** (linhas 232-239) funciona e protege o fall-through que ela mesma descreve — o teste `t_score_nao_numerico_bloqueia` é sólido (usa docker falso, roda sem imagem).
- **Fail-closed nos caminhos de falha**: JSON vazio → bloqueio; JSON ilegível (`ERRO*`) → bloqueio; `python3` ausente → veredito vazio → score `""` → guarda bloqueia; timeout estourado → saída vazia/truncada → bloqueio; `MAX_SCORE=""` é seguro (o `:-` aplica o default — confirmado por experimento).
- **Timeout**: `-s KILL` + `rc ≥ 124` → `docker rm -f` do container órfão; `--sig-proxy=false`; o `rc=$?` é capturado antes de qualquer comando posterior — coerente.
- **`${base[@]+"${base[@]}"}`** — idiomática correta para array vazio.
- **`report_slug`** (linhas 155-157): sem path traversal — `tr` elimina separadores, `sed` corta pontos/dashes nas bordas; slug vazio cai em `.json` inócuo; alvos absolutos fora de `SCAN_ROOT` e URLs produzem slugs inertes.
- **`discover_skills`**: o subshell do `while read` só imprime (não acumula estado) — sem risco de perda de estado; espaços em nomes sobrevivem (leitura `read -r` + citação em `TARGETS`); fixture excluída (confirmado por execução); `node_modules`/`.git` excluídos.
- **Suíte de testes**: 16/16 passando na máquina atual com a imagem docker real.
- **Sourcing para testes**: a guarda `${BASH_SOURCE[0]} != ${0}` (linhas 180-182) funciona; o source não dispara scan nem efeito colateral; nenhum helper colide destrutivamente com `fail()` hoje.
- **`set -uo pipefail` sem `set -e`** é intencional e consistente: todos os retornos de `scan_target` e todos os pontos de cálculo do veredito foram mapeados; os que poderiam aprovar indevidamente bloqueiam.
- **Pin remoto** bate com o commit declarado (`t_pin_declarado_bate_com_a_tag_remota` passou com rede OK).
- **Divergência documentação × código** verificada: limiares (50/20), códigos de saída, flags e `SKILL_GUARD_REPORTS` estão consistentes; as divergências reais estão nos itens 5, 6 e 7 acima.

**Limitação da revisão**: não testei a construção da imagem do zero (já presente localmente), nem o caminho do baseline dentro do container com o scanner real — o prompt marca esse comportamento como já verificado e foi tratado como dado.