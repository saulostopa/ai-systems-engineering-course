---
title: Aula 15 — Do Markdown ao runtime executável
---

# Aula 15 — Do Markdown ao runtime executável

> A evolução deste curso: do harness que *instrui* para o harness que *executa*.

## O limite do Markdown

Até aqui, o harness era Markdown: AGENTS.md, policies, SKILL.md, templates.
Eles instruem o agente — e funcionam bem para orientação. Mas têm um teto:

| Capacidade | Markdown | Código executável |
|---|---|---|
| Impor ordem de passos | instrução ("faça X depois de Y") | grafo: o runner executa na ordem |
| Bloquear transição inválida | gate hook (se instalado) | `runner` recusa em runtime |
| Garantir "done" só com evidência | política | gate determinístico + schema |
| Forçar limites (retries, profundidade) | "não exceda..." | `Limits` aplicado em código |
| Auditoria | git log + narrativa | trilha de eventos persistida |
| Retomada | session-handoff.md | checkpoint + resume do estado |

A lição da Aula 04 continua valendo — **roteador curto + docs rotadas** — mas
agora há uma segunda camada: o que é *controle* (ordem, gates, estado, limites)
deve virar código; o que é *conhecimento* (contexto, políticas explicadas,
skills) permanece em Markdown.

## Instrução, política, contrato, controle

Quatro tipos de regra — e quatro lares:

| Tipo | Exemplo | Onde vive |
|---|---|---|
| **Instrução** | "leia o AGENTS.md antes de editar" | AGENTS.md / SKILL.md |
| **Política** | "uma feature `in_progress` por vez" | `policies/*.md` (explicação) |
| **Contrato** | `NodeInput` → `NodeOutput` tipado | **código** (schemas) |
| **Controle** | "só o runner avança status" | **código** (runner) |

Markdown **explica**; código **governa**. A regra executável tem **fonte única
de verdade**: o schema/gate/runner — não cinco markdowns que divergem.

## O que permanece em Markdown

- **AGENTS.md**: o roteador (o quê ler, como trabalhar) — nunca a autoridade de fluxo.
- **SKILL.md**: conhecimento sob demanda (como fazer X) — carregado quando a tarefa pede.
- **policies/**: a *razão* das regras (o porquê do DoD, do escopo) — a regra em si vira gate.
- **Docs e aulas**: explicam o sistema; o sistema executa sozinho.

## Por que o agente não pode ser a autoridade do workflow

O agente raciocina; o workflow **controla efeitos e estado**. Se o agente
decidisse quando "done", teríamos de volta o auto-engano da Aula 09 — agora
mecanizado em larga escala. O padrão do ADK 2 (e deste curso):

> **Agentes produzem propostas/resultados; o runner controla efeitos e estado.**

No `hard-harness`, o agente devolve `NodeOutput(proposed_next=...)` — e o
runner decide se aceita, se recusa (com evento auditável) ou se segue o grafo.
Não existe API de transição para o agente (verificado por teste).

## Exemplo executável mínimo

```sh
cd hard-harness
PYTHONPATH=. python3 examples/basic_workflow/workflow.py
# → boot → load_scope → planner → validate_plan → coder
#   → fan-out [build, tests, e2e, lint] → join → router → reviewer → evidence → close
```

## Principais aprendizados

1. Markdown instrui; código executa. Controle ≠ conhecimento.
2. Contrato e controle moram em schemas/gates/runner — fonte única de verdade.
3. Políticas explicam o porquê; gates impõem o quê.
4. O agente propõe; o runner decide. Autoridade de estado nunca é delegada.

## Verifique seu aprendizado

```
"quiz me on a Aula 15"
```

**Próxima aula**: [16 — ADK 2 e os três padrões de orquestração](/lectures/lecture-16).