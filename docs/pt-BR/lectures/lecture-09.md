---
title: Aula 09 — Declarar vitória cedo demais
---

# Aula 09 — Declarar vitória cedo demais

> O agente diz "pronto". O harness responde: "prove".

## O padrão que se repete

O agente implementa a feature, roda uma vez, vê que "funciona" e declara vitória. O que ele não verificou:

- os casos de borda (empty state, dados duplicados, payload inválido);
- os testes existentes (e os que ele quebrou);
- o build completo (não só o trecho que ele tocou);
- o efeito em componentes vizinhos (o factory chama isso de *neighbor effects*);
- a integração ponta a ponta (Aula 10);
- o contrato com hooks/gates (lint, format, e2e gate).

"Parece que funciona" é a forma mais cara de "pronto" que existe: o custo de descobrir depois é 10x o de verificar agora.

## A mecânica do auto-engano

O agente não mente de propósito — ele **completa o raciocínio na cabeça** e confunde intenção com resultado. A escrita do código *produz* a sensação de que o código funciona (o viés de fluência). Contra isso, o harness oferece uma única arma confiável: **evidência externa obrigatória**.

## Evidência antes de "done"

O `webmotors-harness-factory` transforma isso em política (`policies/evidence-required.md`):

> "A conclusão requer evidência registrada: comandos executados, esperado vs. real. Nunca afirme 'done' sem prova."

Na prática, evidência é:

```
✓ build passou            (output do comando, não "deve passar")
✓ testes rodaram          (nome dos testes + contagem, não "testei")
✓ diff revisado           (git diff: só o escopo declarado)
✓ gates passaram          (pre-commit/pre-push hooks)
✓ artefato gerado         (report/quiz/flowchart salvos)
```

E o requisito sutil do factory:

> "Compare os nomes dos testes antes e depois e confirme que nenhum foi deletado, renomeado, pulado ou enfraquecido — uma suíte verde com menos testes do que você começou é uma regressão, não um passe."

## O fluxo do AgEnFK como professor

O workflow do AgEnFK encarna a aula:

1. `verify` exige evidência com **critérios de saída obrigatórios** por passo;
2. o teste é uma etapa separada (`log-test PASSED/FAILED`);
3. **DONE só é alcançável via `validate_progress` no passo final** — não existe "marcar como done".

A story A1 passou por isso: o gate recusou o DONE direto; o caminho foi rodar o build, registrar o teste com o comando real, e avançar com evidência. O "declarei vitória" foi convertido em "provei a vitória".

## A pergunta que desarma o auto-engano

Antes de qualquer "pronto", o harness faz quatro perguntas — e a resposta é sempre um comando executado, nunca uma frase:

| Pergunta | Resposta exigida |
|---|---|
| Está construído? | `build` com exit 0 (output anexado) |
| Está coberto? | testes novos + suíte completa passando, sem redução |
| Está no escopo? | `git diff` mostrando só o declarado |
| Está integrado? | E2E/gates/hooks passando |

## Na Webmotors

- **Dev**: o "pronto" de uma tela inclui o e2e do `qa-playwright-e2e` passando no gate — não a opinião do agente.
- **QA**: a triagem de flaky não aceita "deve ser flaky da rede" — exige trace viewer e evidência do teste.
- **Finanças**: o relatório de madrugada não vale sem a validação das planilhas (esperado vs. real reconciliado).
- **Games**: o build para a plataforma não sobe sem a validação de publish.

## Principais aprendizados

1. "Parece que funciona" é o custo mais caro de "pronto".
2. Intenção ≠ resultado: evidência externa obrigatória quebra o auto-engano.
3. Suíte verde com menos testes é regressão, não passe.
4. "Done" é um estado alcançado por fluxo com prova, não uma palavra.

## Verifique seu aprendizado

```
"quiz me on a Aula 09"
```

**Próxima aula**: [10 — Testes de ponta a ponta mudam o resultado](/pt-BR/lectures/lecture-10).