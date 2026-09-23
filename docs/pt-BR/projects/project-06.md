---
title: Projeto 06 — harness ADK + RAG + Jev
---

# Projeto 06 — harness ADK + RAG + Jev

> Um workflow agêntico determinístico em que decisões tipadas escolhem políticas de recuperação e o código permanece no controle.

## Objetivo

Construir o `adk-rag-harness` como um projeto de composição. O Google ADK controla o grafo de workflow e o runtime, o subsistema RAG controla a recuperação de evidências e o Jev avalia decisões delimitadas antes do roteamento pelo código.

O `rag-harness` existente continua utilizável sem ADK ou Jev. Este projeto adiciona uma fronteira de adapter sem mover os internals de RAG para a camada de orquestração.

## Primeiro recorte

Implementar e avaliar:

1. se a recuperação é necessária;
2. qual coleção ou estratégia de busca usar;
3. se as evidências são suficientes para responder.

Usar as decisões tipadas Noul, Choice e Score do Jev. Aplicar limiares no código e manter caminhos determinísticos para baixa confiança, falhas do provedor e evidências contraditórias.

## Critérios de conclusão

- A interface do provedor funciona em testes sem rede.
- As decisões registram pergunta, resposta, confiança, limiar e rota escolhida.
- Cada resultado de recuperação mantém referências às fontes.
- Baixa confiança e erros do provedor seguem um caminho seguro testado.
- A avaliação informa precisão do roteamento, qualidade da recuperação, citações, latência, custo e fallback.

## Implementação atual

A fatia local está em `adk-rag-harness/` e inclui o entrypoint do Dev UI do
ADK. Instale com `uv sync --extra adk --extra ollama --extra jev-sdk` e inicie
com `uv run adk web`. O modelo de conversa padrão é `llama3.1:8b`; o provider
de decisão tipada é o `ollama-system-one` local usando `qwen2.5:14b`.
Defina `HARNESS_RAG_PROVIDER=rag-harness` depois de criar o índice local do
curso para trocar a evidência de demonstração por fontes reais do repositório.
A [aula do Dev UI com Ollama](/pt-BR/lectures/lecture-18) traz a sequência
completa de prompts, screenshots e checklist de evidências.

Execute a suíte offline completa com `python3 -m unittest discover -s tests -v`
a partir desse diretório. Ela inclui as evals de contrato dos prompts dourados e
não exige chave de API em nuvem.

Veja o [registro da feature](/pt-BR/tasks/adk-rag-jev-harness) para as decisões e guardrails adotados.

**Designs**: [ADK + RAG + Jev](/pt-BR/harness-designs/adk-rag-jev-harness) ·
[ADK RAG PostgreSQL](/pt-BR/harness-designs/adk-rag-postgres-harness) ·
[Projeto 06B](/pt-BR/projects/project-06-postgres)
