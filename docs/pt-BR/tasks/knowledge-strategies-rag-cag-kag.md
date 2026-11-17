---
title: Backlog — estratégias de conhecimento RAG, CAG e KAG
---

# Backlog — estratégias de conhecimento RAG, CAG e KAG

Status: **backlog** · Priority: **P1** · Escopo: ADK + RAG + Jev e os harnesses RAG

## Por que isso entra no backlog

O curso atual trata RAG como a principal estratégia para conhecimento externo.
A distinção do artigo é útil porque o conhecimento pode ter formatos diferentes:

- **RAG** busca em um corpus grande ou mutável e injeta as evidências
  selecionadas no momento da requisição.
- **CAG** carrega previamente um pacote de contexto estável e limitado e
  reutiliza o contexto processado. O KV cache é uma técnica de implementação,
  não uma garantia de que todo modelo ou runtime local exponha a mesma API.
- **KAG** raciocina sobre entidades, relações e regras conectadas, mantendo os
  vínculos com as fontes. O framework de pesquisa KAG combina grafo de
  conhecimento, recuperação e raciocínio guiado por forma lógica; ele é mais
  específico do que apenas adicionar um banco de grafos a um RAG.

A imagem fornecida foi registrada como evidência do backlog:

![Estratégias de conhecimento RAG, CAG e KAG](/images/rag-cag-kag.gif)

## Onde colocar

Não criar três harnesses independentes agora. Adicionar uma decisão tipada de
**estratégia de conhecimento** ao harness ADK + RAG + Jev, com estes modos:

| Modo | Melhor uso | Onde entra no curso | Decisão |
|---|---|---|---|
| `rag` | Conhecimento grande, mutável ou que precisa de busca seletiva | Harnesses RAG local e PostgreSQL existentes | Continua como baseline padrão. |
| `cag` | Pacotes estáveis e pequenos, como políticas, contratos de API ou playbooks | Primeiro como perfil de context pack no `adk-rag-harness` e nos harnesses de domínio | Medir antes de adicionar código específico de KV cache. |
| `kag` | Entidades conectadas, perguntas multi-hop, regras e raciocínio explicável | Futuro `adk-kag-harness`, aproveitando as fronteiras PostgreSQL e ADK | Criar apenas depois de escolher um caso real com conhecimento em grafo. |

O roteador deve decidir a partir de sinais mensuráveis: tamanho do corpus,
atualização, orçamento de contexto, densidade de relações, número de saltos da
pergunta, exigência de citações e orçamento de latência. O Jev pode classificar
a escolha delimitada; o código valida a decisão, aplica limites e preserva o
fallback determinístico.

## Evolução proposta

1. Definir um contrato independente de provedor para `KnowledgeStrategy`, com
   decisões `rag`, `cag` e `kag`.
2. Implementar primeiro `cag` como context pack versionado: manifesto, hashes
   das fontes, orçamento de tokens, proveniência e regras de invalidação. A
   primeira versão deve funcionar com Ollama e OpenRouter sem exigir APIs de KV
   cache.
3. Criar uma suíte que envie os mesmos prompts por RAG e CAG e meça qualidade,
   completude das citações, atualidade, latência, tokens e fallback.
4. Definir um piloto KAG com um grafo pequeno, arestas ligadas às fontes,
   perguntas multi-hop e caminho bloqueado para raciocínio sem suporte.
5. Criar um harness KAG separado somente se o piloto mostrar ganho material
   sobre o RAG híbrido.

## Critérios de aceite

- O roteador registra por que escolheu `rag`, `cag` ou `kag`.
- Cada modo retorna a proveniência das fontes ou informa explicitamente que ela
  não está disponível.
- O CAG invalida o context pack quando o manifesto das fontes muda.
- O KAG nunca trata uma aresta inferida como fato verificado sem vínculo com uma
  fonte.
- A avaliação compara os modos disponíveis usando os mesmos prompts dourados.
- Baixa confiança, contexto desatualizado, lacunas do grafo e falhas do
  provedor seguem um caminho seguro determinístico.

## Referências

- [Cache-Augmented Generation](https://arxiv.org/abs/2412.15605)
- [KAG: Boosting LLMs in Professional Domains via Knowledge Augmented Generation](https://arxiv.org/abs/2409.13731)
- [Feature atual ADK + RAG + Jev](/pt-BR/tasks/adk-rag-jev-harness)
