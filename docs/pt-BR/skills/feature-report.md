---
title: feature-report
---

# feature-report — o resultado, com cada número rastreável

> Não é tutorial nem changelog: o que foi entregue, as decisões com seus
> trade-offs causais, a verificação que de fato foi executada, e as perguntas
> que ficaram abertas. Cada número aponta para um diff, um teste ou um log.

## Veja primeiro

<a href="/demos/demo-report.html" target="_blank" rel="noopener">
<strong>▶ Abrir o relatório demo</strong></a> — uma entrega real, renderizada pela skill.

Quatro seções, nesta ordem, porque a ordem é o argumento:

1. **O que foi entregue** — uma frase que quem não escreveu consegue repetir.
2. **Decisões e trade-offs** — *escolhi X em vez de Y porque Z, ao custo de W*.
   Uma decisão sem custo declarado é uma preferência fantasiada de decisão.
3. **Verificação** — a tabela `comando → esperado → obtido`, com saída real.
4. **Perguntas abertas** — o que a entrega *não* resolveu.

Experimente o **toggle PT/EN** e o **tema** no cabeçalho: o artefato carrega os
tokens SSTT, então lê como o resto do ecossistema, e funciona nos dois
idiomas sem um segundo arquivo.

## Como o harness chama a skill

A entrega deve um relatório, e o fluxo diz isso:

```yaml
artifacts:
  - diagram
  - report
  - quiz
```

O `wm-harness plan done` recusa arquivar o plano enquanto ele faltar:

```
[wm-harness] ERROR: feature/OEM-123 owes a delivery report (flow 'feature-default')
             — the feature-report skill writes docs/artifacts/feature-OEM-123-report.html
```

E o harness confere o artefato, não só a existência dele:

```sh
./scripts/artifacts.sh feature/OEM-123 --kind report
# [artifacts] OK — report: 5 x '<section class="card"' visible
```

::: warning Para que serve essa checagem
Ela conta seções que sobrevivem **fora de comentários HTML**. Não é paranoia — a
demo ficou meses neste repositório como um arquivo de 18 KB que renderizava uma
casca vazia, porque um comentário gerado nunca era fechado e engolia todas as
seções seguintes. O tamanho do arquivo parecia certo. Ninguém abriu.
:::

## O que vem aqui

| Peça | O que é |
|---|---|
| `skills-artifacts/feature-report/SKILL.md` | A skill: Gather → Write → Output, com checklist de acessibilidade |
| `skills-artifacts/assets/system.css` | Tokens SSTT, light/dark, `:focus-visible`, contraste AA |
| `skills-artifacts/assets/skeleton.html` | Casca acessível: `aria-live`, toggle PT/EN, progresso |
| `skills-artifacts/scripts/build-demo.py` | O gerador — e o `verify()`, que se recusa a escrever um artefato cujo conteúdo está invisível |

```sh
cd skills-artifacts && python3 scripts/build-demo.py
```

**Relacionados**: [feature-quiz](/pt-BR/skills/feature-quiz) · [feature-archify](/pt-BR/skills/feature-archify) ·
[Criar uma nova skill](/pt-BR/skills/how-to-create)
