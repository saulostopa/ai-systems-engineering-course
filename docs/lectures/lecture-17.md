---
title: Aula 17 — Construindo um Hard Harness
---

# Aula 17 — Construindo um Hard Harness

> A aula prática: o componente `hard-harness/` deste curso — grafo executável,
> contratos tipados, gates determinísticos, persistência sem banco, retomada
> e auditoria. Tudo executável aqui e agora.

## A arquitetura em uma página

```
hard-harness/
├── core/          # grafo, runner, schemas, gates, events — o núcleo
├── stores/        # FileStateStore (sem banco) + AgEnFKStore (adapter)
├── adapters/      # adk2 (inspiração opcional) + rag (provedor de contexto)
├── agents/        # planner, coder, reviewer, evidence — só raciocínio
├── examples/basic_workflow/   # o grafo completo do requisito
└── tests/         # 19 testes (transições, gates, fan-out, limites...)
```

Regra de ouro em uma linha: **o agente propõe; o runner decide; o gate
bloqueia; o store registra.**

## Máquina de estados

`WorkflowState` carrega status (`pending → running → blocked → passed →
failed → closed`), nó atual, dados persistentes, retries, chamadas de LLM e
erro. **Somente o runner transiciona** — o método `_transition` é interno.

```python
from hard_harness.core import Runner, WorkflowGraph

runner = Runner(graph, store=store, limits=Limits(max_depth=16, max_retries=2))
state = runner.run(initial={"scope": {...}})
```

## Schemas — contratos tipados

`NodeInput` (visão imutável) → `NodeOutput` (proposta) → o runner valida:

- `NodeOutput.proposed_next` — sugestão do agente; o runner aceita/recusa.
- `NodeOutput.gate` — `GateResult` com falhas `{check, expected, actual}`.
- `NodeOutput.evidence` — `Evidence` (comando, esperado, real, passou).
- `NodeOutput.review` — `ReviewResult` (verdict + findings).

## Gates determinísticos

```python
from hard_harness.core.gates import gate_from_command, gate_node_output

build = gate_node_output("build", gate_from_command("build", "npm run build", "build"))
```

O gate roda o comando real; exit ≠ 0 → falha explícita; o runner **bloqueia a
transição** (nada de "parece que funciona").

## Fan-out e join

```python
g.fan_out("coder_agent", ["build", "tests", "e2e", "lint"])
g.join("join", ["build", "tests", "e2e", "lint"], "router")
```

O runner dispara os 4 em paralelo (`MAX_CHILDREN` aplicado), agrega por id e
só então executa o join. Falha de filho NUNCA some: vira payload explícito
(`{"error": ...}`) que o join/ router decide. Fan-out sem join = erro explícito.

## Router determinístico com default

```python
def route_by_checks(state_data):
    return "passed" if state_data.get("join", {}).get("all_ok") else "failed"

g.router("router", route_by_checks, {"passed": "reviewer_agent", "failed": "correction_agent"}, default="correction_agent")
```

Rota inexistente → default assume → **nunca encerra em silêncio** (lição ADK
L2b; testado).

## Evidências

Todo gate produz `Evidence`; o nó `evidence` consolida o fan-out; eventos de
evidência são emitidos e persistidos. A moeda do harness (Aula 09) agora é
gerada e auditada pelo runtime.

## Persistência sem banco

```
.harness/
├── state.json     # snapshot atômico (tmp + rename)
├── events.jsonl   # trilha de auditoria append-only
├── artifacts/     # artefatos dos nós
└── locks/         # exclusão mútua (O_EXCL)
```

Interface `StateStore` (read/write/events) — `FileStateStore` agora;
`AgEnFKStore` e SQLite depois, com o mesmo contrato.

## Retomada e auditoria

```python
store = FileStateStore("meu_run")
runner = Runner(graph, store=store)
runner.bus.subscribe(lambda ev: store.append_event(ev))
state = runner.run(...)          # executa e persiste a cada nó
state2 = runner.run(state=store.read_state())  # retoma do checkpoint
```

Interrupção no meio? `read_state()` + `run(state=...)` retoma do nó atual.
Toda transição, recusa de proposta e falha de gate vira `Event` — auditável.

## Executando o exemplo completo

```sh
cd hard-harness
PYTHONPATH=. python3 examples/basic_workflow/workflow.py
PYTHONPATH=. python3 tests/test_hard_harness.py   # 19/19
```

## Principais aprendizados

1. Núcleo framework-agnóstico: o ADK é inspiração, não dependência.
2. Agente propõe → runner decide → gate bloqueia → store registra.
3. Contratos tipados tornam transições inválidas impossíveis de silenciar.
4. Limites (profundidade, largura, retries, LLM, timeout) vivem em código.
5. Persistência mínima em arquivo + eventos = retomada e auditoria sem banco.

## Verifique seu aprendizado

```
"quiz me on a Aula 17"
```

**Volte à teoria**: [15 — Do Markdown ao runtime](/lectures/lecture-15) · [16 — ADK 2](/lectures/lecture-16)