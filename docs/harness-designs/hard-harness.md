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
├── stores/        # FileStateStore (sem banco) + AgEnFKStore (adapter)
├── adapters/      # adk2 (inspiração), rag (provedor de contexto)
├── agents/        # planner, coder, reviewer, evidence (só raciocínio)
├── examples/
│   ├── basic_workflow/    # pipeline completo (o 1º consumidor)
│   └── app_harness/       # fan-out de QA + join (integração C)
└── tests/         # 19 testes unitários
```

Aulas: [15](/lectures/lecture-15) · [16](/lectures/lecture-16) · [17](/lectures/lecture-17).

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

### 2 · Harness enterprise (B2) — adapter AgEnFK

`stores/agenfk_store.py` implementa a interface `StateStore` contra o AgEnFK:
lê item/status, registra avanço (`verify`) e evidências (`log-test`) quando
disponível. Se o AgEnFK estiver indisponível, o store **para e informa** —
nunca contorna. Hierarquia, evidência, gatekeeper e telemetria continuam
sendo do AgEnFK; o runner apenas fala com ele via interface.

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

## Decisões de arquitetura (e limites honestos)

| Decisão | Por quê |
|---|---|
| Núcleo framework-agnóstico | ADK 2 é inspiração/adapter; orquestração própria não depende de provedor |
| Agentes só raciocinam | autoridade de estado nunca é delegada (testado) |
| Router com default obrigatório | rota inexistente nunca encerra em silêncio (lição ADK L2b) |
| Persistência em arquivo primeiro | `.harness/` (state.json + events.jsonl + artifacts + locks) — banco depois |
| Limites em código | MAX_DEPTH/CHILDREN/RETRIES/LLM_CALLS/timeout/budget no runner |
| RAG = contexto, nunca orquestrador | recuperação separada da orquestração (requisito do curso) |
| Sem banco nesta versão | `FileStateStore` hoje; `AgEnFKStore`/SQLite via mesma interface |

**Limitações**: agentes são stubs (provider LLM a injetar); Collaborative e
Dynamic (ADK 2) são evolução declarada, não implementados no núcleo — o grafo
já suporta fan-out runtime via `run_fanout` com `MAX_CHILDREN`.

**Relacionados**: [Aula 16 (ADK 2)](/lectures/lecture-16) · [Harness básico](/harness-designs/basic-harness) · [Harness enterprise](/harness-designs/enterprise-harness) · [App Harness](/harness-designs/app-harness) · [RAG](/harness-designs/rag-harness)