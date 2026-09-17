# Scan de todas as skills do repositório

`gate-skill-scan.sh --all` · SkillSpector `v2.11.2` · estático (`--no-llm`) ·
2026-09-17

**41 alvos** varridos — as skills aparecem em cópias (`.claude/skills/`,
`.agents/skills/`, `skills-artifacts/`, `app-harness/`, `area-copilot/`,
`domains/`), e cada cópia é escaneada por si, porque cópias divergem.

```
SKILL GUARD OK — 40 aprovada(s), 1 com aviso, 0 bloqueada(s)   (exit 0)
```

## Resultado

| Alvo | Score | Severidade | Achados |
|---|---|---|---|
| `.agents/skills/archify` (vendorada, com baseline) | 22/100 | MEDIUM | 2 |
| `.agents/skills/agenfk` · `.claude/skills/agenfk` | 11/100 | LOW | 2 |
| `.agents/skills/agenfk-test` · `.claude/skills/agenfk-test` | 7/100 | LOW | 1 |
| `skills-artifacts/feature-archify` | 7/100 | LOW | 1 |
| `.agents/skills/agenfk-pr` · `.claude/skills/agenfk-pr` | 6/100 | LOW | 1 |
| `.claude/skills/agenfk-flow` | 6/100 | LOW | 1 |
| outros 32 alvos | 0/100 | LOW | 0 |

Uma única acima do limiar de aviso — e é a **única de terceiro** do
repositório. Não é coincidência: as outras nasceram aqui, em PR revisado.

### De brinde: as cópias divergiram

`.claude/skills/agenfk-flow` dá 6/100 e `.agents/skills/agenfk-flow` dá 0/100.
Não é ruído do scanner — os arquivos **são diferentes**:

```
- compatibility: all            (.agents — versão CLI-only, atual)
+ compatibility: claude-code    (.claude — versão antiga, orientada a MCP)
```

A cópia antiga documenta `list_projects()` via MCP e o `curl
http://localhost:3000` que a nova proíbe — daí o achado `E1`.

Isso só apareceu porque o gate nomeia o relatório pelo **caminho**. Na primeira
versão ele usava o basename, e `.claude/skills/agenfk-flow` sobrescrevia
`.agents/skills/agenfk-flow`: metade dos resultados sumia silenciosamente e a
deriva entre as duas árvores continuaria invisível.

## Os achados LOW — todos triados

| Skill | Regra | O que casou | Veredito |
|---|---|---|---|
| `agenfk` | `EA2` Autonomous Decision Making ×2 | a expressão *"without asking"* no `SKILL.md` | Observação legítima sobre autonomia, não defeito. A skill de fato descreve quando o agente age sem perguntar. |
| `agenfk-flow` | `E1` External Transmission | `curl http://localhost:3000` | **Falso positivo com ironia**: a linha casada é a que **proíbe** essa rota de bypass. O scanner marca o exemplo dentro da proibição. |
| `agenfk-pr` | `RA2` Session Persistence | o texto da própria `description` | Falso positivo — colisão com o vocabulário da descrição. |
| `agenfk-test`, `feature-archify` | `RP1` MCP Rug Pull | — (sem trecho, confiança 0.7) | Falso positivo: nenhuma das duas declara ferramenta MCP. |

Nenhum exigiu ação. Todos abaixo do limiar de aviso (20).

## `archify` — 100/100 CRITICAL, e o que isso realmente significa

O gate reprovou uma skill **que já estava instalada neste repositório** desde o
commit `5a485aa`. Essa é a demonstração mais útil do piloto: o gate chegou
depois da skill, e encontrou o que ninguém tinha olhado.

Mas 100/100 não quer dizer "malicioso". Abrindo os 59 achados um a um:

| Regra | Qtd | O que realmente casou | Veredito |
|---|---|---|---|
| `AE1` analysis-evasion | 13 | `bin/archify.mjs` (2101 linhas), `assets/template.html` (14934 linhas) acima do limite de inspeção por arquivo | **Sinal de cobertura**, não evasão |
| `RA2` Session Persistence | 8 | o identificador JavaScript `pList` | Falso positivo |
| `PE3` Credential Access | 7 | `/etc/passwd`, `secret.txt`, `access tokens` — **dentro de `test/`** | Falso positivo (fixtures) |
| `EA3` Scope Creep | 7 | a frase **`NOT LIMITED TO`** do texto da licença SIL Open Font | Falso positivo |
| `P2` Hidden Instructions | 6 | comentários HTML/SVG (`<!-- Toolbar -->`, `<!-- Legend -->`) | Falso positivo |
| `YR4` YARA MCP tool poisoning | 6 | o base64 da fonte WOFF2 embutida (`d09GMg` = magic `wOF2`) + `description =` do CSS | Falso positivo |
| `RP1` MCP Rug Pull | 6 | arquivos de teste; archify não é servidor MCP | Falso positivo |
| `TM1`, `MP3`, `OH3`, `LP3` | 4 | `"remove"`, `"reset state"`, `"without cutting"` em testes | Falso positivo |
| `SC1` Unpinned Dependencies | 1 | `"ajv": "^8.17.1"` sem pin exato | **Verdadeiro**, menor |
| `SC4` Known Vulnerable Dependency | 1 | **`fast-uri@3.1.5`, 4 advisories** (via `ajv@8.20.0`) | **VERDADEIRO E ACIONÁVEL** |

**58 de 59 eram ruído. 1 era real.**

O achado real, verificado em `.agents/skills/archify/package-lock.json:41`:

```
node_modules/ajv           -> 8.20.0   (dependência: fast-uri ^3.0.1)
node_modules/ajv/node_modules/fast-uri -> 3.1.5
```

`fast-uri@3.1.5` carrega CVE-2026-75931 (host confusion por canonicalização
IDN pulada), CVE-2026-75975 e CVE-2026-75899 (SSRF por normalização de IPv6
malformado e por hostname com percent repetido), mais uma quarta advisory.
Chega via `ajv`, que o archify usa para validar os schemas de diagrama.

### O que foi feito com isso

`.harness/baselines/agents-skills-archify.yaml` suprime **apenas os
falsos positivos verificados**, com o motivo de cada um escrito por extenso.
`SC4` e `SC1` ficam de fora do baseline de propósito — continuam visíveis a
cada scan até serem corrigidos upstream.

Re-scan com o baseline aplicado:

```
[warn]  archify — score 22/100 (MEDIUM), 2 achado(s), cobertura partial
```

| | Sem baseline | Com baseline |
|---|---|---|
| Score | 100/100 CRITICAL | **22/100 MEDIUM** |
| Achados | 59 | **2** |
| Suprimidos | 0 | **57** |
| Gate | bloqueia (exit 1) | **avisa** (exit 0) |

Os 2 que restaram são exatamente `SC4` e `SC1` — os verdadeiros. O veredito
foi registrado em `skills-lock.json` como `ACEITO_COM_RESSALVA`, com o score
bruto (100) preservado ao lado do triado (22): quem abrir o arquivo vê as duas
coisas, não só a confortável.

O baseline fica **fora da árvore escaneada**, em `.harness/baselines/`, um por
skill. Ele já esteve dentro do diretório da skill — a revisão externa mostrou
que era um bypass, e a correção está descrita em `REVISAO-EXTERNA.md`.

## O desfecho do `SC4` — o ciclo completo

O achado real virou correção, e o caminho até ela é o que o gate existe para
provocar.

**Primeiro, medir a exposição em vez de reagir ao rótulo.** "2 CVEs HIGH" não
diz se alguém está exposto. O que diz:

| Pergunta | Resposta |
|---|---|
| `ajv` é dependência de runtime? | Não — `devDependencies` |
| Quem usa `ajv`? | Só `scripts/generate-validators.mjs`, gerador de build que lê schemas **locais** |
| A saída dele está versionada? | Sim — `renderers/shared/generated-validators.mjs`, que é o que `bin/archify.mjs` carrega |
| Existe `node_modules`? | Não |
| O `SKILL.md` manda instalar? | Não |

Os CVEs são SSRF e host confusion **no parse de URI**. O único consumidor lê
JSON do disco. **Exposição real: nenhuma.**

**Mesmo assim, corrigir.** As advisories estão resolvidas na `3.1.6`; o `ajv`
pede `^3.0.1`, então a `3.1.8` entra sem conflito — uma entrada do lockfile, sem
tocar em código. Dois motivos, nenhum deles "estamos vulneráveis":

1. Protege quem um dia rodar `npm install` ali para regenerar os validadores.
   Hoje ninguém roda; a cópia vendorada é permanente e essa suposição não é.
2. Mantém o aviso do gate significando alguma coisa. Um `SC4` conhecido e nunca
   resolvido ensina o time a ignorar o aviso do archify — e o próximo achado,
   que pode ser real, chega no meio desse ruído.

O que **não** foi feito: subir o limiar nem suprimir o `SC4` no baseline.
Suprimir achado verdadeiro para ficar verde é exatamente o que a skill proíbe.

**O `integrity` foi verificado contra o tarball real** (`sha512` calculado do
`.tgz` baixado), não copiado da resposta do registry. Numa correção de supply
chain, confiar no hash que alguém te passou é repetir o problema.

**E o patch precisa sobreviver.** Corrigir um lockfile vendorado cria
divergência silenciosa com o upstream: a próxima atualização do archify apaga o
patch sem avisar. Então:

- `skills-lock.json` ganhou `localPatches`, com uma asserção **verificável**
  (`verifyContains: fast-uri-3.1.8.tgz`, `verifyAbsent: fast-uri-3.1.5.tgz`).
- `validate-harness.sh` passou a conferir isso a cada health check. Revertendo o
  patch, ele falha com *"patch perdido — falta fast-uri-3.1.8.tgz"*.
- Issue upstream: [tt-a1i/archify#463](https://github.com/tt-a1i/archify/issues/463),
  para o patch deixar de ser nosso.

**Resultado, re-escaneado:**

| | Antes do bump | Depois |
|---|---|---|
| Score | 22/100 MEDIUM | **2/100 LOW** |
| Achados | 2 (`SC4` + `SC1`) | **1 (`SC1`)** |
| Gate | avisa | **aprova** |

O `SC4` sumiu porque a causa foi corrigida, não porque foi suprimido. O `SC1`
que resta é o range `"ajv": "^8.17.1"` sem pin exato — verdadeiro, menor, e
upstream: fica visível.

Um campo que ninguém verifica é uma anotação, não um controle — a mesma lição
do `scanVerdict`, que só passou a valer quando o `validate-harness` começou a
conferir o score gravado em vez da mera presença do campo.

## O gate reprovou a si mesmo

Na primeira varredura completa depois de pronta, a **própria `skill-guard`**
saiu com **33/100 MEDIUM, 2 achados** — ambos `SC2` (External Script
Fetching), casando com o texto `curl | bash` nas linhas em que a skill
**nomeia o padrão** para quem vai ler o relatório do scanner.

É a mesma ironia do `agenfk-flow`, marcado por documentar o `curl
http://localhost:3000` que ele proíbe: **o scanner estático não distingue
mencionar de fazer.**

A saída não foi reescrever o texto. Documentação de segurança precisa poder
citar a string que descreve — quem lê o relatório tem de achar no texto o mesmo
`curl | bash` que viu no achado. Foi para o baseline, com o motivo escrito.

E aí apareceu o caso circular: suprimir os dois `SC2` fez nascer um `AE1` novo,
porque a `SKILL.md` passou a citar `.skillspector-baseline.yaml` — arquivo que
o SkillSpector **exclui de propósito** da análise de conteúdo (para que o texto
das supressões não vire achado). A referência fica `out_of_scope` e sai como
sinal de cobertura.

| | Sem baseline | Só com SC2 | Com SC2 + AE1 |
|---|---|---|---|
| Score | 33/100 | 25/100 | **0/100** |
| Achados | 2 | 1 | **0** |

Três iterações para uma skill de 114 linhas que não faz nada perigoso. É o
custo real de operar um gate — e a razão de ele precisar de um dono, não só de
uma instalação.

## A lição do piloto

Um scanner de segurança entrega **ruído com sinal dentro**, não um veredito.
O valor não está no número: está em alguém abrir os 59 achados, verificar cada
um contra o código e escrever por que 58 não contam. O gate automatiza a
pergunta; a resposta ainda é trabalho de gente.

E o inverso também vale: **score 0 não é aprovação.** Vinte skills pontuaram 0
neste scan. Isso significa "nenhum padrão conhecido casou em modo estático" —
não que sejam seguras.
