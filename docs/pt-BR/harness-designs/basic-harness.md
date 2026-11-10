---
title: Harness básico (download)
---

# Harness básico (download)

> A camada de controle instalável para um repositório pequeno. O núcleo
> executável está publicado no [catálogo standalone de harnesses](https://github.com/saulostopa/ai-systems-engineering-harnesses/tree/main/harness-basic).

## Para quem é

Projetos pequenos e médios, times de 1-5 pessoas, sem infraestrutura própria
de processo. O harness básico entrega o mínimo que muda o comportamento do
agente: roteador curto, estado explícito, políticas de escopo/evidência, planos
de execução e gates mecânicos.

## Dois perfis de distribuição

| Capacidade | Núcleo standalone | Distribuição padrão do curso |
|---|---:|---:|
| Roteador, estado e políticas | sim | sim |
| Planos de execução e artefatos da entrega | sim | sim |
| Gates pre-commit/pre-push | sim | sim |
| Skills padrão em `.agents/skills/` | não | sete skills incluídas |
| Instalação explícita na própria pasta | somente alvo separado | `./install.sh --self` |

O repositório standalone continua sendo o núcleo portátil. Uma distribuição
derivada pode incluir as skills padrão e gerenciar a própria pasta do pacote.
Separar os perfis evita que a documentação prometa arquivos ou comandos que
não existem na distribuição escolhida.

## Estrutura do pacote-base

```text
harness-basic/
├── package.json
├── install.sh                # copia o payload e ativa hooks
├── templates/
│   ├── AGENTS.md             # roteador (Aula 04)
│   ├── feature_list.json     # escopo com estado (Aula 08)
│   ├── progress.md           # diário da sessão (Aula 05)
│   ├── session-handoff.md    # bilhete entre sessões (Aula 05)
│   ├── exec-plan.md          # rota da feature com evidência (Aula 13)
│   ├── policies/             # escopo, Definition of Done, evidência
│   └── init.sh               # inicialização do ambiente (Aula 06)
├── scripts/                  # saúde, gates, artefatos e scan de skills
├── tests/                    # testes dos gates mecânicos
└── .githooks/
    ├── pre-commit
    └── pre-push
```

## Instalar o núcleo standalone

A partir da raiz do checkout de `harnesses`:

```bash
./harness-basic/install.sh /caminho/absoluto/do/projeto
cd /caminho/absoluto/do/projeto
./init.sh
./scripts/validate-harness.sh
```

A pasta de destino deve existir. Quando ela é um repositório Git, o instalador
configura `core.hooksPath=.githooks`. Caminhos existentes são protegidos;
`--force` permite sobrescritas e deve ser seguido pelo health check do harness.

## Instalar uma distribuição derivada nela mesma

Quando a pasta do pacote também será o primeiro repositório gerenciado, o
instalador derivado usa um contrato explícito de auto-instalação:

```bash
git init                       # somente se o Git ainda não estiver inicializado
./install.sh --self
./init.sh
```

`--self` é intencionalmente diferente de `./install.sh .`: a flag explícita
confirma que pacote e destino são a mesma pasta. O instalador do núcleo
standalone espera um destino separado; confira o README da distribuição antes
de usar esse modo.

## Skills padrão do curso

A distribuição padrão do curso instala estas skills em `.agents/skills/`:

| Skill | Responsabilidade |
|---|---|
| `feature-report` | Relatório acessível com evidências rastreadas a comandos e diffs |
| `feature-quiz` | Quiz adaptativo em quatro níveis sobre a feature entregue |
| `feature-archify` | Diagrama validado da feature concluída |
| `skill-guard` | Scan de skills externas antes da instalação |
| `qa-playwright-e2e` | Cobertura E2E resiliente com Playwright |
| `qa-perf-triage` | Diagnóstico de concorrência e regressões de latência |
| `agentic-navigation` | Aceite visual de um fluxo real da aplicação |

`feature-report` e `feature-quiz` compartilham os assets Eleanor em
`.agents/skills/assets/`. `feature-archify` é o wrapper do curso; a renderização
também precisa da skill de terceiros `archify`, instalada somente depois do
`skill-guard`. O gate E2E permanece inativo até `.harness/config.yaml` conter
um bloco `qa:`.

## Checklist da primeira feature

1. Personalize as seções 1 e 7 do `AGENTS.md`.
2. Substitua os exemplos em `feature_list.json`.
3. Marque exatamente uma feature como `in_progress`.
4. Crie o plano em `docs/exec-plans/active/`.
5. Rode `./init.sh` e `./scripts/validate-harness.sh`.
6. Peça ao agente para implementar, testar e registrar comando → esperado → real.

## O que os gates fazem

| Gate | Quando | Comportamento |
|---|---|---|
| `pre-commit` | todo commit | Exige exatamente uma feature `in_progress`; aplica a política E2E quando configurada |
| `pre-push` | todo push | Bloqueia arquivos ausentes, estado inválido, planos inconsistentes ou registros de skills inválidos |
| `gate-skill-scan.sh` | antes de instalar skill externa | Executa o gate estático e fixado do SkillSpector e registra evidência |

## Evolução natural

| Quando | Evolua para |
|---|---|
| Vários times ou repositórios | [Harness enterprise](/pt-BR/harness-designs/enterprise-harness) |
| QA específica de aplicação | [App Harness](/pt-BR/harness-designs/app-harness) |
| Recuperação de contexto do repositório/negócio | [RAG Harness & Area Copilots](/pt-BR/harness-designs/rag-harness) |
| Conhecimento específico de domínio | [Harnesses de domínio](/pt-BR/harness-designs/domain-harnesses) |

## Garantia

Nenhum arquivo é decorativo: cada um responde a uma pergunta do agente ou
impõe uma fronteira do processo. Se um arquivo não é lido, validado ou usado
por um gate, ele é dívida — não rigor.
