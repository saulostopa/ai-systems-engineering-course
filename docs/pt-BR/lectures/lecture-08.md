---
title: Aula 08 — Feature lists como primitivas de harness
---

# Aula 08 — Feature lists como primitivas de harness

> O que o agente deve fazer é a pergunta mais básica do harness. A resposta é uma lista com estado.

## Por que uma lista com estado

Um prompt diz "implemente a feature X". Mas o mundo real tem 40 features, 12 em andamento, 5 bloqueadas e uma fila de bugs. O agente precisa de uma estrutura que responda, a qualquer momento:

- O que existe para fazer?
- Qual é o estado de cada uma?
- Qual é a prioridade?
- O que está bloqueado e por quê?

Essa estrutura é a **feature list**: um arquivo versionado (tipicamente JSON) onde cada feature tem identificador, título, descrição, estado e prioridade.

## O `feature_list.json` do factory

O `harness-factory` usa exatamente esse padrão:

```json
{
  "status": "not_started",
  "id": "feature/OEM-123",
  "title": "Landing page do grupo de carros",
  "description": "..."
}
```

Estados do ciclo: `not_started` → `in_progress` → `blocked` → `passing`.

O id segue a convenção de branch que já está em uso — `feature/OEM-123`,
`bugfix/AC-455`, `release/EST-3445` — então escopo, branch e ticket têm o mesmo
nome. Uma tradução a menos para um humano fazer, e um lugar a menos para errar.

E a regra de operação (que já vimos na Aula 06):

> "Apenas uma feature pode estar `in_progress` por vez. Escolha a de maior prioridade entre as `not_started`."

## Por que é uma *primitiva* de harness

"Primitiva" no sentido de bloco fundamental: a feature list é para o harness o que a lista de itens é para o fluxo de trabalho humano — **a fonte de verdade do escopo**. Dela derivam:

- o que a inicialização lê (Aula 06);
- o que a verificação compara (Aula 09 — "pronto" = feature em `passing`);
- o que o handoff resume (Aula 05);
- o que a telemetria mede (Aula 11 — quanto tempo cada feature levou).

A feature list conecta o harness ao **produto**: sem ela, o harness é um processo que roda vazio.

## A mesma ideia, com fluxo

Em escala, a feature list generaliza para itens com tipo (EPIC, STORY, TASK, BUG), hierarquia (parent/children), status por fluxo configurável e trilha de evidência. O `feature_list.json` do factory é a versão "arquivo"; um [workflow engine](/pt-BR/harness-designs/enterprise-harness) é a versão "sistema" — com gates, comentários e testes atrelados.

A lição que conecta os dois: **a forma não importa (arquivo, banco, planilha); o contrato importa** — existe uma estrutura consultável que diz o que fazer, em que estado e com que prioridade, e o harness inteiro opera em cima dela.

## Feature lists para áreas não-técnicas

Esta aula se estende ao modelo multi-team do curso (EPIC E):

- **Finanças**: a feature list é a lista de relatórios a gerar — cada um com estado, fonte de dados e prazo; o harness de madrugada processa `in_progress` e publica `passing` até o café.
- **Games**: a feature list é o backlog do jogo — personagens, narrativas, mecânicas; cada um com estado até a publicação na plataforma.
- **Comercial**: a feature list são as entregas de proposta/deck — com data, cliente e aprovação.

A estrutura é a mesma; o domínio muda. É por isso que a feature list é uma primitiva: ela é **agnóstica de domínio**.

## Principais aprendizados

1. Feature list = fonte de verdade consultável do escopo: o quê, estado, prioridade.
2. Estados explícitos (not_started → in_progress → blocked → passing) dão semântica ao trabalho.
3. Uma feature in_progress por vez é a regra de foco.
4. A forma (JSON, banco, planilha) é detalhe; o contrato é o que importa.
5. A primitiva escala para qualquer domínio — é a base do harness multi-team.

## Verifique seu aprendizado

```
"quiz me on a Aula 08"
```

**Próxima aula**: [09 — Declarar vitória cedo demais](/pt-BR/lectures/lecture-09).