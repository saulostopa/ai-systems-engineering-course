---
title: Backlog — memória de código no Postgres
---

# Backlog — memória de código no Postgres

Status: **in progress** · Priority: **P1** · Escopo: `adk-rag-postgres-harness`, com e sem Jev

**Quick View: How it Works:** <a href="/demos/code-memory-postgres-jev.html" target="_blank" rel="noopener">abra o fluxo</a> de uma pergunta, com Jev e sem Jev.

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
   arquivos `progress` e `handoff` das features. Cada `remember` também grava em um
   arquivo de texto no repositório, como `docs/harness/memories.jsonl`, sem vetores,
   e recusa conteúdo que pareça credencial. O Git é o backup, e o `index` restaura
   as memórias desse arquivo em uma máquina nova.
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
8. **Outros agentes (último corte).** Testar o servidor MCP com o Codex no Biometrik, quando
   chegar o momento. O Claude Code e o agy já foram testados.

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

**A fase 2 está pronta** (mesma branch). O tree-sitter dividiu os 385 arquivos TS e
JS do Biometrik em definições de até 80 linhas, com 1.467 chunks únicos no
repositório:

- O novo índice reaproveitou 201 vetores e gerou 1.266 chunks em 13 minutos.
- `uses useUser` devolveu os 20 arquivos que o grep encontra além da definição.
- Todos os 1.324 imports de módulos locais foram resolvidos, inclusive os aliases do
  `tsconfig.json`.
- Buscas só em código agora apontam para componentes inteiros, como `Login` e
  `UserProvider`. Sem `--collection`, os documentos do harness ainda vêm primeiro, e
  a avaliação do passo 6 precisa medir e corrigir isso.

**A fase 3 está pronta** (mesma branch). O `remember` grava no arquivo versionado e
no banco, e o `recall` busca nas memórias e nos registros das features:

- Uma execução real com `qwen3-embedding:4b` em um repositório temporário restaurou
  as duas memórias depois de apagar o banco, e a decisão substituída continuou oculta.
- O `recall` lê os arquivos de progresso e handoff pelos chunks já indexados, sem
  importar uma segunda cópia, então eles nunca ficam desatualizados.
- A checagem de credenciais usa padrões, então reduz o risco, mas não substitui
  revisar o arquivo no diff.
- No Biometrik, os registros ainda usam chunks de 100 linhas, e o progresso da feature
  de remoção veio em quarto para "por que removemos o Supabase". A avaliação do passo
  6 precisa medir isso.

**A fase 4 está pronta** (mesma branch). O servidor MCP expõe as cinco ferramentas
sobre as mesmas funções da CLI e está registrado para o Biometrik no escopo privado
`local` do Claude Code, então o repositório do Biometrik não mudou:

- Por padrão, o Claude Code escondeu as ferramentas atrás da sua busca de ferramentas, e
  o agente respondeu só com grep e Read. Com `anthropic/alwaysLoad`, a mesma pergunta
  usou `search_code`, `recall`, `find_symbol` e `read_lines`.
- Essa execução não é uma comparação. O agente tentou o grep primeiro e passou às
  ferramentas MCP depois que o grep ficou aguardando aprovação, então a etapa 6 precisa
  medir com que frequência ele as escolhe.
- Em stdio real, uma busca levou 0,2 s com o modelo já carregado e 5,9 s na primeira
  chamada. Sem Ollama, `search_code` falha com um erro claro e `remember` continua salvando.
- O servidor não reindexa, então arquivos novos ficam fora dos resultados até o próximo
  `index`, e ele lê a pasta indexada, não o worktree do agente.

**O teste independente da fase 4 gerou um lote de correções** (mesma branch). Um testador
sem contexto encontrou quatro bugs graves, todos reproduzidos e agora cobertos por testes:

- Um único arquivo grande parava todo o `index`. Agora arquivos problemáticos são listados
  e pulados, sem efeito sobre os 505 arquivos do Biometrik.
- Um separador de linha como U+2028 deixava o arquivo de memórias ilegível, e formatos
  comuns como `DB_PASSWORD=` passavam pela checagem de credenciais.
- Links simbólicos chegavam ao banco e passavam pelo `read_lines`. Agora não são indexados
  nem lidos.
- O `index` também recusa uma pasta inexistente ou inesperada, decisões substituídas não
  voltam mais, e o `uses` encontra pacotes com escopo.
- Passaram para a etapa 6: documentos dominando buscas sem `--collection`, handlers dentro
  de componentes, `recall` sem Ollama e candidatos do HNSW em um banco compartilhado.

**A fase 5 está pronta** (mesma branch). `HARNESS_RAG_PROVIDER=postgres` com
`HARNESS_RAG_PROJECT` seleciona o índice no `adk web`:

- O adapter ignorava a estratégia escolhida pelo Jev, então agora `semantic` e `keyword`
  mudam de fato a busca. As memórias viraram uma terceira coleção, ao lado de `code` e `docs`.
- No Biometrik, o Jev real escolheu `code` para a pergunta do login e `memory` para a do
  Supabase, e citou os arquivos certos. Três perguntas custaram US$ 0,035, tudo do Jev e
  do modelo de conversa.
- Com o PostgreSQL fora do ar, o `adk web` terminou em `blocked` com `human_review`. Com o
  Ollama fora do ar, o workflow fez o mesmo no `hybrid`, enquanto o `keyword` ainda respondeu.
- Para "onde fica o hook useUser", o Jev escolheu `keyword` e a evidência trouxe só os
  usos, então o agente disse que não encontrou a definição. Este caminho não tem
  `find_symbol`, e a etapa 6 precisa medir isso.
- Os modelos locais roteiam pior: `qwen2.5:14b` respondeu à pergunta do login sem buscar,
  e `llama3.1:8b` inventou uma resposta. A etapa 6 os compara com o Jev.

**A fase 6 mediu a busca e os agentes; as correções aguardam decisão** (mesma branch,
`evals/`). Em 32 perguntas do Biometrik com resposta, contando o arquivo certo no top 5:

| Busca | `4b` | `8b` | `voyage-code-4` | Índice JSON |
|---|---|---|---|---|
| Coleção certa, híbrida | 94% | 84% | 81% | 72% |
| Coleção certa, semântica | 91% | 94% | 78% | 84% |
| Sem coleção, híbrida (padrão do MCP) | 56% | 62% | 69% | não se aplica |
| Sem coleção, semântica | 91% | 84% | 62% | não se aplica |

- O `qwen3-embedding:4b` continua como padrão. O `8b` levou 38 minutos para indexar e usa
  9,3 GB, sem ganho claro. A rodada do Voyage não informa o tipo de texto (consulta ou
  documento), então ele pode ter sido subestimado.
- A busca padrão é o principal problema: a parte por texto aceita qualquer palavra e favorece
  documentos longos. Em um teste só de leitura, a busca semântica com nomes exatos primeiro
  manteve 91% e colocou em 1º as seis perguntas sobre nomes.
- O Jev real encontrou o arquivo certo em 20 de 32, a US$ 0,10 por 34 perguntas. Ele não buscou
  em quatro perguntas, e três delas receberam respostas genéricas, sem relação com o repositório.
- O Claude Code usou as ferramentas MCP em 3 de 10 perguntas e citou o arquivo esperado em 8.
  Ele também percebeu que o handoff de `home-streak-progress` estava desatualizado. Em um
  repositório deste tamanho, grep e Read ainda bastam, então o ganho do MCP não está provado.
- Com 32 perguntas escritas depois de ler o código, diferenças pequenas podem ser acaso.

**As correções da fase 6 estão aplicadas** (mesma branch). A busca sem coleção agora vai por
sentido, nomes em estilo de código trazem primeiro a definição, e a triagem diz que as perguntas
são sobre o repositório:

- A busca padrão subiu de 56% para 91% no top 5. Com a coleção certa, a híbrida ficou em 94%, e
  o arquivo certo em 1º lugar subiu de 56% para 66%.
- O Jev real subiu de 20 para 26 de 32, e de 3 para 6 de 6 em nomes. Ele buscou em todas as
  perguntas e continuou admitindo quando o repositório não tinha resposta.
- As regras continuam sendo o ponto fraco, com 2 de 5, porque ele envia algumas para `memory` ou `code`.
- Os números usam as mesmas perguntas que orientaram as correções, então podem estar um pouco otimistas.

**O sistema está pronto para um período de uso real** (mesma branch, e
`feature/jev-adk-rag-harness` no Biometrik). O `npm run assistente` agora usa esta memória por
padrão, com `ASSISTENTE_RAG=json` para voltar. O índice se atualiza depois de cada commit, merge e
troca de branch, e as buscas ficam registradas localmente. Novos ajustes esperam de 2 a 4 semanas
de perguntas reais, que também viram o próximo conjunto de avaliação. Antes de indexar um segundo
projeto grande, é preciso revisar os candidatos do HNSW em um banco compartilhado.

**A fase 7 está pronta, e o agy foi testado** (mesma branch). O design do harness e o Projeto 06B agora
descrevem a memória de código e o que a avaliação ensinou, nos dois idiomas.

- O agy alcançou as ferramentas e respondeu certo quando a pergunta citou `find_symbol`.
- Nas mesmas 10 perguntas do Claude Code, sem citar ferramenta, ele não escolheu o MCP em nenhuma. Deu
  6 respostas, citando o arquivo esperado em 5, e 4 respostas vieram vazias porque o agy sem interação
  negou comandos do shell. Isso é um limite deste teste, não das respostas.
- O agy não tem configuração por repositório, então um servidor fixo em um projeto responderia em todos.
  O registro foi removido depois do teste.
- O Codex foi adiado.

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
- Depois de apagar o banco, o `index` restaura todas as memórias do arquivo
  versionado, e chunks e embeddings são recriados a partir do repositório.
- O Claude Code usa as ferramentas MCP no Biometrik sem nenhuma chamada paga de API
  além de um modelo de embeddings escolhido explicitamente.
- O `adk web` roda com `HARNESS_RAG_PROVIDER=postgres`; falhas na busca terminam em
  `blocked` com `human_review`.
- O caminho sem Jev instala e roda sem o Google ADK.
- O agy consegue usar as ferramentas MCP no Biometrik.
- O Codex usa as ferramentas MCP no Biometrik (adiado).
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
