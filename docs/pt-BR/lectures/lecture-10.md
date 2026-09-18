---
title: Aula 10 — Testes de ponta a ponta mudam o resultado
---

# Aula 10 — Testes de ponta a ponta mudam o resultado

> O agente que testa de ponta a ponta entrega diferente do agente que testa "só o que mexeu".

## Por que E2E muda o comportamento do agente

Não é só sobre pegar bugs. O efeito mais importante do E2E é **no comportamento do próprio agente durante a implementação**:

- **Especificação viva**: o teste descreve o comportamento esperado com precisão — o agente codifica contra um contrato, não contra uma intuição.
- **Feedback tardio eliminado**: o erro que só apareceria em produção aparece em minutos.
- **Confiança verificável**: o agente *sabe* que terminou porque o fluxo completo passou — não porque "parece".
- **Regressão visível**: a mudança de hoje quebra o fluxo de ontem imediatamente.

O teste E2E transforma o harness de "processo que pede verificação" em "processo que verifica sozinho".

## O E2E como gate mecânico

O `webmotors-harness-factory` torna o E2E **parte do contrato de commit**:

> "Mudança de frontend sem cobertura E2E é bloqueada pelo pre-commit hook (`scripts/frontend-qa-gate.sh`)."

Ou seja: não é "não se esqueça de testar" — é "não existe commit de frontend sem teste". A skill `qa-playwright-e2e` apoia com a disciplina de qualidade:

- locators semânticos (`get_by_role`) em vez de CSS/XPath frágil;
- Page Object Model;
- interceptação de rede para setups determinísticos;
- triagem de falhas via trace viewer (o "flaky" vira evidência, não suspeita).

## Dois mundos de verificação

| | Teste unitário | Teste E2E |
|---|---|---|
| Responde | "a função funciona?" | "o usuário consegue?" |
| Velocidade | ms | segundos/minutos |
| Custo | baixo | alto |
| Feedback ao agente | porca/pino | sistema inteiro |
| É gate de commit? | nem sempre | **sim, no nosso harness** |

O ponto da aula: o harness precisa **dos dois**, mas é o E2E que fecha o laço de controle — porque ele valida o mundo inteiro, não a peça.

## O app harness e a navegação agêntica

Esta aula é a porta de entrada para o **App Harness** (EPIC C): além dos testes E2E tradicionais (o time de QA), o harness de app inclui a **navegação agêntica** — o agente sobe o app, abre a tela, navega como um usuário e valida visualmente com o modelo de visão. Os dois formam o loop completo:

```
E2E (QA)          → o fluxo do usuário é garantido por teste automatizado
Navegação agêntica → o agente vê e valida o app de verdade, do build ao aceite
```

O e2e pergunta "o fluxo funciona?"; a navegação agêntica pergunta "o app está aceitável?" — e ambas são gates.

## Na Webmotors — o caso real

Nosso próprio ecossistema tem o padrão em produção: o `webmotors-harness-factory` bloqueia commit de frontend sem E2E; o `harness-agent-skills` entrega a skill que escreve e revisa esses testes; o AgEnFK registra o resultado como etapa do fluxo (test PASSED antes de DONE). O curso inteiro é construído sobre esse mesmo loop — cada aula termina com verificação, e o site só sobe se o build passar.

## Principais aprendizados

1. E2E muda o comportamento do agente na implementação, não só na entrega.
2. Teste como gate mecânico (pre-commit) > teste como intenção.
3. Unitário valida a peça; E2E valida o mundo — os dois, sempre.
4. App Harness = E2E do QA + navegação agêntica com visão.

## Verifique seu aprendizado

```
"quiz me on a Aula 10"
```

**Próxima aula**: [11 — Observabilidade dentro do harness](/pt-BR/lectures/lecture-11).