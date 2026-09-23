---
title: Hard Harness — orquestração executável
---

# Hard Harness — orquestração executável

> O componente `hard-harness/` deste curso: grafo executável, contratos
> tipados, gates determinísticos e agentes especializados — framework-
> agnóstico, com o ADK 2 como referência conceitual (não como dependência).

## O núcleo em uma frase

**Agente propõe → runner decide → gate bloqueia → store registra.**

```
hard-harness/
├── core/          # schemas, graph, runner, gates, events
├── stores/        # FileStateStore — todo o estado fica no repo
├── adapters/      # adk2 (inspiração), rag (provedor de contexto)
├── agents/        # planner, coder, reviewer, evidence (só raciocínio)
├── examples/
│   ├── basic_workflow/    # pipeline completo (o 1º consumidor)
│   └── app_harness/       # fan-out de QA + join (integração C)
└── tests/         # 19 testes unitários
```

Aulas: [15](/pt-BR/lectures/lecture-15) · [16](/pt-BR/lectures/lecture-16) · [17](/pt-BR/lectures/lecture-17).

## Executando

```sh
cd hard-harness
PYTHONPATH=. python3 examples/basic_workflow/workflow.py   # pipeline completo
PYTHONPATH=. python3 tests/test_hard_harness.py            # 19/19
```

## Integração com os cinco harnesses

### 1 · Harness básico (B) — o primeiro consumidor real

O `examples/basic_workflow` é o workflow `plan → code → test → review → close`
que o harness básico sempre documentou — agora **executável**:

```
boot → load_scope → planner_agent → validate_plan (gate) → coder_agent
  → fan-out [build, tests, e2e, lint] → join → router
      ├─ passed → reviewer_agent → evidence → close
      └─ failed → correction_agent → coder_agent (retry limitado)
```

Os gates do B1 (`gatekeeper.sh`, `validate-harness.sh`) continuam nos hooks;
o que mudou é que a **ordem e o estado** agora são do grafo, não da instrução.

### 2 · Harness grande (B2) — o store é uma interface

O runner nunca toca na persistência diretamente: ele fala com `StateStore`, e a
única implementação que acompanha o núcleo é o `FileStateStore` — todo byte de
estado no repo, que é o que o [harness grande](/pt-BR/harness-designs/enterprise-harness)
exige da camada B.

Essa interface é o ponto de extensão. Uma organização que já roda um sistema de
gestão pode colocá-lo atrás dos mesmos quatro métodos e o runner não percebe.
O `examples/adapters/agenfk_store.py` é um exemplo trabalhado: lê item/status de
um CLI externo, registra avanço e evidência, e **para e informa** quando o
sistema está indisponível — nunca contorna. Nada dentro de `hard_harness/`
importa esse arquivo; ele é a demonstração de que a costura existe, não uma
dependência.

### 3 · App harness (C) — fan-out de QA + join

`examples/app_harness/` demonstra o padrão do App Harness: um nó dispara em
paralelo **testes unitários, E2E, acessibilidade e navegação exploratória**,
e o `join` consolida os resultados antes do router decidir. Um só núcleo,
quatro verificações — nada de engine por verificação.

### 4 · RAG / Area Copilot (D) — RAG como nó de contexto

`adapters/rag.py` envolve o `AgentController` do rag-harness com contrato
mínimo: `provide_context(question) → contexto tipado`. O workflow *pede*
contexto (nó `context`), o RAG **não decide transições** — não recebe o
runner e nunca propõe próximo nó. Recuperação separada da orquestração.

```python
rag = RagContextProvider(rag_harness_root=".../rag-harness", index_dir=".../.rag_index")
g.add_node(Node("context", NodeKind.DETERMINISTIC, rag.as_node()))
```

### 5 · Harnesses de domínio (E) — skills e schemas no mesmo núcleo

Finance, Games e Commercial **não criam engines próprios**: fornecem ao núcleo
1) skills (o conhecimento do domínio), 2) schemas (contratos tipados dos seus
artefatos) e 3) gates (suas verificações — reconciliação, playteste,
proposal-check). O `domains/` continua sendo a biblioteca de conhecimento; o
`hard-harness` é o único motor.

## LLM providers — OpenRouter (padrão), Ollama (opcional)

Os agentes do núcleo recebem um provider injetável
(`hard_harness/llm/providers.py`). Seleção por ambiente, sem surpresa de rede:

```sh
# padrão (mesmo fluxo desta sessão):
OPENROUTER_API_KEY=... PYTHONPATH=. python3 examples/basic_workflow/workflow.py

# opcional — local:
OLLAMA_API_URL=http://localhost:11434 PYTHONPATH=. python3 examples/basic_workflow/workflow.py

# sem env: stub determinístico (aviso claro), perfeito para testes/offline
```

- **OpenRouterProvider** — API compatível com OpenAI (stdlib urllib), modelo
  padrão `deepseek/deepseek-v4-flash-0731` (o mesmo desta sessão), usage capturado.
- **OllamaProvider** — endpoint local `/v1/chat/completions`, probe de disponibilidade.
- **Custo no runner** — o provider anexa `llm_cost` (usage em k-tokens) ao
  payload do agente; o runner aplica `Limits.llm_budget` em cima do custo real.
- **Evidência viva**: o workflow completo rodou com OpenRouter real — planner
  gerou plano (1.157 k-tokens), reviewer pediu changes no diff do stub
  (raciocínio real), evidence sintetizou; 4 chamadas, 19 eventos, status closed.

## Decisões de arquitetura (e limites honestos)

| Decisão | Por quê |
|---|---|
| Núcleo framework-agnóstico | ADK 2 é inspiração/adapter; orquestração própria não depende de provedor |
| Agentes só raciocinam | autoridade de estado nunca é delegada (testado) |
| Router com default obrigatório | rota inexistente nunca encerra em silêncio (lição ADK L2b) |
| Persistência em arquivo primeiro | `.harness/` (state.json + events.jsonl + artifacts + locks) — banco depois |
| Limites em código | MAX_DEPTH/CHILDREN/RETRIES/LLM_CALLS/timeout/budget no runner |
| RAG = contexto, nunca orquestrador | recuperação separada da orquestração (requisito do curso) |
| Sem banco nesta versão | `FileStateStore` hoje; SQLite ou sistema externo depois, pela mesma interface |

**Limitações**: agentes são stubs (provider LLM a injetar); Collaborative e
Dynamic (ADK 2) são evolução declarada, não implementados no núcleo — o grafo
já suporta fan-out runtime via `run_fanout` com `MAX_CHILDREN`.

**Relacionados**: [Aula 16 (ADK 2)](/pt-BR/lectures/lecture-16) · [Harness básico](/pt-BR/harness-designs/basic-harness) · [Harness enterprise](/pt-BR/harness-designs/enterprise-harness) · [App Harness](/pt-BR/harness-designs/app-harness) · [RAG](/pt-BR/harness-designs/rag-harness) · [ADK + RAG + Jev](/pt-BR/harness-designs/adk-rag-jev-harness) · [ADK RAG PostgreSQL](/pt-BR/harness-designs/adk-rag-postgres-harness)
