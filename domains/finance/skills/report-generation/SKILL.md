---
name: report-generation
description: Gera e publica o relatório financeiro com fontes citadas — o último passo do pipeline noturno (nightly-run.sh). Use quando o usuário pedir o relatório, o resumo da madrugada, ou 'o que saiu de relatório hoje'.
---

# Geração de relatório financeiro

O relatório noturno é o artefato do harness dormindo: publicado com fontes
antes do time chegar (Aula 13: loop autônomo com critério de saída).

## Gather

- O contexto da área (planilhas) — via Area Copilot (`area_harness query`).
- A data: o relatório é `relatorios/YYYY-MM-DD-<slug>.md`, um por dia.

## Write

Estrutura fixa do relatório:

1. **Data e pipeline** — quando rodou, com qual versão do playbook.
2. **Perguntas respondidas** — cada uma com FONTE citada (arquivo + linhas).
3. **Reconciliação** — esperado vs. real (skill spreadsheet-analysis); falha registrada, nunca arredondada.
4. **Alertas** — dados faltantes, outliers, divergências; cada um com linha citada.
5. **Status** — `CONSOLIDADO` (tudo reconciliado) ou `COM DIVERGÊNCIAS` (lista).

## Output

- `relatorios/YYYY-MM-DD-<slug>.md` publicado (pasta versionada do playbook).
- Se o status for `COM DIVERGÊNCIAS`: registrar no log do harness (log-event.sh) — fricção registrada é dívida que não vira (Aula 11).