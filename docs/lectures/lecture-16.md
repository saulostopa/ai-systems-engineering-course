---
title: Aula 16 — ADK 2 e os três padrões de orquestração
---

# Aula 16 — ADK 2 e os três padrões de orquestração

> Referência conceitual obrigatória:
> [ADK 2 Orchestration codelab](https://codelabs.developers.google.com/adk2/instructions).
> Três padrões, um eixo: **quem decide o próximo passo** — o grafo que você
> desenhou, o LLM ou o seu código em runtime.

## O eixo de decisão

| Padrão | Quem decide o próximo passo | Quando usar |
|---|---|---|
| **1 · Graph** | o grafo que você desenhou | você consegue desenhar o fluxo antes da entrada chegar |
| **2 · Collaborative** | o LLM (coordena especialistas) | o time é conhecido, mas a requisição escolhe o subconjunto |
| **3 · Dynamic** | seu código, em runtime | a *forma* do trabalho depende da entrada |

Uma frase do codelab para guardar: *"predictable work stays as functions;
clear rules become explicit routing; reasoning uses the model."*

## 1 · Graph workflows

Quando o fluxo é conhecível a priori, desenhe o grafo:

```
START ─► fetch_weather ─┐
START ─► analyze_course ┼─► JoinNode ─► strategy_agent
START ─► pull_fitness ──┘
```

- **funções e agentes são peers** — o trabalho previsível custa 0 LLM;
- **fan-out paralelo** — três arestas saindo de START já são paralelismo;
- **JoinNode** — aguarda TODAS as fontes e agrega por nome;
- **router determinístico** — um `if`, não o modelo:
  `route = "HOT" if temp >= 70 else "COLD" ...` com **DEFAULT_ROUTE obrigatório**;
- agentes só onde há raciocínio (estratégia, não roteamento).

O custo: o codelab mostra a versão "um agente gigante" fazendo 4 chamadas e
inventando números — o grafo faz **1 chamada** com os dados vindo de código.

## 2 · Collaborative agents

Quando o time é fixo mas o pedido escolhe os membros:

- **`chat`** (default de subagent) — transfere a conversa inteira para um
  especialista; nunca volta automaticamente;
- **`single_turn`** — cada especialista vira uma *ferramenta*; o coordenador
  chama o subconjunto **em paralelo**, cada um devolve resultado **tipado**,
  e o coordenador sintetiza;
- **`task`** — conversa com *linha de chegada tipada*: pergunta até coletar
  os campos, pausa, e retorna via `finish_task` com objeto validado.

A escolha do modo em uma pergunta: *"o usuário precisa falar com ele — até
quando?"* → chat (indefinidamente) · task (até os campos) · single_turn (nunca).

## 3 · Dynamic workflows

Quando a forma do trabalho nasce da entrada:

- **largura em runtime** — `parallel_worker=True` fana um worker sobre N itens
  decididos pelo LLM;
- **recursão escrita por você** — o worker chama a si mesmo via `ctx.run_node`;
- **limites em código** — `if finding.needs_deeper and depth < MAX_DEPTH` é
  SEU código, não configuração. O codelab é explícito: a recursão é sua, o
  freio é seu.

⚠️ O teto cresce rápido: `MAX_DEPTH=3` leva ~30 chamadas a ~93.

## Aplicação aos harnesses deste curso

| Harness | Padrão dominante | Onde |
|---|---|---|
| Básico (B1) | **Graph** | pipeline plan → code → test → review → close |
| Enterprise (B2) | **Graph + Collaborative** | workflow engine + especialistas por área |
| App (C) | **Graph** | fan-out de testes/E2E/a11y/navegação + join |
| RAG/Area Copilot (D) | **Graph (com nó de contexto)** | RAG é *provedor de contexto*, nunca orquestrador |
| Domínios (E) | **Graph (mesmo núcleo)** | Finance/Games/Commercial fornecem skills e schemas |

## Como escolher (árvore do codelab)

```
SequentialAgent/ParallelAgent/LoopAgent resolvem?  → use-os, pare
└─ Não — preciso de router, join ou nós não-agentes
   ├─ Consigo desenhar antes da entrada?  → Graph
   └─ Não
      ├─ Time conhecido, pedido escolhe?  → Collaborative
      └─ Forma depende da entrada?        → Dynamic
```

## Principais aprendizados

1. Três padrões, um eixo: quem decide o próximo passo.
2. Função para previsível; router para regra clara; agente para raciocínio.
3. DEFAULT obrigatório em routers — rota desconhecida nunca morre em silêncio.
4. Dynamic = código; logo, os limites são seus, em código.
5. O `hard-harness` implementa o padrão Graph como núcleo (Aula 17) e deixa
   Collaborative/Dynamic como evolução — o ADK é inspiração, não dependência.

## Verifique seu aprendizado

```
"quiz me on a Aula 16"
```

**Próxima aula**: [17 — Construindo um Hard Harness](/lectures/lecture-17).