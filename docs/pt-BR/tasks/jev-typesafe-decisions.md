---
title: Backlog — decisões do Jev pela TypeSafe
---

# Backlog — decisões do Jev pela TypeSafe

Status: **backlog** · Priority: **P1** · Escopo: harness ADK + RAG + Jev

## Por que isso entra no backlog

Hoje o harness ADK + RAG + Jev decide por
`HARNESS_DECISION_PROVIDER=openrouter-system-one` com
`OPENROUTER_DECISION_MODEL=typesafe/jev-router`. Essa rota é útil, mas é um
roteador de modelos: o Jev escolhe um modelo (o Kimi respondeu os testes do
Biometrik em 2026-10-29) e é esse modelo que preenche o contrato JSON da
decisão. A confiança é informada pelo próprio modelo, como faria um modelo
local no Ollama, então o gate tripartite (`execute`, `confirm`,
`human_review`) continua apoiado na opinião de uma LLM sobre si mesma.

O endpoint `/v1/systemone` da TypeSafe é o serviço de decisões tipadas que o
curso descreve ("a LLM escreve, o Jev decide"). O harness já traz os
adaptadores — `JevDecisionProvider` (sem dependências) e
`TypeSafeSdkDecisionProvider` (extra `[jev-sdk]`), escolhidos com
`HARNESS_DECISION_PROVIDER=jev` — e o `evals/run_jev_evals.py`, mas esse modo
nunca foi validado contra o serviço real.

## Objetivo

Transformar o `jev` (TypeSafe System One) em um provedor de decisões validado,
compará-lo com o `typesafe/jev-router` e com o modo local do Ollama nas mesmas
perguntas e decidir com evidência qual vira o padrão.

## Evolução proposta

1. **Credencial.** Ler a `TYPESAFE_API_KEY` do ambiente ou de um arquivo local
   fora do repositório, como já acontece com a chave do OpenRouter. Nunca
   registrar, imprimir ou commitar a chave; falhar fechado com mensagem clara
   quando ela faltar.
2. **Teste ao vivo.** Rodar o `evals/run_jev_evals.py` e o app do ADK com
   `HARNESS_DECISION_PROVIDER=jev`, com o RAG de demonstração e com um índice
   real.
3. **Avaliação comparativa.** Passar os golden prompts e um conjunto de um
   repositório real (documentação, código, sem busca, tentativas de injeção,
   pedidos ambíguos) por `jev`, `openrouter-system-one`
   (`typesafe/jev-router`) e `ollama-system-one` (`qwen2.5:14b`). Registrar
   rota, coleção, estratégia, confiança, latência, tokens e custo por decisão.
4. **Calibrar o gate.** Verificar se a confiança da TypeSafe separa decisões
   certas de erradas melhor que a autodeclarada e só ajustar `auto_threshold` e
   `review_threshold` a partir dessa evidência.
5. **Escolher o padrão.** Manter o `typesafe/jev-router` como padrão, a menos
   que o `jev` vença em acerto ou calibração com custo aceitável; documentar a
   escolha na aula 18 e no projeto 06.

## Critérios de aceite

- `HARNESS_DECISION_PROVIDER=jev` roda de ponta a ponta no `adk web` com um
  índice real e devolve respostas tipadas `Noul`, `Choice` e `Score`.
- Falta de credencial, cota estourada e timeout resultam em `blocked` com
  `human_review`, nunca em resposta sem verificação.
- O relatório comparativo cobre os três provedores nas mesmas perguntas, com
  acerto, calibração da confiança, latência e custo.
- O provedor de decisões padrão é escolhido a partir desse relatório, e o
  motivo fica registrado no README do harness e no curso.
- Nenhuma credencial chega ao repositório, aos logs ou à saída das avaliações.

## Dependências

- Conta e chave de API da TypeSafe.
- O registro de tokens e custos, para que a comparação use a mesma fonte de
  custo do uso diário.

## Referências

- [Feature atual do ADK + RAG + Jev](/pt-BR/tasks/adk-rag-jev-harness)
- [Referência do Jev](/pt-BR/reference/jev)
- [SDK Python da TypeSafe](https://github.com/typesafe-ai/typesafe-sdk-python)
