---
title: Backlog — memória de código no Postgres
---

# Backlog — memória de código no Postgres

Status: **in progress** · Priority: **P1** · Escopo: `adk-rag-postgres-harness`, com e sem Jev

## Por que isso entra no backlog

Agentes de código perdem entre sessões o que aprenderam sobre um repositório, e
o grep só encontra o que o agente já sabe nomear. A Cursor resolve isso com um
índice de código que o agente consulta pelo significado. Segundo a documentação
pública dela, esse índice respeita os arquivos de ignore, quebra o código pela
sintaxe, sincroniza de forma incremental com uma árvore de hashes dos arquivos,
devolve caminho e linhas para o cliente ler localmente e oferece a busca
semântica como uma ferramenta do agente, ao lado do grep.

Os harnesses já têm partes disso. O `rag-harness` descobre arquivos pelo Git e
pelo `.ragignore`, guarda embeddings em cache por hash e tem um controlador
agêntico, mas mantém o índice em arquivos JSON e só quebra Python pela sintaxe.
O [`adk-rag-postgres-harness`](/pt-BR/harness-designs/adk-rag-postgres-harness)
tem Docker e pgvector, mas é um esboço:

- Substitui a coleção inteira a cada indexação.
- A busca pontua todas as linhas e mistura uma nota de texto sem normalização
  com a distância de cosseno, então nunca usa o índice HNSW.
- Fixa o vetor em 768 dimensões e gera um embedding por vez, sem cache.
- Ignora o `.ragignore` e a lista de arquivos do Git.
- O `adk web` não consegue selecioná-lo: o `HARNESS_RAG_PROVIDER` só aceita
  `demo` e `index`.
- Não tem símbolos nem memória, e só dois testes.

## Objetivo

Transformar o `adk-rag-postgres-harness` em uma memória de código sobre Postgres
e Docker, feita com peças open source, com um núcleo e duas portas de entrada:

- **Sem Jev:** um servidor MCP e um CLI, para que o Claude Code, o Codex e o agy
  usem a memória pela assinatura e decidam sozinhos o que buscar.
- **Com Jev:** `HARNESS_RAG_PROVIDER=postgres` no `adk web`, com o Jev escolhendo
  coleção e estratégia e os gates de confiança ainda valendo.

## Decisões

Tomadas com o dono do curso em 2026-10-30.

| Tema | Decisão | Motivo |
|---|---|---|
| Local | Evoluir o `adk-rag-postgres-harness` | Sem pacote novo; o ADK vira extra opcional, e o caminho sem Jev não precisa instalá-lo |
| Entrada sem Jev | Servidor MCP + CLI | O CLI é necessário para indexar de qualquer forma; o MCP deixa as ferramentas visíveis para o agente, ao lado do grep |
| Embeddings | Open source, começando com `qwen3-embedding:4b` no Ollama | Sem custo de API; a nota é próxima da do `8b`, com cerca de metade do tamanho |
| Chunks de TS, TSX e JS | tree-sitter | O Biometrik é React Native; chunks por linha cortam componentes e funções |
| Escopo da memória | Código + decisões e handoffs | Decisões e convenções são o que os agentes perdem entre sessões |
| Resultado da busca | Caminho e linhas, relidos do disco | O agente nunca recebe código desatualizado |

## Evolução proposta

1. **Núcleo no Postgres.** Tabelas `projects`, `files` (caminho, hash, linguagem),
   `chunks` (linhas, hash do conteúdo, `tsvector` gerado), `embeddings` (hash do
   conteúdo, modelo, vetor), `symbols`, `edges`, `memories` e `queries`. Sincronizar
   por hash de arquivo e gerar embeddings só do que mudou, em lotes. Buscar com
   RRF (reciprocal rank fusion) sobre os 50 primeiros do HNSW e os 50 primeiros do
   texto completo.
2. **Chunks pela estrutura do código.** tree-sitter para TS, TSX e JS, o chunker
   por AST que já existe para Python e extração de símbolos e imports, para
   responder "onde X é usado".
3. **Memória.** Guardar decisões, convenções e handoffs com a fonte, e marcar uma
   memória como substituída quando outra mais nova tomar o lugar dela. Importar os
   arquivos `progress` e `handoff` das features.
4. **Entrada sem Jev.** Comandos de CLI para indexar e buscar, e um servidor MCP
   com `search_code`, `find_symbol`, `read_lines`, `remember` e `recall`, sobre as
   mesmas funções. Registrar o servidor para o Biometrik.
5. **Entrada com Jev.** Ligar o adaptador existente ao app do ADK com
   `HARNESS_RAG_PROVIDER=postgres`.
6. **Avaliação.** Perguntas-padrão do Biometrik comparam `qwen3-embedding:4b`,
   `qwen3-embedding:8b` e `voyageai/voyage-code-4`, o índice JSON contra o Postgres
   e o Jev contra o agente decidindo sozinho. Registrar hit@k, MRR, latência e
   custo, e fixar o modelo padrão a partir dessa evidência.
7. **Curso.** Atualizar o design do harness e as aulas relacionadas, em inglês e
   em português do Brasil.

## Andamento

**A fase 1 está pronta** (2026-10-30, branch `feature/code-memory-postgres` do
repositório de harnesses). Medido no Biometrik, com 505 arquivos e 728 chunks
únicos, em um M1 Max com `qwen3-embedding:4b`:

- A primeira indexação levou 26 minutos, e uma execução sem mudanças levou 0,7 s.
- Uma busca levou cerca de 0,6 s pelo CLI, incluindo o embedding da pergunta.
- O PostgreSQL escolheu uma varredura exata nesse tamanho, o que é correto para
  tão poucas linhas. Em um teste sintético com 20.000 linhas ele escolheu o índice
  HNSW, e a parte da busca no banco levou 0,07 s.
- Uma busca sem `--collection` fica cheia de documentos do harness, e os chunks por
  linha ainda cortam componentes. A fase 2 e a avaliação tratam disso.

## Modelo de embeddings

Vetores de modelos diferentes ficam em espaços diferentes, então não podem ser
convertidos: trocar de modelo significa gerar os embeddings do texto de novo.
Como a tabela `embeddings` usa o hash do conteúdo e o modelo como chave, vetores
de vários modelos podem coexistir, e voltar a um modelo já usado não recalcula
nada. Os índices JSON do Biometrik usam Voyage e precisam ser gerados de novo, não
importados.

As tags do `qwen3-embedding` podem gerar mais dimensões que as 2.000 aceitas por
um índice HNSW no tipo `vector` do pgvector. O plano corta os vetores para 1.024
dimensões e os normaliza de novo.

Os autores informam nDCG@10 de 80,06 para o modelo 4B e de 80,68 para o 8B no MTEB
Code. O resultado é deles mesmos, então o passo 6 decide com perguntas reais.

Ainda falta confirmar quando o trabalho começar:

- Como as dimensões do `voyage-code-4` se encaixam na coluna de vetor compartilhada.
- Se o `nomic-embed-code` está disponível no Ollama, como mais um candidato.

## Critérios de aceite

- `docker compose up` e um comando do CLI indexam um repositório real, e uma
  segunda execução só gera embeddings dos arquivos que mudaram.
- A busca consegue usar o índice HNSW, confirmado com `EXPLAIN` em uma tabela grande
  o bastante para o planejador preferi-lo, e devolve caminho e linhas com o conteúdo
  relido do disco.
- Arquivos TS e TSX são quebrados pela sintaxe, e o `find_symbol` encontra
  componentes e funções do Biometrik.
- As memórias registram a fonte, e uma memória substituída não volta como atual.
- O Claude Code usa as ferramentas MCP no Biometrik sem nenhuma chamada paga de API
  além de um modelo de embeddings escolhido explicitamente.
- O `adk web` roda com `HARNESS_RAG_PROVIDER=postgres`; falhas na busca terminam em
  `blocked` com `human_review`.
- O caminho sem Jev instala e roda sem o Google ADK.
- O relatório de avaliação fixa o modelo de embeddings padrão, e o motivo fica
  registrado no README do harness e no curso.
- Nenhuma credencial ou valor de `.env` chega ao banco, aos logs ou à saída das
  avaliações.

## Dependências

- Docker e Ollama na máquina de desenvolvimento.
- O registro de tokens e custos, para que a comparação use a mesma fonte de custo
  do uso diário.

## Referências

- [Design do harness com Postgres](/pt-BR/harness-designs/adk-rag-postgres-harness)
- [Design do harness de RAG](/pt-BR/harness-designs/rag-harness)
- [Feature atual do ADK + RAG + Jev](/pt-BR/tasks/adk-rag-jev-harness)
- [Registro de tokens e custos](/pt-BR/tasks/token-cost-ledger)
- [Qwen3 Embedding no Ollama](https://ollama.com/library/qwen3-embedding)
- [Artigo do Qwen3 Embedding](https://arxiv.org/abs/2506.05176)
