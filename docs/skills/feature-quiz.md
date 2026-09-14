---
title: feature-quiz (v2)
---

# feature-quiz (v2 — adaptativo)

Quiz graduado em 4 níveis sobre a feature recém-implementada, com pontuação automática, feedback por nível e **modo de revisão adaptativo**: cada questão errada entra automaticamente na revisão — o leitor não passa batido pelo erro.

## Entregável F1

A evolução está em `skills-artifacts/` (raiz deste repo): SKILL.md v2, assets (system.css Eleanor + skeleton com aria-live e toggle EN/PT), build-demo.py e o `quizzes/demo-quiz.html` renderizado como evidência (4 níveis × 3 questões, estrutura validada).

## Os 4 níveis

1. **Básico** — fatos de superfície (recall).
2. **Intermediário** — mecânica (fluxo principal).
3. **Avançado** — racional (trade-off aceito sobre a alternativa rejeitada).
4. **Difícil** — bordas e falhas reais do diff/testes (nunca pegadinha inventada).

Cada questão: stem + 3 opções (uma correta) + `quiz-why` com justificativa rastreável ao material lido.

## Adaptatividade

O skeleton já implementa: pontuação por nível com `aria-live`, e as questões erradas entram em `#review-root` automaticamente. O gerador só monta os níveis — não reimplementa a lógica.

**Relacionado**: [feature-report](/skills/feature-report) · [Criar uma skill nova](/skills/how-to-create)
