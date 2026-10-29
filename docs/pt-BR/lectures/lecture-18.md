---
title: Aula 18 — Executando o harness ADK com Ollama
---

# Aula 18 — Executando o harness ADK com Ollama

> Um laboratório prático do `adk-rag-harness`: executar o Dev UI do ADK contra
> um modelo local do Ollama, usar pedidos em linguagem natural e inspecionar as
> evidências que provam que o workflow rodou.

## O que esta aula ensina

O Dev UI é um cliente do harness. Ele serve para enviar pedidos, iniciar
sessões e inspecionar eventos. Ele não substitui o workflow determinístico. O
modelo propõe quando chamar uma ferramenta; `run_workflow` continua aplicando
em código a decisão tipada, a política de recuperação e os fallbacks.

A configuração local padrão exercita duas rotas com os prompts da aula:

- pedidos diretos, que respondem sem recuperação;
- pedidos recuperados, que retornam a evidência local de demonstração e a
  referência da fonte.

O app usa por padrão o OpenRouter com o Jev (`typesafe/jev-router`) tanto na
conversa quanto nas decisões tipadas. Esta aula roda tudo localmente, então
define `HARNESS_CHAT_PROVIDER=ollama` e
`HARNESS_DECISION_PROVIDER=ollama-system-one`. O modelo de conversa é o
`llama3.1:8b`. As decisões tipadas usam `qwen2.5:14b`, pois ele foi mais
consistente que o `llama3.1:8b` nas evals de roteamento. O `demo` continua
disponível como provider determinístico explícito.

O provedor Jev oficial da TypeSafe é habilitado separadamente com `HARNESS_DECISION_PROVIDER=jev` e uma
`TYPESAFE_API_KEY`. Essa separação mantém os experimentos locais seguros e
repetíveis.

## Pré-requisitos

- Python 3.10 ou mais recente;
- [`uv`](https://docs.astral.sh/uv/);
- [Ollama](https://ollama.com/) rodando localmente;
- o [projeto standalone `adk-rag-harness`](https://github.com/saulostopa/harnesses/tree/main/adk-rag-harness) disponível.

Confira se o modelo está instalado:

```sh
ollama list
```

Se estiver faltando, instale uma vez:

```sh
ollama pull llama3.1:8b
```

O Ollama Desktop pode já estar servindo a API. Se não estiver, inicie o
servidor local em outro terminal:

```sh
ollama serve
```

A API padrão é `http://localhost:11434`. Uma verificação rápida é:

```sh
curl -fsS http://127.0.0.1:11434/api/tags
```

## Instale e inicie o harness

Use `uv` tanto para instalar quanto para executar. Assim o comando `adk` fica
no ambiente do projeto, sem depender de uma instalação global de `pip` ou `adk`.

```sh
git clone https://github.com/saulostopa/harnesses.git
cd adk-rag-harness
uv sync --extra adk --extra ollama --extra jev-sdk
HARNESS_CHAT_PROVIDER=ollama HARNESS_DECISION_PROVIDER=ollama-system-one \
OLLAMA_MODEL=llama3.1:8b uv run adk web
```

Abra [http://127.0.0.1:8000/dev-ui/?app=adk_app](http://127.0.0.1:8000/dev-ui/?app=adk_app)
e selecione `adk_app`. Mantenha o terminal rodando enquanto usa a UI. Reinicie
`adk web` depois de mudar o código Python ou variáveis de ambiente.

A integração usa o provedor `ollama_chat` do LiteLLM. O modelo precisa saber
chamar ferramentas; `llama3.1:8b` é o padrão do curso porque completou o caminho
de tool call neste laboratório. Se o modelo responder apenas texto sem chamar
`run_workflow`, o harness não foi exercitado.

## Prompts em linguagem natural para a demonstração

Cole um prompt por vez na caixa de mensagem. Nenhuma sintaxe de comando
especial é necessária.

| Prompt | O que demonstra | Rota esperada |
|---|---|---|
| `Escreva uma saudação curta para um participante do curso.` | Um pedido que não precisa de evidência do repositório | Direta |
| `Encontre a política de deploy na documentação do curso e resuma as evidências.` | Um pedido que precisa de recuperação e referência de fonte | Recuperada |
| `Procure no repositório a regra que controla quando um pedido precisa de evidência externa.` | Linguagem de recuperação sem citar o nome de uma função | Recuperada |
| `Preciso de uma resposta sobre a arquitetura do projeto. Qual coleção deve ser pesquisada e por quê?` | Pedir uma política de recuperação em linguagem natural | Recuperada |
| `Responda somente quando a evidência do repositório for suficiente; caso contrário, explique o que está faltando.` | O contrato desejado para uma resposta protegida | Guardada |

Os dois primeiros prompts são o smoke test confiável da demonstração atual. O
O último descreve o contrato de baixa confiança; seu comportamento completo é
coberto pelos testes de política de decisão e se torna efetivo quando os
provedores reais do Jev e do RAG forem habilitados.

Os mesmos prompts estão armazenados em `adk-rag-harness/evals/golden_prompts.json`.
Execute as evals offline do contrato com:

```sh
python3 -m unittest discover -s tests -v
```

As evals comparam rota, quantidade de chamadas ao RAG, coleção, estratégia,
fonte da evidência e comportamento de bloqueio/solicitação de esclarecimento.
Elas não comparam o texto gerado, evitando falhas falsas por uma pequena mudança
de redação.

### Trocando o provedor de decisões

O modelo de conversa e o provedor de roteamento tipado são separados. O app lê
`HARNESS_DECISION_PROVIDER` em `adk_app/agent.py`:

```sh
# Padrão: OpenRouter com Jev na conversa e nas decisões
uv run adk web

# Provider demo determinístico
HARNESS_DECISION_PROVIDER=demo uv run adk web

# Decisões tipadas locais com Ollama
HARNESS_DECISION_PROVIDER=ollama-system-one \
OLLAMA_DECISION_MODEL=qwen2.5:14b uv run adk web

# Decisões no OpenRouter com outro modelo hospedado
OPENROUTER_DECISION_MODEL=deepseek/deepseek-v4-flash-0731 uv run adk web
```

Os dois modos compatíveis com OpenAI preservam o contrato tipado, mas não são o
modelo Jev. Avalie os valores de confiança antes de usá-los como limite de
política em produção. Os CLIs instalados `codex`, `claude` e `agy` podem ser
envolvidos depois por adapters de subprocesso somente leitura e saída estrita
com JSON Schema; suas ferramentas interativas e estado de sessão não devem
rodar dentro desse caminho de decisão.

Se `OPENROUTER_API_KEY` não estiver definido, o app pode ler localmente
`openrouter.key` em `~/.local/share/opencode/auth.json` sem copiar a credencial
para o projeto.

### Trocando a evidência demo pelo índice RAG real

O provider de recuperação é independente do provider de decisões. Crie uma vez
o índice dos documentos do curso:

```sh
ollama pull nomic-embed-text
RAG_EMBEDDER=ollama OLLAMA_EMBED_MODEL=nomic-embed-text \
PYTHONPATH=rag-harness python3 -m rag_harness index docs --verbose
```

Depois inicie o app com:

```sh
HARNESS_RAG_PROVIDER=rag-harness uv run adk web
```

O índice é local e ignorado pelo Git. Um índice ausente ou falha de recuperação
produz `blocked`, evitando que o assistente apresente evidências inventadas.
O modelo `nomic-embed-text` fornece embeddings semânticos pela API local do
Ollama. Para validar a arquitetura totalmente offline, use
`RAG_EMBEDDER=ngram`; recrie o índice ao trocar o provider de embeddings.

Em um repositório de aplicação, crie um índice por coleção com
`--profile docs` (Markdown, JSON, YAML) e `--profile code` (Python, shell,
TypeScript, JavaScript), e aponte `HARNESS_RAG_DOCS_INDEX` e
`HARNESS_RAG_CODE_INDEX` para `.rag_index/docs` e `.rag_index/code`. Só as
coleções com índice são oferecidas ao provider de decisões. Dentro de um
repositório Git, o indexador lê apenas os arquivos versionados, sempre ignora
lockfiles e respeita um `.ragignore` na raiz. `RAG_EMBEDDER=openrouter` troca o
Ollama por um modelo de embeddings hospedado (padrão `voyageai/voyage-code-4`);
cada índice registra o seu embedder, então uma busca com outro embedder falha
de forma segura. O README do `adk-rag-harness` traz a referência completa.

Combine com as decisões padrão do OpenRouter ao testar o caminho completo:

```sh
HARNESS_RAG_PROVIDER=rag-harness uv run adk web
```

Depois que o contrato offline passar, exercite o caminho do modelo real com
Ollama:

```sh
HARNESS_OFFLINE=1 OLLAMA_MODEL=llama3.1:8b uv run python evals/run_ollama_evals.py
```

Essa verificação opt-in falha se o modelo não chamar `run_workflow`, retornar a
rota errada ou produzir uma recuperação sem evidência.

A próxima fronteira de integração é o Jev. Configure a chave somente no shell
e execute:

```sh
TYPESAFE_API_KEY=sua-chave uv run python evals/run_jev_evals.py
```

Essa verificação avalia as decisões tipadas de roteamento do Jev separadamente
do Ollama e exibe apenas modelo do provedor, rota, confiança e quantidade de
evidências.
Ela exercita a camada de decisão fundamental que sustenta os quatro pilares operacionais do Jev
([Rotear, Filtrar, Pontuar e Liberar](/pt-BR/reference/jev)): protegendo contra injeções de prompt,
roteando para a faixa de modelo adequada e aplicando portões de confiança tripartites antes das ações rodarem.


## Como ler o Dev UI

### Events

A visão Events mostra a mensagem do usuário, a chamada de ferramenta do modelo,
o resultado de `run_workflow` e a resposta final. Um exemplo de recuperação
bem-sucedido se parece com isto:

```text
pedido do usuário
  → run_workflow("find the deployment policy")
  → evidência, rota e confiança
  → resposta final com a referência da fonte
```

![ADK Dev UI mostrando os eventos do workflow de recuperação](/images/adk-rag-ollama-events.png)

### Traces

A visão Traces prova qual provedor foi usado e onde o tempo foi gasto. Neste
setup, procure `generate_content ollama...`, `run_workflow`, latência e contagem
de tokens. O formato esperado é:

```text
adk_rag_router
├── call_llm → generate_content ollama...
├── run_workflow
└── call_llm → generate_content ollama...
```

![ADK Dev UI mostrando chamadas ao Ollama e execução do workflow](/images/adk-rag-ollama-traces.png)

![Primeira execução local bem-sucedida no ADK Dev UI](/images/adk-rag-ollama-first-run.png)

### State, Artifacts e Evals

- **State** mostra o estado da sessão entre as etapas.
- **Artifacts** é onde uma implementação futura pode expor arquivos gerados ou
  pacotes de evidência.
- **Evals** é o lugar para adicionar pedidos dourados e comparar roteamento,
  evidência e qualidade da resposta. Uma resposta verde no chat sozinha não é
  uma avaliação.

## Solução de problemas

| Sintoma | Verificação |
|---|---|
| `command not found: adk` | Execute `uv run adk web` a partir de `adk-rag-harness`. |
| O modelo não é chamado | Confirme que o Ollama está acessível e use um modelo com suporte a tools. |
| `ollama ps` fica vazio depois da resposta | O modelo pode ter sido descarregado; inspecione durante um pedido ativo ou rode `ollama list`. |
| A UI abre, mas o app não aparece | Inicie o servidor a partir do diretório do repositório com o diretório do app disponível e atualize a página. |
| A rota é sempre de demonstração | Confira se `HARNESS_DECISION_PROVIDER` não está definido como `demo`. |
| O trace não mostra Ollama | Confirme `OLLAMA_MODEL` e `OLLAMA_API_BASE`, depois reinicie `adk web`. |

## Checklist de evidências

Antes de considerar o laboratório concluído, registre:

1. o modelo presente em `ollama list`;
2. uma visão Events com chamada de ferramenta e resposta final;
3. uma visão Traces contendo `generate_content ollama` e `run_workflow`;
4. o prompt exato usado;
5. a rota, confiança e referência de fonte retornadas pelo workflow.

## Verifique seu aprendizado

```text
"quiz me on a Aula 18"
```

**Volte à teoria**: [16 — ADK 2](/pt-BR/lectures/lecture-16) · [17 — Construindo um Hard Harness](/pt-BR/lectures/lecture-17)

**Laboratório do projeto**: [Projeto 06 — harness ADK + RAG + Jev](/pt-BR/projects/project-06)

**Referências oficiais**: [Integração do ADK com Ollama](https://adk.dev/agents/models/ollama/) · [Interface web do ADK](https://adk.dev/runtime/web-interface/)
