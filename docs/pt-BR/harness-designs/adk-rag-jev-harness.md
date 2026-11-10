---
title: Harness ADK + RAG + Jev
---

# Harness ADK + RAG + Jev

Este design combina o Google ADK para o runtime, um adapter RAG para evidências e
o Jev para decisões tipadas delimitadas com base no princípio: **"O LLM escreve, o Jev decide"**.
O modelo generativo propõe respostas e ações; o Jev avalia decisões através dos
quatro pilares operacionais (**Rotear, Filtrar, Pontuar e Liberar**), e o código de política do harness
mantém a autoridade total sobre rotas, limiares de confiança e caminhos de fallback.

```text
pedido do usuário
  │
  ▼
[ Jev Guardrail (Filtrar) ] ── (abusivo / injeção) ──► bloqueado
  │ (limpo)
  ▼
[ Jev Roteador de Modelos (Rotear) ]
  ├─ pedido simples ──────► LLM Pequeno ($) ────────► Resposta Direta
  └─ complexo / busca ────► Workflow ADK
                              │
                              ├─ [ Jev Filtro de Tool Call (Filtrar) ] ──► permite / pergunta / nega
                              ├─ Adapter RAG ──► [ Jev Reranker (Pontuar) ] ──► top-K evidências
                              │
                              ▼
                       LLM Grande ($$$) (Síntese)
                              │
                              ▼
                       [ Jev Eval de Resposta (Pontuar) ]
                              │
                              ▼
                       [ Portão Tripartite (Liberar) ]
                         ├─ alta confiança (≥ 0.85) ──► executa / responde
                         ├─ média confiança ──────────► confirma com usuário
                         └─ baixa confiança (< 0.50) ─► escalona humano (HITL)
```

## Os 4 Pilares Operacionais neste Harness

| Pilar | Responsabilidade do Jev | Autoridade do Harness |
|---|---|---|
| **Rotear** | Avalia a complexidade do prompt; seleciona LLM Pequeno vs. Grande | Preserva tokens e impõe orçamentos de custo e latência |
| **Filtrar** | Guardrail pré-LLM (barra injeções); Autorização de Tool Calls (`permite`, `pergunta`, `nega`) | Previne ataques de prompt e blinda ações destrutivas de ferramentas |
| **Pontuar** | Reranker de trechos RAG; pontuação de fundamentação da resposta da LLM | Minimiza a janela de contexto e previne alucinações |
| **Liberar** | Emite scores de confiança para o portão tripartite | O código executa, pede confirmação ao usuário ou bloqueia |

A camada RAG nunca escolhe o próximo nó do workflow. Ela retorna fonte, texto,
score e metadados de linha. O workflow bloqueia quando o provider falha ou a
evidência é insuficiente, impedindo uma resposta sem suporte.

## Camadas da Arquitetura

| Camada | Responsabilidade | Autoridade |
|---|---|---|
| ADK | sessão, chamada de ferramentas e traces do Dev UI | ciclo de vida do runtime |
| Jev | respostas tipadas `noul`, `choice` e `score` nos 4 pilares | saída de decisão delimitada |
| Workflow e Políticas | rota, limiares tripartites, fallbacks e estado bloqueado | fluxo de controle final |
| Adapter RAG | consulta a coleção, ranqueia trechos e devolve fontes | somente evidências |
| LLMs Estratificadas | geração e síntese calibradas por tier de modelo | somente geração textual |

## Projeto de referência

A implementação está disponível em
[`adk-rag-harness`](https://github.com/saulostopa/ai-systems-engineering-harnesses/tree/main/adk-rag-harness).
O [projeto ADK + RAG + Jev](/pt-BR/projects/project-06) explica instalação,
providers, prompts e avaliações.

Os princípios fundamentais de design estão documentados na [referência de decisão operacional Jev](/pt-BR/reference/jev).
O diagrama de arquitetura está disponível em
[`adk-harness-architecture.html`](https://github.com/saulostopa/ai-systems-engineering-course/blob/main/docs/architecture/adk-harness-architecture.html).

## Quando usar

Use este design quando a recuperação precisar de roteamento explícito e
evidências revisáveis, especialmente em assistentes de repositório, perguntas
de arquitetura, gestão de custos multi-modelo e fluxos críticos nos quais
uma resposta sem suporte ou ação não autorizada deve interromper a execução.
