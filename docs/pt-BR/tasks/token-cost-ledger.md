---
title: Backlog — registro de tokens e custos
---

# Backlog — registro de tokens e custos

Status: **em andamento** · Priority: **P1** · Escopo: `harness-usage`, `rag-harness`, ADK + RAG + Jev e hard harness

## Por que isso entra no backlog

Cada chamada a uma LLM feita por um harness gasta tokens e, com provedores
hospedados, dinheiro: decisões do Jev, o modelo de conversa, embeddings da
indexação e de cada pergunta e os agentes do hard harness. Até agora só o hard
harness contava tokens, e nenhum harness registrava quanto custou uma pergunta,
uma feature ou um índice. Sem essa evidência o curso não consegue comparar
provedores (por exemplo, o [Jev pela TypeSafe](/pt-BR/tasks/jev-typesafe-decisions))
nem manter um orçamento mensal.

## Decisões (2026-10-29)

| Tema | Decisão |
|---|---|
| Armazenamento | Um arquivo JSONL por mês dentro de cada repositório-alvo, em `.harness/usage/AAAA-MM.jsonl`, ignorado pelo Git |
| Orçamento | `HARNESS_BUDGET_USD`, padrão de US$ 25 por mês somando todos os registros; aviso em 80% e 100%, sem bloquear |
| Primeira entrega | `rag-harness`, `adk-rag-harness` e `hard-harness` |
| Relatórios | Tabela no terminal, CSV, Markdown e um painel HTML autocontido |

## Formato do registro

Uma linha por chamada ao provedor, só acrescentando. Perguntas, respostas,
código e chaves nunca são gravados.

```json
{"schema": 1, "ts": "2026-10-29T22:10:03Z", "run_id": "…", "request_id": "…",
 "harness": "adk-rag-harness", "component": "decision",
 "provider": "openrouter", "model": "typesafe/jev-router", "routed_model": "deepseek/…",
 "input_tokens": 812, "output_tokens": 64, "cached_tokens": 0,
 "cost_usd": 0.00041, "cost_source": "provider",
 "latency_ms": 930, "status": "ok", "error_kind": null,
 "project": "biometrik-app-reactnative", "feature": "jev-adk-rag-harness"}
```

- `component`: `decision`, `chat`, `embedding_index`, `embedding_query` ou
  `agent`.
- `request_id` agrupa todas as chamadas feitas para uma pergunta.
- `routed_model` é o modelo que um roteador como o `typesafe/jev-router`
  escolheu.
- `cost_source`: `provider` (o OpenRouter devolve `usage.cost` em US$),
  `price_table` (tokens × tabela de preços do OpenRouter em cache), `local`
  (Ollama, custo zero) ou `unknown`.
- `feature` vem do `active_feature_id` do repositório-alvo, quando existe.

## Relatórios

- Totais por dia e por mês, com projeção até o fim do mês e situação do
  orçamento.
- Por componente, provedor, modelo e modelo escolhido pelo roteador.
- Por projeto e por feature.
- Por pergunta (`request_id`): média, p50 e p95.
- Custo de indexação e taxa de erros por provedor.

## Critérios de aceite

- Toda chamada paga nos três harnesses grava uma linha, inclusive quando falha.
- Gravar o registro nunca quebra um harness: um erro de I/O é avisado uma vez e
  a chamada segue.
- Um registro dentro de um repositório Git que não esteja ignorado gera aviso.
- O aviso de orçamento aparece em 80% e 100% do `HARNESS_BUDGET_USD`.
- Os relatórios leem vários repositórios de uma vez.
- Nenhuma pergunta, resposta, trecho de código ou credencial chega ao registro.

## Referências

- [Feature do ADK + RAG + Jev](/pt-BR/tasks/adk-rag-jev-harness)
- [Decisões do Jev pela TypeSafe](/pt-BR/tasks/jev-typesafe-decisions)
