---
title: Harness ADK + RAG + Jev
---

# Harness ADK + RAG + Jev

Este design combina o Google ADK para o runtime, um adapter RAG para
evidências e o Jev para decisões tipadas delimitadas. O modelo propõe respostas
estruturadas; o workflow valida essas respostas e o código mantém a autoridade
sobre rotas, thresholds e falhas.

```text
pedido → agente ADK → ferramenta run_workflow → decisão Jev
                                      ├─ direct → resposta
                                      ├─ clarify → pedir novamente
                                      └─ retrieve → adapter RAG → evidência
                                                        ├─ retrieved
                                                        └─ blocked
```

| Camada | Responsabilidade | Autoridade |
|---|---|---|
| ADK | sessão, chamada da ferramenta e traces do Dev UI | ciclo de vida do runtime |
| Jev | respostas tipadas `noul`, `choice` e `score` | saída de decisão delimitada |
| Workflow | rota, thresholds, fallbacks e estado blocked | fluxo de controle final |
| Adapter RAG | consulta a coleção e devolve fontes | somente evidências |

A camada RAG nunca escolhe o próximo nó do workflow. Ela retorna fonte, texto,
score e metadados de linha. O workflow bloqueia quando o provider falha ou a
evidência é insuficiente, impedindo uma resposta sem suporte.

## Projeto de referência

A implementação está disponível em
[`adk-rag-harness`](https://github.com/svslwm/harness-plannig/tree/develop/adk-rag-harness).
O [projeto ADK + RAG + Jev](/pt-BR/projects/project-06) explica instalação,
providers, prompts e avaliações.

O diagrama de arquitetura está disponível em
[`adk-harness-architecture.html`](https://github.com/svslwm/harness-plannig/blob/develop/docs/architecture/adk-harness-architecture.html).

## Quando usar

Use este design quando a recuperação precisar de roteamento explícito e
evidências revisáveis, especialmente em assistentes de repositório e perguntas
de arquitetura nas quais uma resposta sem suporte deve interromper a execução.
