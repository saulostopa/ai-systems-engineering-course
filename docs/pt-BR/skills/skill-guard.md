---
title: skill-guard
---

# skill-guard — nenhuma skill entra sem scan

Skill wrapper + **gate executável** que integra o
[SkillSpector](https://github.com/NVIDIA/SkillSpector) (NVIDIA, Apache-2.0) ao
fluxo de instalação de skills do harness.

Todo o resto deste curso trata a skill como *a coisa boa*: o pacote de
instrução que ensina o agente a fazer algo bem. Esta página trata a skill como
**superfície de ataque** — porque ela é as duas coisas ao mesmo tempo.

## Por que isto existe

Uma skill entra no contexto do agente e passa a **dirigir o comportamento do
modelo**. Ela chega por `npx skills add`, por um link no Slack, por um
copiar-e-colar — sem revisão de código, sem sandbox, sem CI. É a forma mais
barata de comprometer um agente e a mais cara de auditar depois que já rodou.

No levantamento da NVIDIA sobre 31.132 skills: **26,1% continham
vulnerabilidades** e **5,2% mostravam sinal de intenção maliciosa**.

O harness já bloqueia commit sem feature declarada (Aula 07) e código sem
evidência (Aula 09). Uma skill de terceiro entrando sem qualquer gate era o
buraco no meio disso.

## Entregue

| Peça | O que é |
|---|---|
| `skills-artifacts/skill-guard/SKILL.md` | Skill wrapper no padrão do curso — quando escanear, como ler o veredito, o que registrar |
| `harness-basic/scripts/gate-skill-scan.sh` | **O gate**: bloqueia a instalação de skill reprovada (exit 1) |
| `skills-lock.json` | Veredito (`scanVerdict`) gravado por skill — quem aprovou, com qual scanner, quando |
| `pilots/skillspector-demo/` | Evidência: scan real de todas as skills do repositório + o fixture que prova que o gate bloqueia |

## O gate

```sh
harness-basic/scripts/gate-skill-scan.sh <alvo>   # dir, SKILL.md, .zip ou URL de repo
harness-basic/scripts/gate-skill-scan.sh --all    # todas as skills do repositório
```

Três decisões de projeto, e o motivo de cada uma:

**Docker, não `pip install`.** O scanner é Python 3.12+; a máquina do time tem
o Python que tem. A imagem é construída do `Dockerfile` oficial na primeira
execução e reusada depois. Zero dependência do ambiente local.

**Estático (`--no-llm`), não semântico.** Um gate precisa de veredito
**determinístico**: o mesmo alvo dá o mesmo resultado, em CI, offline, sem
chave de API e sem custo por scan. A etapa semântica pega o que o estático não
vê — mas um gate que muda de opinião entre execuções não é um gate.

**Pin por commit, não por tag.** O gate confere que `v2.11.2` ainda aponta para
`69dcdfb7…` antes de confiar no scanner. Uma tag remota pode ser reescrita: o
nome fica igual e o código muda. Fixar uma ferramenta de supply chain por um
ponteiro móvel seria a própria falha que ela procura.

## Ler o veredito

| Score | Severidade | O gate |
|---|---|---|
| 0-20 | LOW | **aprova** (exit 0) |
| 21-50 | MEDIUM | **avisa** — leia os achados e decida |
| 51-100 | HIGH / CRITICAL | **bloqueia** (exit 1) |

Relatórios JSON completos em `.harness/skill-scans/<caminho-da-skill>.json`. Os achados
são identificados por padrão — `SC2` (`curl \| bash`), `PE3` (acesso a
credenciais), `E1`/`E4` (transmissão externa, vazamento de contexto), `P1`/`P2`
(instruction override, instruções ocultas), `TM2` (tool misuse) — entre 71
padrões em 17 categorias, incluindo *MCP tool poisoning*.

## Falsos positivos — o baseline

Um scanner estático entrega **ruído com sinal dentro**. Quando um achado é
falso positivo verificado, ele entra num baseline — nunca some por ajuste de
limiar:

```yaml
# .harness/baselines/agents-skills-archify.yaml
rules:
  - id: "EA3"
    message: "*NOT LIMITED TO*"
    reason: >-
      Casa com a frase da licença SIL Open Font embutida no template.
```

O baseline fica em `.harness/baselines/<slug>.yaml`, **fora da árvore
escaneada**, e é montado somente-leitura no container. Um por skill — nunca um
global, que desarmaria a regra para todas as outras.

::: danger Por que não dentro da skill
A primeira versão guardava o baseline em `<skill>/.skillspector-baseline.yaml`,
com o argumento de que ficaria "revisável em PR ao lado do código que perdoa".
A revisão externa derrubou o argumento: é **circular** — o mesmo PR que traz a
skill traz o baseline. Um autor hostil iteraria o scanner até escrever um YAML
que suprime todos os próprios achados, e o gate passaria a medir o que ele
escolheu. "Nenhuma skill entra sem passar pelo scanner" viraria "entra qualquer
skill que saiba escrever um YAML".

Hoje o gate **bloqueia** qualquer alvo que traga um baseline dentro de si.
:::

O gate aplica o baseline sozinho quando encontra o arquivo. Toda regra exige
`reason`: uma supressão sem motivo escrito é uma decisão que ninguém poderá
revisar depois.

**Nunca suprima um achado que você não abriu.** No piloto, 57 dos 59 achados do
`archify` eram ruído — mas isso só é uma afirmação legítima porque os 59 foram
lidos um a um. Ver [`pilots/skillspector-demo/scan-results.md`](https://github.com/svslwm/harness-plannig/blob/develop/pilots/skillspector-demo/scan-results.md).

::: tip O gate reprovou a si mesmo
Na primeira varredura, a própria `skill-guard` saiu com 33/100 — dois `SC2`
casando com o texto `curl | bash` nas linhas em que ela **nomeia o padrão**.
O scanner estático não distingue mencionar de fazer. A saída não foi
parafrasear o texto (quem lê o relatório precisa achar a mesma string no
documento), foi o baseline com o motivo escrito.
:::

## Os limites — leia antes de confiar

Um gate sobre o qual você mente é pior que nenhum gate, então:

- **Score 0 significa "nenhum padrão conhecido", não "é seguro".** O modo
  estático julga **forma**, não intenção.
- **O estático é forte em comando e fraco em prosa.** No fixture de teste,
  o scanner pegou `curl | bash` (SC2), leitura de `~/.ssh` (PE3) e as quatro
  transmissões externas (E1) — e **não** marcou o "ignore quaisquer restrições
  anteriores" nem o pedido de repetir o prompt de sistema. Instrução maliciosa
  escrita em português corrido é justamente o que a etapa semântica veria.
- **`cobertura: partial` é o caso comum, não a exceção.** Parte do conteúdo
  não foi inspecionada; o número aparece ao lado do score de propósito.
- **O gate vale para o que passa por ele.** Uma skill instalada à mão, fora do
  `skills-lock.json`, não foi escaneada por ninguém.
- **O pin cobre a tag remota, não a imagem local.** O gate confere que
  `v2.11.2` ainda aponta para o commit fixado, mas reusa qualquer imagem local
  com esse nome. Um cache de CI envenenado com uma `skillspector:v2.11.2`
  adulterada passaria com "pin confirmado" na tela. Onde isso importa, force a
  reconstrução: `docker rmi skillspector:v2.11.2` antes de rodar o gate.

## Regras

- Escaneie **antes de baixar** — `gate-skill-scan.sh <url>` busca dentro do
  container. Clonar para escanear depois já pôs o código na máquina.
- Skill aprovada entra no `skills-lock.json` com o `scanVerdict` que a aprovou.
- Origem mudou, veredito morreu: rode de novo.
- **Nunca suba o limiar para fazer uma skill passar.** Instalar algo que o gate
  bloqueou é uma decisão do usuário, tomada com os achados na frente e
  registrada — não um ajuste silencioso de `SKILL_GUARD_MAX_SCORE`.

## Revisão externa

Este gate passou por uma **revisão adversarial independente** depois de pronto,
e ela achou coisa séria: o baseline e o marcador de fixtures moravam dentro do
diretório da skill — os dois controlados pela entidade que o gate deveria estar
medindo — e um `SKILL_GUARD_MAX_SCORE` não-inteiro desarmava o gate em
silêncio, aprovando score 70.

O relatório completo (11 achados, com os cenários de falha reproduzidos) está
em [`pilots/skillspector-demo/REVISAO-EXTERNA.md`](https://github.com/svslwm/harness-plannig/blob/develop/pilots/skillspector-demo/REVISAO-EXTERNA.md),
junto do prompt que a produziu.

É a parte mais instrutiva do piloto: **um gate de segurança escrito com
cuidado ainda tinha um bypass**, e quem o escreveu não o viu. Revisão
independente não é formalidade de processo.

**Relacionado**: [Criar uma skill nova](/pt-BR/skills/how-to-create) ·
[feature-archify](/pt-BR/skills/feature-archify) · [Visão geral](/pt-BR/skills/)
