---
title: Harness ADK RAG com PostgreSQL
---

# Harness ADK RAG com PostgreSQL

Esta é a variante com armazenamento compartilhado do design ADK + RAG + Jev.
Ela mantém o mesmo workflow tipado e o mesmo contrato de evidência, mas guarda
chunks, metadados e embeddings no PostgreSQL com pgvector.

```text
repositórios e docs → chunks AST/linhas → embeddings Ollama
                                      ↓
                         PostgreSQL + pgvector
                          ├─ busca textual
                          └─ similaridade vetorial
                                      ↓
                           ranking de evidência híbrida
                                      ↓
                         ADK + Jev → retrieved ou blocked
```

| Aspecto | ADK RAG local | ADK RAG PostgreSQL |
|---|---|---|
| Armazenamento | índice JSON ignorado | PostgreSQL + pgvector |
| Público | curso e projetos pequenos | projetos compartilhados por times |
| Atualizações | comando local de indexação | substituição centralizada da coleção |
| Filtros | configuração do adapter | metadados e filtros JSONB |
| Recuperação | controlador lexical/semântico | busca textual + ranking cosine |

O PostgreSQL fornece persistência compartilhada e recuperação eficiente; ele não
decide as transições do workflow. O determinismo continua vindo das decisões
tipadas, coleções e estratégias permitidas, ordenação estável, thresholds e do
estado `blocked`.

## Projeto de referência

A implementação está disponível em
[`adk-rag-postgres-harness`](https://github.com/saulostopa/harnesses/tree/main/adk-rag-postgres-harness).
Veja o [Projeto 06B](/pt-BR/projects/project-06-postgres) para Docker,
migrations, ingestão e comandos de embeddings locais com Ollama.

## Quando usar

Use este design quando vários usuários ou serviços compartilharem o índice,
quando o repositório tiver muitos chunks de código e arquitetura, ou quando a
recuperação precisar de filtros por metadados e atualizações centralizadas.
