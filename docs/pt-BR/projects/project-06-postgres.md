---
title: Projeto 06B — ADK RAG com PostgreSQL
description: Harness de referência com PostgreSQL e pgvector para times maiores.
---

# Projeto 06B — ADK RAG com PostgreSQL

Esta é a variante do Projeto 06 para projetos maiores. Ela mantém a mesma
fronteira do workflow ADK + RAG e troca o índice local em JSON por PostgreSQL e
pgvector.

Use este projeto quando várias pessoas ou serviços compartilharem a base de
conhecimento, quando o repositório tiver muitas funções e registros de
arquitetura, ou quando a recuperação precisar de filtros por metadados e
persistência centralizada. O `adk-rag-harness` local continua sendo a
implementação recomendada para o curso e projetos pequenos.

## Baixar e executar

O projeto de referência está disponível no repositório em
[`adk-rag-postgres-harness`](https://github.com/saulostopa/harnesses/tree/main/adk-rag-postgres-harness).

```bash
git clone https://github.com/saulostopa/harnesses.git
cd adk-rag-postgres-harness
uv sync --extra postgres
docker compose up -d postgres
uv run python -m adk_rag_postgres_harness.cli migrate
```

Ingira uma coleção usando embeddings semânticos locais:

```bash
ollama pull nomic-embed-text
HARNESS_EMBED_PROVIDER=ollama HARNESS_EMBED_MODEL=nomic-embed-text \
PYTHONPATH=.:../rag-harness \
uv run python -m adk_rag_postgres_harness.cli ingest /caminho/para/seu-repositorio --collection docs
```

O banco armazena a fonte, os limites do chunk, os metadados e o embedding. A
consulta combina busca textual do PostgreSQL com similaridade cosine do
pgvector e retorna o mesmo contrato de evidência usado pelo harness local.

O banco não torna o workflow determinístico sozinho. O determinismo vem da
rota tipada, das coleções e estratégias permitidas, da ordenação estável, dos
thresholds e do estado `blocked` quando a evidência é insuficiente.

**Design**: [Harness ADK RAG com PostgreSQL](/pt-BR/harness-designs/adk-rag-postgres-harness)
