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

A demonstração offline atual garante duas rotas:

- pedidos diretos, que respondem sem recuperação;
- pedidos recuperados, que retornam a evidência de demonstração e a referência
  da fonte.

O provedor Jev real é habilitado separadamente com `HARNESS_OFFLINE=0` e uma
`TYPESAFE_API_KEY`. Essa separação mantém os experimentos locais seguros e
repetíveis.

## Pré-requisitos

- Python 3.10 ou mais recente;
- [`uv`](https://docs.astral.sh/uv/);
- [Ollama](https://ollama.com/) rodando localmente;
- o diretório `adk-rag-harness/` disponível.

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
cd adk-rag-harness
uv sync --extra adk --extra ollama --extra jev-sdk
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
| A rota é sempre de demonstração | É esperado com `HARNESS_OFFLINE=1`, o padrão. Use `HARNESS_OFFLINE=0` e `TYPESAFE_API_KEY` somente ao testar o Jev. |
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
