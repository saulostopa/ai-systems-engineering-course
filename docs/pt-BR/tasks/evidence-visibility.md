---
title: Backlog — visibilidade das evidências no ADK Dev UI
---

# Backlog — visibilidade das evidências no ADK Dev UI

Status: **backlog** · Priority: **P2** · Scope: harness ADK + RAG + Jev

## Objetivo

Tornar as evidências de roteamento visíveis sem exigir que o aluno expanda a
resposta JSON bruta de `run_workflow` no painel Events.

## Experiência proposta

- mostrar rota, confiança, coleção e estratégia em um card compacto de evidência;
- mostrar cada fonte, score e trecho com limite claro de citação;
- distinguir os estados `direct`, `retrieved`, `clarify` e `blocked`;
- expor o mesmo pacote de evidência em Events, Artifacts e na resposta final;
- mostrar o motivo e a evidência faltante quando o workflow bloquear ou pedir esclarecimento.

## Guardrails

- a UI é uma projeção do resultado tipado do workflow;
- não deve inferir evidências a partir da prosa do modelo;
- referências de fonte permanecem ligadas a cada trecho;
- conteúdo controlado pelo usuário passa por redaction e limites de tamanho antes da exibição;
- traces continuam mostrando tempo e tokens separadamente.

## Critérios de aceitação

- o aluno identifica rota e fonte sem abrir JSON bruto;
- um resultado bloqueado ou de esclarecimento explica por que não há evidência;
- Events e Artifacts exibem o mesmo pacote estruturado;
- a camada visual não altera as decisões do workflow.
