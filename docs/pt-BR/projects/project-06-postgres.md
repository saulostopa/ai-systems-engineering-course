---
title: Projeto 06B — ADK RAG com PostgreSQL
description: Uma memória de código em PostgreSQL e pgvector, usada com o Jev ou por um agente de código sozinho.
---

# Projeto 06B — ADK RAG com PostgreSQL

Construa uma memória de código para um repositório real e depois meça o resultado. A busca roda
localmente, então só o caminho com Jev tem custo.

**Quick View: How it Works:** <a href="/demos/code-memory-postgres-jev.html" target="_blank" rel="noopener">abra o fluxo</a>.

## 1. Instalar e indexar

O projeto está em
[`adk-rag-postgres-harness`](https://github.com/saulostopa/ai-systems-engineering-harnesses/tree/feature/code-memory-postgres/adk-rag-postgres-harness),
na branch `feature/code-memory-postgres` até o merge.

```bash
git clone -b feature/code-memory-postgres https://github.com/saulostopa/ai-systems-engineering-harnesses.git
cd harnesses/adk-rag-postgres-harness
uv sync --extra postgres
docker compose up -d postgres
ollama pull qwen3-embedding:4b
uv run python -m adk_rag_postgres_harness.cli index /caminho/do/repo --project meu-repo
```

A primeira execução gera o embedding de cada trecho, o que levou cerca de 13 minutos para 1.300 trechos
em um M1 Max. Uma execução sem mudanças leva menos de um segundo.

## 2. Buscar e salvar decisões

```bash
uv run python -m adk_rag_postgres_harness.cli search "onde o login é tratado" --project meu-repo
uv run python -m adk_rag_postgres_harness.cli symbol useUser --project meu-repo
uv run python -m adk_rag_postgres_harness.cli uses useUser --project meu-repo
uv run python -m adk_rag_postgres_harness.cli remember "As novas tentativas ficam no cliente da API." \
  --project meu-repo --kind decision --source "PR 12"
uv run python -m adk_rag_postgres_harness.cli recall "onde ficam as novas tentativas" --project meu-repo
```

O `remember` grava em `docs/harness/memories.jsonl` no repositório de destino. Faça commit desse arquivo:
o Git é o backup, e o `index` o restaura em uma máquina nova.

## 3. Usar sem Jev

A partir do repositório de destino, entregue as ferramentas ao seu agente:

```bash
claude mcp add --scope local code-memory -- uv run --directory /caminho/do/adk-rag-postgres-harness \
  --extra postgres python -m adk_rag_postgres_harness.cli mcp --project meu-repo
```

O agy aceita o mesmo comando por `agy mcp add`, mas essa configuração vale para todos os repositórios.
O Claude Code e o agy foram testados, e o Codex não.

## 4. Usar com Jev

```bash
cd ../adk-rag-harness
uv sync --extra adk --extra openrouter --extra postgres
HARNESS_RAG_PROVIDER=postgres HARNESS_RAG_PROJECT=meu-repo uv run adk web
```

O Jev e o modelo de conversa são pagos pelo OpenRouter, enquanto a busca continua local. O Ollama
precisa estar rodando para `hybrid` e `semantic`.

## 5. Medir antes de ajustar

Escreva perguntas com o arquivo que deve responder a cada uma, como em
`evals/biometrik_questions.json`, e rode:

```bash
uv run --extra postgres python evals/run_retrieval.py --questions minhas_perguntas.json --out resultados.json
```

Nosso primeiro padrão encontrou o arquivo certo em só 56% das perguntas. Só vimos e corrigimos isso porque
medimos. Use `queries --json` para transformar perguntas registradas no próximo conjunto de avaliação:
perguntas escritas depois de ler o código favorecem a busca.

**Blueprint**: [Harness ADK RAG com PostgreSQL](/pt-BR/harness-designs/adk-rag-postgres-harness)
