---
name: feature-quiz
description: Gera um quiz HTML graduado em 4 níveis sobre uma feature recém-implementada, com pontuação automática, feedback por nível, modo de revisão adaptativo (questões erradas repetidas) e suporte a dois idiomas. Use quando o usuário pedir para ser testado/avaliado sobre uma feature ou material.
---

# Feature quiz (v2 — adaptativo)

Quiz graduado em 4 níveis com **modo de revisão adaptativo**: cada questão
errada entra automaticamente na revisão (repetição com o porquê à mostra) —
o leitor não "passa batido" pelo erro (Aula do curso: capacidade crítica).

## Gather

- O relatório da feature (`reports/<mesmo-slug>.html`) — o quiz deve concordar com ele nas decisões e na verificação.
- O diff e os testes: **difícil** vem de edge case ou falha real presente no diff/testes, nunca de pegadinha inventada.
- Cada questão precisa ser respondível a partir do material lido.

## Write

Quatro `.quiz-level` (sempre nesta ordem, `data-level="tier-1..4"`, com `data-level-label` e `data-level-hint`):

1. **Básico** — fatos de superfície (o que faz, onde mora, como invoca). 3 questões.
2. **Intermediário** — mecânica (como funciona, fluxo principal). 3 questões.
3. **Avançado** — racional (por que esta decisão sobre a rejeitada; o trade-off aceito). 3 questões.
4. **Difícil** — bordas e falhas (o que quebra, limites, interação com outros sistemas). 3 questões.

Cada questão: um `.quiz-stem`, três `.quiz-opt` (exatamente um `data-correct="true"`), um `.quiz-why` com justificativa rastreável.

**Adaptatividade (v2)** — o skeleton já implementa:
- pontuação por nível com `aria-live` no resultado;
- questões erradas entram em `#review-root` (revisão com o texto da pergunta) — o gerador só precisa montar os 4 níveis; o modo de revisão é automático;
- toggle EN/PT: adicione `data-i18n-pt`/`data-i18n-en` em todos os textos (stem, opções, hint, why).

## Output

- Renderize pelos assets v2 (`system.css` + `skeleton.html` copiados inteiros).
- Salve `quizzes/YYYY-MM-DD-<slug>-quiz.html`, entregue **sem respostas marcadas** (uma tentativa por pergunta — reload é o único retry, sem localStorage de respostas).