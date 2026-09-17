---
name: feature-report
description: Gera um relatório HTML autocontido e acessível do que uma feature entregou — decisões, trade-offs, verificação e perguntas abertas, com números rastreados a fonte. Use quando o usuário pedir relatório/resumo do que acabou de implementar.
---

# Feature report (v2 — Eleanor)

Relato de resultado, não tutorial: o que foi entregue, as decisões com
trade-offs causais, a verificação executada e as perguntas abertas. Cada
número rastreável a diff, teste ou log — nunca estimado em silêncio.

## Gather

- A mudança: leia o diff e o código que ele toca.
- A verificação real: comandos executados e saídas (build, testes, e2e).
- O contexto do item: o que foi declarado em escopo (scope-control) — o relatório compara entrega vs. escopo.
- Se existir `reports/<mesmo-slug>.html` anterior, leia e diferencie o que mudou.

## Write

Estrutura (cards, sempre nesta ordem):

1. **O que foi entregue** — resultado, passado declarativo. Nada de processo ("trabalhamos").
2. **Decisões e trade-offs** — formato causal: "Escolhido X em vez de Y porque Z, ao custo de W".
3. **Verificação** — tabela: comando, esperado, real. Número sem fonte vira "não medido".
4. **Perguntas abertas** — perguntas de verdade, respondíveis, não disfarçadas de TODO.

## Acessibilidade obrigatória (v2)

- Contrastes AA: textos secundários/muted nas cores de papel correspondentes.
- Estrutura semântica: um `h1` por página, `section` com `aria-label`.
- Tabelas com `th`; números em `tabular-nums`.
- Nenhuma informação transmitida só por cor (verdicto tem ícone/texto além da cor).

## Output

- Renderize **inteiro** pelos assets v2: `../assets/system.css` (bloco `<style>`) e `../assets/skeleton.html` (estrutura + scripts copiados por inteiro — os scripts têm literais `${...}` que colidem com template engines; nunca reescrever).
- Todo elemento com `data-i18n` ganha `data-i18n-pt` e `data-i18n-en` (toggle EN/PT no toolbar já funciona).
- Salve em `reports/YYYY-MM-DD-<slug>.html` e abra.