---
title: Backlog — provedores de decisão via CLI
---

# Backlog — provedores de decisão via CLI

Status: **backlog** · Priority: **P2** · Scope: harness ADK + RAG + Jev

## Objetivo

Adicionar adapters opcionais de decisão para agentes CLI autenticados
localmente:

- `HARNESS_DECISION_PROVIDER=cli-agy`;
- `HARNESS_DECISION_PROVIDER=cli-codex`;
- `HARNESS_DECISION_PROVIDER=cli-claude`.

Os adapters permitiriam comparar decisões tipadas de roteamento dos CLIs
instalados sem mudar o workflow ADK nem o contrato neutro de provider
`DecisionProvider`.

## Contrato proposto

Cada adapter deve executar um pedido não interativo e retornar o mesmo
`DecisionResult` tipado usado pelo Jev e pelos providers compatíveis com OpenAI.
O pedido deve incluir o estado atual, as perguntas delimitadas e um JSON Schema
estrito para respostas `Noul`, `Choice` e `Score`.

A implementação deve usar os modos de impressão/não interativos dos CLIs:

| Provider | Modo candidato | Controles necessários |
|---|---|---|
| Agy | `--print --output-format json` | desabilitar slash commands; sem tools do workspace |
| Codex | `exec --ephemeral --sandbox read-only --output-schema` | sem edição, worktree ou sessão persistente |
| Claude | `-p --output-format json --json-schema` | sem tools; negar prompts de permissão |

As flags devem ser configuráveis, pois as versões dos CLIs podem mudar. O
adapter nunca deve executar uma sessão interativa irrestrita dentro de
`run_workflow`.

## Guardrails

- execução somente leitura por padrão;
- sem shell, escrita de arquivos, browser ou tools MCP;
- timeout e encerramento do processo;
- limite de tamanho da saída;
- parsing JSON e validação de schema estritos;
- nenhuma API key ou saída bruta do CLI nos logs;
- falhas do provider seguem o fallback seguro do workflow;
- decisões CLI são consultivas e não autorizam ações irreversíveis;
- evals separadas por CLI e versão do modelo.

## Plano de avaliação

Executar os prompts dourados de resposta direta, recuperação, esclarecimento e
bloqueio. Comparar rota, calibração de confiança, coleção, estratégia,
evidência e latência com `ollama` e o Jev oficial quando disponível.
Registrar a versão do CLI e a configuração do comando em cada resultado.

## Critérios de aceitação

- Cada provider CLI passa nos testes compartilhados do contrato `DecisionProvider`.
- Saídas malformadas, truncadas ou fora do schema são rejeitadas.
- Um CLI travado ou indisponível chega ao fallback determinístico.
- O provider padrão continua sendo `demo`; ativar um CLI é explícito.
- A integração não modifica o workspace nem cria sessões persistentes.
