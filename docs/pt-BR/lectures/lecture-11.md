---
title: Aula 11 — Observabilidade dentro do harness
---

# Aula 11 — Observabilidade dentro do harness

> Se você não mede o trabalho do agente, você não sabe se o harness funciona.

## O paradoxo da confiança

O harness impõe gates, verificação e evidência. Mas quem verifica o **próprio harness**? Quem diz que os gates estão funcionando, que o fluxo está fluindo, que o tempo por feature está caindo (ou subindo)?

Sem observabilidade, o harness é uma caixa preta que "parece que está ajudando". Com observabilidade, ele é um sistema que você **pode melhorar com dados**.

## O que observar

| Dimensão | Pergunta | Fonte de dados |
|---|---|---|
| Fluxo | Quanto tempo cada item leva por etapa? | Timestamps do workflow |
| Fricção | Quantos retries, loops, comandos repetidos? | Logs de sessão, `log-friction` |
| Custo | Quantos tokens por feature? Por etapa? | Telemetria de uso |
| Qualidade | Quantos testes falharam antes do green? Quantas retomadas? | Trilha de teste do fluxo |
| Saúde do harness | Gates bloqueando o esperado? Hooks rodando? | Health check, validação do harness |

## O `log-friction` do factory

O `webmotors-harness-factory` tem uma skill dedicada: **`log-friction`** — registra cada atrito do fluxo (agente travou, comandou em loop, o contexto estourou, o gate bloqueou algo errado). A regra de ouro:

> "Não existe 'o harness está bom' — existe 'o harness está bom *até agora*'. Fricção não registrada é dívida de observabilidade."

E a skill vem com um critério de decisão que vimos no `rag-harness.md`:

> "Reabra esta proposta somente se: (1) o harness estiver em uso real; (2) `log-friction` mostrar dor real de recuperação de contexto; (3) os agentes em uso não resolverem nativamente."

Ou seja: **a decisão de construir foi adiada por falta de evidência, e a evidência viria da observabilidade.** Esta é a aula mais estratégica do curso — ela ensina a decidir com dados em vez de intuição.

## Telemetria no AgEnFK

O AgEnFK coleta eventos de tokens, comandos e adoção, com um banco dedicado e um painel. As perguntas que ele responde no nosso projeto:

- Quanto custou a story A1 em tokens? (para o benchmark do EPIC G)
- Quanto tempo cada fase (plan → code → verify) levou?
- O gatekeeper bloqueou quantas vezes, e foi correto?

Esses números alimentam o **health check do harness** — a métrica que vamos usar no EPIC G (métricas e evidência) para provar o valor do harness para o C-Level.

## Observabilidade para cada domínio

O princípio se estende aos harnesses de domínio (EPIC E):

- **Finanças**: o harness de madrugada registra quantas planilhas processou, quantas validações falharam, quanto tempo levou — o relatório da manhã vem com *prova*.
- **Games**: quantos playtestes simulados rodaram, quantos builds de publish passaram.
- **Comercial**: quantos decks gerados, tempo por proposta.

## O laço de melhoria

```
medir → detectar fricção → ajustar o harness → medir de novo
```

O harness é um produto como qualquer outro: sem observabilidade, você melhora por palpite. Com ela, você melhora por evidência — que é exatamente a cultura que este curso ensina a aplicar ao próprio trabalho.

## Principais aprendizados

1. Quem verifica o verificador? Observabilidade é a resposta.
2. Meça fluxo, fricção, custo, qualidade e saúde do harness.
3. `log-friction`: fricção não registrada é dívida de observabilidade.
4. Decisões de construir/adotar devem partir de evidência, não de intuição.
5. Observabilidade alimenta o loop de melhoria contínua do harness.

## Verifique seu aprendizado

```
"quiz me on a Aula 11"
```

**Próxima aula**: [12 — Sessões terminam com estado limpo](/pt-BR/lectures/lecture-12).