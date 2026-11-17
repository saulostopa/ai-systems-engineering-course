---
title: Harness grande (multi-time)
---

# Harness grande (multi-time)

> O harness para projetos onde vários times trabalham: o básico + camadas de
> governança, fluxo e observabilidade. Definido por **contratos**, não por um produto.

## Para quem é

Projetos grandes, múltiplos times, muitos agentes em paralelo, necessidade de
auditoria e medição. O harness grande não substitui o básico — **ele o envolve**:
cada time mantém seu esqueleto; a camada grande adiciona fluxo,
gatekeepers, telemetria e relatórios.

## As duas camadas

Tudo abaixo falha na prática se uma coisa for errada: **onde cada peça mora**.
O harness grande se instala em dois lugares, e a divisão não é questão de gosto.

```
~/wm-harness/                  ← A · orquestrador: 1× por máquina, acima dos projetos
├── engine/                      runner, gates, CLI
├── flows/                       definições de fluxo compartilhadas pela organização
├── telemetry/                   agregação cross-projeto
└── ui/                          kanban, dashboards

<repo-do-time>/                ← B · controle: no repo, no PR, revisável
├── AGENTS.md
├── feature_list.json            escopo e estado por feature
├── progress.md · session-handoff.md
├── policies/
├── .harness/
│   ├── config.yaml              qual fluxo, qual versão do engine
│   ├── state.json               estado da execução corrente
│   └── events.jsonl             trilha append-only
└── docs/exec-plans/
    ├── active/                  planos em voo
    └── done/                    concluídos, com evidência anexada
```

A regra que decide o corte:

> **O orquestrador é dono do *como*. O repositório é dono do *o quê* e do
> *o que aconteceu*.**

Definições de fluxo, gates e agregação são compartilhados e versionados
centralmente — uma curva de aprendizado para a organização inteira. Escopo,
planos, evidência e estado moram no repo, viajam no PR e são revisados como código.

E o teste para qualquer caso em dúvida:

> **Se apagar o orquestrador da máquina fizer o projeto perder informação sobre
> si mesmo, a peça está na camada errada.**

Cada desenvolvedor instala a camada A uma vez. A camada B chega no repo pelo
instalador do orquestrador e é pequena de propósito: sem engine, sem
`node_modules`, sem banco — só o que controla as features.

::: warning A falha que isso evita
Um workflow engine que guarda itens, comentários e evidências num banco central
*fora* do repo reprova no teste acima: apague a ferramenta e o histórico do
projeto some. Também quebra a [Aula 03](/pt-BR/lectures/lecture-03) — o
repositório deixa de ser o sistema de registro. Armazenamento central serve para
**agregação** (telemetria, visão cross-time); não serve como **única** cópia.
:::

## As camadas de capacidade

```
┌─────────────────────────────────────────────────────┐
│ 4. Observabilidade  (telemetria, log-friction,      │
│    dashboards, health check do harness)             │
├─────────────────────────────────────────────────────┤
│ 3. Workflow engine  (itens, fluxos, gatekeeper,     │
│    evidência, DONE só com validação)                │
├─────────────────────────────────────────────────────┤
│ 2. Governança       (políticas, gates mecânicos,    │
│    hooks, revisão cruzada)                          │
├─────────────────────────────────────────────────────┤
│ 1. Esqueleto        (harness básico por projeto:    │
│    AGENTS.md, feature list, políticas)              │
└─────────────────────────────────────────────────────┘
```

### Camada 1 — Esqueleto (por projeto)

O [harness básico](/pt-BR/harness-designs/basic-harness). Cada time tem o seu, com
a feature list da sua área. Nada muda aqui quando você escala.

### Camada 2 — Governança

O que o básico já tem (gatekeeper de commit, validação) vira um
**contrato organizacional**:

| Mecanismo | Básico | Grande |
|---|---|---|
| Gate de commit | UMA feature in_progress | + escopo declarado obrigatório (policies/scope-control.md) |
| Gate de push | Harness saudável | + relatório de PR obrigatório, CI com validação |
| Verificação | Build + testes | + gate de E2E para frontend (factory: `frontend-qa-gate.sh`) + revisão cruzada por fluxo |
| Exceção | Bypass local consciente | Bypass registrado e auditável (log + motivo) |

A regra da governança: **se o processo depende de boa vontade, ele não acontece**
(Aula 07). Tudo vira script, hook ou passo de fluxo.

### Camada 3 — Workflow engine

Esta camada é um **contrato**, não um produto. Qualquer engine que satisfaça os
cinco requisitos abaixo serve; a escolha da implementação vem depois e é reversível.

| Requisito | O que significa | Aula |
|---|---|---|
| **Itens com hierarquia e tipo** | EPIC → STORY → TASK/BUG; o `feature_list.json` ganha parentesco e fluxo | 08 |
| **Fluxos configuráveis** | cada tipo de trabalho tem passos com **critério de saída obrigatório** | 13 |
| **Gatekeeper mecânico** | edição só dentro de um item ativo; **DONE inalcançável por atalho** | 07 |
| **Evidência como passo** | teste registrado PASSED/FAILED *antes* de concluir — o autoengano vira falha de fluxo | 09 |
| **Trilha auditável** | histórico de status, comentários, evidência: o "quem, quando, por quê" de cada item | 11 |

Escrever como contrato é o que torna a camada portátil. Um time pode começar com
arquivos e hooks, migrar para um engine compartilhado depois, e as outras três
camadas nem percebem.

### Camada 4 — Observabilidade

A camada que distingue um harness de um processo burocrático como sistema de
melhoria contínua (Aula 11):

| Métrica | Fonte |
|---|---|
| Tempo por passo/item | timestamps do workflow |
| Fricção (retries, loops, travamentos) | `log-friction` / `log-event.sh` |
| Custo por feature | telemetria de tokens |
| Saúde do harness | `validate-harness.sh` + health check da camada 3 |
| Qualidade | testes falhando antes do verde, retomadas |

Regra de ouro: **fricção não registrada é dívida de observabilidade**. Todo ponto
de fricção vira entrada de log — e toda entrada de log é candidata a melhoria do
harness.

## Planos de execução, no repo

O contrato da camada 3 precisa de um lugar para a decomposição de uma feature.
Esse lugar é `docs/exec-plans/`, e ele segue três regras.

**A pasta é orçamento de contexto.** No boot o agente lê só `active/` — um
conjunto pequeno e limitado ([Aula 06](/pt-BR/lectures/lecture-06)). Planos
concluídos vão para `done/` para que a leitura nunca cresça sem limite
([Aula 04](/pt-BR/lectures/lecture-04)).

**O front-matter é a verdade.** O status autoritativo é um campo dentro do plano,
nunca a localização dele. Duas fontes que podem discordar uma hora discordam.

O id é o nome do branch — `feature/OEM-123`, `bugfix/AC-455`,
`release/EST-3445` — então plano e branch são a mesma coisa. O arquivo achata a
barra, porque barra é separador de caminho.

```markdown
docs/exec-plans/active/feature-OEM-123.md
---
id: feature/OEM-123
status: in_progress
flow: feature-default
exit_criteria:
  - build verde
  - e2e passando
---

# Passos
1. [x] escopo declarado
2. [ ] implementação
3. [ ] evidência registrada

# Evidência
(obrigatória antes de status: done)
```

**O gate reconcilia os dois.** O `validate-harness.sh` falha quando a localização
diverge do status, e quando um plano marcado `done` não tem bloco de evidência.
Arquivar deixa de ser convenção que alguém lembra e vira mecânico — que é o
argumento inteiro da [Aula 07](/pt-BR/lectures/lecture-07).

Cada artefato mantém um papel distinto, sem sobreposição:

| Artefato | Papel | Aula |
|---|---|---|
| `feature_list.json` | o **mapa** — o que existe e em que estado | 08 |
| `docs/exec-plans/active/` | a **rota** — decomposição da feature em voo, com critério de saída | 13, 14 |
| `docs/exec-plans/done/` | o **registro** — o que aconteceu, com evidência | 09, 11 |
| `progress.md` / `session-handoff.md` | continuidade de **sessão** | 05 |

## O modelo multi-time

Cada time = um projeto com seus itens e fluxos, **no mesmo framework**:

```
Time Catálogo   (projeto A) ──┐
Time Fipe       (projeto B) ──┼──▶ workflow engine (orquestrador compartilhado)
Time Finanças   (projeto C) ──┘        │
                                       ├── agregação central (telemetria)
                                       └── relatório por time
```

Benefícios: um único padrão (uma curva de aprendizado), telemetria
agrega por time, e governança escala sem reinventar.

Repare no que **não** atravessa a seta: escopo, planos e evidência de cada
projeto ficam no repositório dele. O orquestrador lê para agregar; não é a casa
deles.

## Escopo — o harness grande só onde você quer

O harness grande precisa de uma decisão de **escopo**: ele deve agir apenas nos
projetos que aderiram. A mecânica:

- o gatekeeper **verifica o caminho do arquivo** contra `.harness/config.yaml`
  e só age dentro de projetos gerenciados (fail-open fora deles);
- regras e skills são instaladas **no projeto** (`.claude/skills/` ou
  `.agents/skills/`, `AGENTS.md` do repo), não globalmente;
- fora do projeto: agente 100% independente; dentro: workflow completo.

Instalar regras globalmente é o erro comum: faz todo repositório da máquina
herdar um workflow ao qual nunca aderiu. A independência entre agentes na mesma
máquina não é negociável.

## Implementações

As camadas acima são o desenho. Implementá-las é uma escolha separada e
reversível — e mais de uma opção funciona:

| Opção | Onde encaixa | Trade-off |
|---|---|---|
| **Arquivos + hooks** (harness básico estendido) | organizações pequenas, primeiro passo | zero infraestrutura; agregação cross-projeto é manual |
| **Issue tracker + CI** (Jira, GitHub Projects + Actions) | times que já vivem no tracker | reaproveita ferramenta existente; gates dependem da disciplina do CI |
| **Engine dedicado** | muitos times, necessidade de telemetria | enforcement mais forte; mais um serviço para manter no ar |

::: tip Referência interna — AgEnFK
O `agenfk` é um engine construído pelo time de Car Sales que cobre as camadas 3
e 4 (itens, fluxos, gatekeeper, evidência, telemetria, UI Kanban). Se você é da
um time e quer uma implementação pronta, vale olhar.

É **referência, não requisito**: nenhum harness deste curso depende dele, e
nenhuma aula o exige. Dois pontos para conferir contra a regra acima antes de
adotar: o estado dele mora num SQLite central fora do repositório, e a
inicialização espera o Claude Code instalado.
:::

## Maturidade — o que existe hoje

Esta página é um **blueprint**. Parte dela é código que dá para instalar agora;
parte ainda é contrato esperando implementação. Ler como produto pronto seria um
erro, então o estado honesto:

| Camada | Estado hoje | Onde |
|---|---|---|
| A · Orquestrador | **Pronto e instalável** — CLI `wm-harness`: adopt, status, check, plan, report | `enterprise-harness/install.sh` |
| 1 · Esqueleto | **Pronto e instalável** | `harness-basic/install.sh` |
| 2 · Governança | **Pronto** — gate de commit, health check, hooks pre-commit/pre-push | `harness-basic/scripts/`, `.githooks/` |
| 3 · Workflow engine | **Funcionando, em arquivo**: os fluxos dirigem os planos, o gate reconcilia localização e status | `enterprise-harness/flows/`, `docs/exec-plans/` |
| 4 · Observabilidade | **Parcial** — registro de fricção e agregação cross-projeto funcionam; não há UI nem série histórica | `wm-harness report`, `log-event.sh` |

## Começando hoje

Instale o orquestrador uma vez, numa pasta raiz acima dos seus projetos, e
adote os repositórios que aderiram:

```sh
enterprise-harness/install.sh --prefix ~/wm/wm-harness --projects ~/wm
wm-harness adopt ~/wm/catalogo
wm-harness status
```

O [Projeto 06](/pt-BR/projects/project-06) percorre o ciclo inteiro, incluindo o
passo que mais importa: apagar o orquestrador e ver os projetos continuarem
funcionando.

Para um repositório pequeno sozinho, nada disso é necessário — o
`harness-basic/install.sh` entrega as camadas 1 e 2 por conta própria.

O que ainda falta: não há UI, nem servidor, nem sincronização entre máquinas.
A agregação é um relatório de CLI calculado na hora a partir dos repositórios, e
série histórica não fica guardada em lugar nenhum. Esses são os motivos para
buscar um engine dedicado, não motivos para esperar antes de começar.

::: info Sobre os pilotos do EPIC G
Os pilotos rodaram em 2026-09-12 e estão registrados em `pilots/`: o **G1**
instalou o harness básico num repo real (`pricing-cli`), o **G2** validou a
camada de QA do app harness, o **G3** colocou o Area Copilot para trabalhar em
finanças, e o **G4** consolidou as métricas. Nenhum deles exercitou a camada 3
com engine — que é exatamente a lacuna que esta página descreve.
:::

## Gateway de Decisão e Roteamento com Jev

Em uma estrutura corporativa multi-time, chamadas irrestritas a LLMs em dezenas de repositórios adotados explodem rapidamente os custos e introduzem alta dispersão de latência. A Camada A (`~/wm-harness/`) integra a [arquitetura de decisão Jev](/pt-BR/reference/jev) como um gateway operacional:

- **Roteador de Modelos Corporativo**: Direciona requisições de desenvolvedores e agentes para modelos Pequenos ($), Médios ($$) ou Grandes ($$$) com base na complexidade da tarefa, protegendo o orçamento da organização.
- **Guardrails de Tool Calls e Segurança**: Intercepta chamadas de ferramentas nos workflows com políticas determinísticas de `permite`, `pergunta` (HITL) ou `nega`, blindando deploys destrutivos ou vazamento de segredos.
- **Labeling em Massa e Triagem de Conformidade**: Pontua em lote e classifica a conformidade de repositórios, tendências de cobertura de testes e higiene de commits sem os custos pesados de inferência generativa.

**Relacionados**: [Harness básico](/pt-BR/harness-designs/basic-harness) ·
[App Harness](/pt-BR/harness-designs/app-harness) · [Harnesses de domínio](/pt-BR/harness-designs/domain-harnesses) ·
[Harness ADK + RAG + Jev](/pt-BR/harness-designs/adk-rag-jev-harness)

