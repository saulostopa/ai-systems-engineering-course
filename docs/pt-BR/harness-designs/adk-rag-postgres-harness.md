---
title: Harness ADK RAG com PostgreSQL
---

# Harness ADK RAG com PostgreSQL

Este design é uma **memória de código**: um índice local de um repositório, das suas decisões
e dos seus logs de feature, usado com o Jev ou por um agente de código sozinho. Ele é feito com
peças open source e não precisa de API paga para buscar.

**Quick View: How it Works:** <a href="/demos/code-memory-postgres-jev.html" target="_blank" rel="noopener">abra o fluxo</a> de uma pergunta, com Jev e sem Jev.

```text
Arquivos do Git → chunks por sintaxe → embeddings no Ollama → PostgreSQL + pgvector
                                                                       │
             ┌─────────────────────────────────────────────────────────┤
             │                                                         │
   Com Jev: adk web                                 Sem Jev: MCP ou CLI
   o Jev escolhe coleção e estratégia               o agente decide o que buscar
   os gates podem bloquear para revisão humana      o agente escreve a resposta
   conversa e decisões são pagas                    nenhuma chamada ao OpenRouter
```

## O que ele guarda

| Dado | Origem | Se o banco for perdido |
|---|---|---|
| Chunks, símbolos e imports | Arquivos do Git, divididos por tree-sitter ou por linhas | O `index` reconstrói |
| Embeddings | `qwen3-embedding:4b`, por hash do conteúdo e modelo | O `index` calcula de novo |
| Memórias | `docs/harness/memories.jsonl`, com commit no repositório de destino | O `index` restaura |
| Perguntas registradas | Buscas pela CLI, pelo MCP e pelo `adk web` | Perdidas, então exporte antes |

## Os limites que importam

- **A busca não decide.** O PostgreSQL devolve evidência. A rota tipada, as coleções permitidas,
  os limites e o `blocked` continuam vindo do workflow.
- **O texto vem do disco.** O banco dá o caminho e as linhas, e `stale` marca um arquivo que mudou
  depois da indexação.
- **Alguns arquivos ficam de fora.** Links simbólicos, nomes como `.env*` ou `secret`, binários e
  arquivos muito grandes são pulados e listados.
- **As falhas aparecem.** Sem o banco ou o modelo, a busca termina em `blocked` com `human_review`.
  O `keyword` não precisa de modelo, então continua funcionando sem o Ollama.

## O que a avaliação mudou

Medimos 32 perguntas sobre um repositório, contando o arquivo certo no top 5. Os resultados
mudaram mais o design do que a escolha do modelo:

| Busca | Resultado |
|---|---|
| Híbrida em todas as coleções, o primeiro padrão | 56% |
| Por sentido em todas as coleções, o padrão atual | 91% |
| Híbrida na coleção certa | 94% |

- **O modelo não era o problema.** `qwen3-embedding:8b` e `voyage-code-4` não trouxeram ganho claro
  sobre o modelo local menor.
- **Misturar rankings pode piorar.** A parte por texto aceitava qualquer palavra e favorecia documentos
  longos, o que escondia o código.
- **Nomes precisam de um caminho direto.** O ranking encontra os muitos usos de um nome antes da sua
  única definição, então nomes em estilo de código agora trazem a definição primeiro.
- **O roteador precisa de contexto.** Sabendo que as perguntas são sobre o repositório, o Jev parou de
  responder de conhecimento geral e subiu de 20 para 26 de 32.
- **Uma ferramenta disponível pode não ser usada.** O Claude Code escolheu o MCP em 3 de 10 perguntas,
  e o agy em nenhuma. O Claude Code ainda respondeu bem com grep, então o ganho do MCP não está provado
  neste tamanho.

Esses números usam perguntas escritas depois de ler o código, e as correções foram escolhidas com elas,
então podem estar um pouco otimistas. A próxima avaliação usa perguntas reais registradas.

## Quando usar

Use quando você quiser decisões pesquisáveis, ou quando um repositório for grande o bastante para o
grep deixar de bastar. Em um projeto pequeno, o [harness RAG local](/pt-BR/harness-designs/rag-harness)
não precisa de Docker.

## Projeto de referência

Veja o [Projeto 06B](/pt-BR/projects/project-06-postgres) para os passos e o
[backlog](/pt-BR/tasks/code-memory-postgres) para o registro completo.
