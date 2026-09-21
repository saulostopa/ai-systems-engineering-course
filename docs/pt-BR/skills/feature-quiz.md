---
title: feature-quiz
---

# feature-quiz — o artefato que descobre se você entendeu

> O relatório conta o que aconteceu. O quiz descobre se aquilo grudou. Quatro
> níveis, e toda resposta errada entra numa lista de revisão automaticamente — o
> leitor não passa batido pelo que errou.

## Veja primeiro

<a href="/demos/demo-quiz.html" target="_blank" rel="noopener">
<strong>▶ Abrir o quiz demo</strong></a> — responda antes de continuar lendo; leva um minuto.

Repare no que **não** acontece quando ele carrega: nada está destacado. Escolha
suas respostas, aperte **Conferir respostas**, e só então cada opção fica verde
ou vermelha, cada justificativa aparece, e as erradas se juntam na revisão.

::: warning O bug que vale conhecer
Até esta página ser escrita, a opção correta era estilizada incondicionalmente —
toda resposta ficava verde desde o carregamento. O quiz era entregue com o
próprio gabarito à mostra. Uma regra de CSS agora condiciona a revelação a
`.quiz-level[data-checked="true"]`, que o script só marca depois que você envia.
:::

## Os quatro níveis

| Nível | Cobra | Falha quando |
|---|---|---|
| **Básico** | recall — fatos de superfície | o leitor nunca leu o relatório |
| **Intermediário** | mecânica — o fluxo principal | leu, mas não acompanhou |
| **Avançado** | racional — o trade-off aceito sobre a alternativa recusada | sabe *o quê*, não *por quê* |
| **Difícil** | bordas — falhas reais do diff e dos testes | nunca olhou os limites |

Cada questão: um enunciado, três opções com exatamente uma correta, e uma
justificativa `quiz-why` rastreável ao material. **Difícil nunca significa
pegadinha** — uma casca de banana inventada não ensina nada e custa confiança.

## Adaptatividade

A casca já implementa: pontuação por nível anunciada via `aria-live`, e todo
item errado copiado para o `#review-root` automaticamente. O gerador só monta os
níveis — nunca reimplementa a lógica, que é por isso que um quiz não sai com o
laço de pontuação quebrado.

## Como o harness chama a skill

```yaml
artifacts:
  - diagram
  - report
  - quiz
```

```
[wm-harness] ERROR: feature/OEM-123 owes a delivery quiz (flow 'feature-default')
             — the feature-quiz skill writes docs/artifacts/feature-OEM-123-quiz.html
```

```sh
./scripts/artifacts.sh feature/OEM-123 --kind quiz
# [artifacts] OK — quiz: 25 x 'quiz-opt' visible
```

A checagem conta opções que sobrevivem **fora de comentários HTML** — bytes no
disco não são evidência de que um navegador vai mostrar alguma coisa.

**Relacionados**: [feature-report](/pt-BR/skills/feature-report) · [feature-archify](/pt-BR/skills/feature-archify) ·
[Criar uma nova skill](/pt-BR/skills/how-to-create)
