# Aulas

A teoria por trás de harness engineering, adaptada para a realidade da Webmotors.
Cada aula termina com um `feature-quiz` gerado pela própria skill — você aprende
harness engineering consumindo os artefatos que o harness produz.

## Currículo

| # | Aula | Resumo |
|---|------|--------|
| 01 | [Por que agentes capazes ainda falham](/lectures/lecture-01) | O modelo não é o produto; o ambiente decide o resultado. |
| 02 | [O que é um harness, de fato](/lectures/lecture-02) | Ferramentas, prompt, skills e o loop fechado de trabalho. |
| 03 | [O repositório como sistema de registro](/lectures/lecture-03) | A verdade vive no repo, não na conversa. |
| 04 | [Por que um único arquivo de instruções falha](/lectures/lecture-04) | Rotear por arquivos pequenos vence empilhar tudo num AGENTS.md gigante. |
| 05 | [Continuidade em tarefas longas](/lectures/lecture-05) | Estado entre sessões: progresso, handoff e retomada. |
| 06 | [Inicialização como fase própria](/lectures/lecture-06) | O boot do harness antes do trabalho começar. |
| 07 | [Excesso de autonomia e entrega incompleta](/lectures/lecture-07) | Escopo, gates e o que fica de fora. |
| 08 | [Feature lists como primitivas de harness](/lectures/lecture-08) | `feature_list.json` como fonte de verdade do que fazer. |
| 09 | [Declarar vitória cedo demais](/lectures/lecture-09) | Evidência antes de "done". |
| 10 | [Testes de ponta a ponta mudam o resultado](/lectures/lecture-10) | QA como gate mecânico, não como intenção. |
| 11 | [Observabilidade dentro do harness](/lectures/lecture-11) | Medir friction, loops e custo de cada feature. |
| 12 | [Sessões terminam com estado limpo](/lectures/lecture-12) | Clean state, handoff e a próxima sessão agradece. |
| 13 | [De prompts manuais a loops autônomos](/lectures/lecture-13) | Loop engineering: planejar, agir, verificar, repetir. |
| 14 | [De loops únicos a engenharia de grafos](/lectures/lecture-14) | Múltiplos agentes, orquestração e o futuro multi-agente. |

::: tip Como estudar
Cada aula termina com a instrução do quiz — peça ao seu agente:

```
"quiz me on a Aula 01"   (ou a aula que você acabou de ler)
```

A skill `feature-quiz` gera o quiz em 4 níveis e você valida o que absorveu.
:::