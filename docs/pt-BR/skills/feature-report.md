---
title: feature-report (v2)
---

# feature-report (v2 — Eleanor)

Relato de resultado, não tutorial: o que foi entregue, decisões com trade-offs
causais, verificação executada e perguntas abertas — cada número rastreável a
diff, teste ou log.

## Entregável F1

A evolução está em `skills-artifacts/` (na raiz deste repo):

| Peça | O que é |
|---|---|
| `skills-artifacts/feature-report/SKILL.md` | Skill v2: Gather → Write → Output, com checklist de acessibilidade obrigatória |
| `skills-artifacts/feature-quiz/SKILL.md` | Skill v2: quiz 4 níveis + **modo de revisão adaptativo** (erradas entram na revisão) |
| `skills-artifacts/assets/system.css` | CSS com **tokens Eleanor** (Figtree, red `#d81f41`, gray dark, indigo), claro/escuro, `:focus-visible`, `prefers-reduced-motion`, contrastes AA |
| `skills-artifacts/assets/skeleton.html` | Skeleton acessível: `aria-live` no resultado, toggle EN/PT (`data-i18n`), progresso, revisão |
| `skills-artifacts/scripts/build-demo.py` | Gerador mecânico (o mesmo caminho da skill) — produz os demos |
| `skills-artifacts/reports/demo-report.html` | Report demo renderizado (evidência) |
| `skills-artifacts/quizzes/demo-quiz.html` | Quiz demo renderizado: 4 níveis, 12 questões, validação estrutural OK |
| `skills-artifacts/skill-design-v2.md` | A evolução do design system v1 → Eleanor, item a item |

## O que mudou (resumo)

- **Eleanor**: fonte Figtree, brand red `#d81f41` como único accent, paleta gray/indigo real dos tokens.
- **Acessibilidade executável**: foco visível em anel, movimento reduzido, `aria-live` no resultado do quiz, contraste AA, sem informação só por cor.
- **Multi-idioma**: toggle EN/PT funcionando no toolbar (pares `data-i18n-pt/en`).
- **Quiz adaptativo**: questões erradas entram automaticamente no modo de revisão — o leitor não passa batido pelo erro.

## Como usar

```
"gera o relatório dessa feature"      → skill v2 (se instalada deste repo)
"me testa com um quiz dos 4 níveis"
```

Para gerar os demos novamente:

```sh
cd skills-artifacts && python3 scripts/build-demo.py
```

**Relacionado**: [feature-quiz](/pt-BR/skills/feature-quiz) · [Criar uma skill nova](/pt-BR/skills/how-to-create)