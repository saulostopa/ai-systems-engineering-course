---
title: Aula 14 — De loops únicos a engenharia de grafos
---

# Aula 14 — De loops únicos a engenharia de grafos

> Quando um agente não basta, você não contrata mais um agente: você projeta um grafo de agentes. E o grafo é um harness.

## O limite do loop único

Um loop único funciona para uma feature bem delimitada. Mas o trabalho real é composto: escopo, implementação, QA, revisão, evidência, publicação. Fazer tudo num loop único significa:

- um contexto só carrega o peso de tudo (custo e deriva);
- um único ponto de decisão concentra os erros;
- nenhuma especialização (o mesmo agente que escreve código também revisa — o que anula a revisão);
- sem paralelismo (QA espera o código; o código espera o QA).

## O grafo de agentes

A **engenharia de grafos** trata o trabalho como um grafo de **nós** (agentes/especialistas) e **arestas** (transferências com contrato). O harness deixa de governar um loop e passa a governar o **roteamento entre loops**:

```
          ┌──────────┐
 humano ─▶│ planejar │─▶ escopo aprovado
          └──────────┘
               │
          ┌────▼─────┐   diff     ┌────────┐   report   ┌──────────┐
          │ codificar │──────────▶│ revisar │──────────▶│ evidenciar│──▶ artefatos
          └──────────┘            └────────┘            └──────────┘
               │                                              ▲
               └─────── testes E2E / gates mecânicos ─────────┘
```

Cada nó:

- tem **entrada definida** (contrato do que recebe);
- tem **saída verificável** (o que produz e como se prova);
- pode ter **ferramentas próprias** (QA usa Playwright; o planejador usa a feature list);
- **não precisa conversar** com os outros nós — comunica por artefatos (diff, teste, report), que é exatamente a lição da Aula 03 (repo como sistema de registro).

## O padrão mais importante: especialização e revisão cruzada

No grafo, o agente que **escreve** não é o mesmo que **revisa**. Isso não é burocracia — é a correção de um defeito estrutural do loop único: quem implementou já decidiu que está certo (viés da Aula 09). A revisão cruzada traz:

- olhos novos sobre o diff;
- o revisor quebra o auto-engano;
- a evidência do revisor é registrada como etapa do fluxo.

Num workflow engine isso é nativo: as fases `code` e `review` são steps separados, e o item só avança com a validação de cada um. O "grafo" mínimo de um item gerenciado já é: plan → code → test → review → close.

## Como o harness governa o grafo

| Mecanismo | Papel no grafo |
|---|---|
| Itens com estado | O "token" que trafega entre nós |
| Gates por etapa | Impedem arestas inválidas (ex.: code sem teste) |
| Evidência por etapa | Prova que o nó cumpriu a saída antes de transferir |
| Artefatos no repo | A linguagem comum entre nós (diff, report, quiz) |
| Telemetria | Mede o custo de cada nó e da travessia inteira |

## Multi-agente no nosso futuro

Esta aula fecha o curso apontando para o que os harnesses de domínio (EPIC E) e o multi-team vão usar:

- **App Harness**: um agente implementa, um agente de QA valida com E2E, um agente navega e valida com visão — três nós no mesmo grafo.
- **Finance Harness**: o nó "processar planilhas" roda de madrugada e entrega para o nó "publicar relatório" — grafo com disparo temporal.
- **Áreas**: cada área publica artefatos (reports, quizzes) num repositório comum — a "intranet de artefatos" do EPIC F — que alimenta a busca RAG: um grafo que cruza domínios.

E o grafo se retroalimenta: os artefatos de um nó viram contexto (RAG) para o nó seguinte — conhecimento acumulado como ativo, não como conversa perdida.

## Da teoria ao executável — o hard harness

A Aula 14 descreveu grafos como conceito; as aulas 15-17 o transformam em
**código executável**. O componente `hard-harness/` deste curso materializa
exatamente o que esta aula desenhou:

| Teoria (Aula 14) | Executável (hard-harness) |
|---|---|
| Nós especializados | `agents/` (planner, coder, reviewer, evidence) |
| Arestas com contrato | `core/graph.py` (fan_out, join, router com default) |
| Comunicação por artefatos | `NodeOutput.artifacts` + `ArtifactRef` |
| Revisão cruzada | `ReviewResult` — quem escreve não revisa |
| Quem governa o grafo | `core/runner.py` — única autoridade de estado |
| Loops com critério | retries/limites em `Limits` + gates determinísticos |
| Evidência | `Evidence` gerada por gates e consolidada no nó evidence |

O grafo da Aula 14 deixou de ser diagrama: virou `examples/basic_workflow` —
rodável com `PYTHONPATH=. python3 hard-harness/examples/basic_workflow/workflow.py`,
com o mesmo formato do ADK 2 (funções para previsível, agentes para
raciocínio, routers explícitos).

## Principais aprendizados

1. Loop único concentra custo, erro e viés; o grafo distribui e especializa.
2. Nós se comunicam por artefatos verificáveis, não por conversa.
3. Quem escreve não revisa: revisão cruzada quebra o auto-engano.
4. O harness governa o grafo: itens, gates, evidência, artefatos e telemetria.
5. O futuro multi-team é um grafo de loops especializados, com contexto compartilhado via RAG.

## Verifique seu aprendizado

```
"quiz me on a Aula 14"
```

**Continue**: [15 — Do Markdown ao runtime executável](/pt-BR/lectures/lecture-15) ·
[16 — ADK 2](/pt-BR/lectures/lecture-16) · [17 — Construindo um Hard Harness](/pt-BR/lectures/lecture-17).