---
title: Projeto 01 — Baseline vs. harness mínimo
---

# Projeto 01 — Baseline vs. harness mínimo

> O primeiro experimento do curso: a mesma feature, com e sem harness. Meça a diferença antes de confiar nela.

## Objetivo

Rodar uma feature real **duas vezes** — uma com o agente "cru" (sem harness) e outra com o harness mínimo — e comparar:

- tempo até a entrega;
- número de erros corrigidos depois do primeiro "pronto";
- quantidade de retrabalho (commits de correção);
- sensação de confiança (verificado vs. "parece que funciona").

O resultado é o **seu** baseline: a partir dele, todo harness que você construir terá um número para comparar.

## Pré-requisitos

- Um repositório de teste (pode ser um fork de projeto pequeno ou um repo novo).
- Um agente instalado (Claude Code, OpenCode, Cursor, Codex ou Gemini CLI).
- A mesma feature bem delimitada para as duas rodadas (ex.: "adicionar validação de e-mail no formulário X").

## Passo a passo

### Rodada A — sem harness (baseline)

1. Abra o repo **sem nenhum** AGENTS.md, skills ou regras.
2. Peça ao agente: `implemente a validação de e-mail no formulário X`.
3. Anote: tempo até o primeiro "pronto", o que ele verificou (se verificou), quantas correções vieram depois.
4. Não interfira — deixe o agente declarar vitória do jeito dele.

### Rodada B — com harness mínimo

1. Adicione ao repo:

```markdown
# AGENTS.md

## 1. O que este repo é
Projeto de teste para o Projeto 01 do curso.

## 2. Como verificar
- Rode `npm run build` — deve passar.
- Rode `npm test` — deve passar.
- Nada é "pronto" sem o build e os testes rodados e anexados.

## 3. Escopo
- Uma feature por vez.
- Não toque em nada fora da feature.
```

2. Adicione o estado:

```json
{
  "features": [
    { "id": "f1", "title": "Validação de e-mail", "status": "in_progress" }
  ]
}
```

3. Peça a **mesma** tarefa ao agente.
4. Anote: tempo até o "pronto" *com* build e testes, quantas correções, o que ele registrou como evidência.

### Comparação

| Métrica | Rodada A (sem harness) | Rodada B (harness mínimo) |
|---|---|---|
| Tempo até o primeiro "pronto" | | |
| "Prontos" que falharam o build/testes | | |
| Correções após o "pronto" | | |
| Evidência registrada (sim/não) | | |

## Verificação

- Build e testes passam na Rodada B (na A, anote se passavam ou se o agente "esqueceu").
- O diff da Rodada B toca só o escopo declarado.
- Você consegue apontar **o que exatamente** o harness mudou no comportamento do agente.

## Entregável

Um parágrafo no seu diário de aprendizagem (ou no `session-handoff.md` do projeto):

> "Sem harness o agente [X]; com harness ele [Y]. A diferença veio de [arquivos/políticas]."

::: tip Dica
Guarde a planilha da comparação. A mesma medição foi feita para o próprio curso nos pilotos do EPIC G — os números consolidados estão em `pilots/g4-metrics/G4-REPORT.md`, e a sua é a versão local dessa evidência.
:::

**Próximo projeto**: [02 — Harness básico instalável](/pt-BR/projects/project-02).