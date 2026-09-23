---
title: Projeto 03 — Harness de App com QA
---

# Projeto 03 — Harness de App com QA

> O harness que combina o teste E2E do time de QA com a navegação agêntica — o agente abrindo o app, navegando e validando com visão.

## Objetivo

Montar o **App Harness** em duas camadas:

1. **Camada QA** — testes E2E com Playwright como gate mecânico (a skill `qa-playwright-e2e` do `harness-agent-skills`).
2. **Camada agêntica** — o agente sobe o app, navega como usuário e valida visualmente (screenshots + modelo de visão), do build ao aceite.

É o EPIC C do curso — aqui você constrói uma versão funcional dele.

## Pré-requisitos

- Um app (pode ser o repo de um app Webmotors ou um app de teste) com `npm run dev`/build funcionando.
- Playwright instalado (a skill usa Python + Playwright).
- Um agente com capacidade de visão (Claude, GPT-4o, Gemini).

## Passo a passo

### Camada 1 — E2E como gate

1. Instale a skill `qa-playwright-e2e` (veja a [Biblioteca](/pt-BR/resources/) para o comando de instalação).
2. Peça ao agente:

```
"escreve os testes E2E dessa tela com Playwright"
```

3. Exija os padrões da skill:
   - locators semânticos (`get_by_role`) — nunca CSS/XPath frágil;
   - Page Object Model;
   - interceptação de rede para setups determinísticos;
   - testes que falham de verdade se a tela quebrar.

4. Torne o E2E um gate de commit:

```bash
# pre-commit (exemplo simplificado)
#!/bin/bash
# roda E2E para arquivos de frontend alterados
if git diff --cached --name-only | grep -qE '^src/.*\.(tsx|vue|jsx)$'; then
  pytest tests/e2e -q || { echo "E2E falhou — commit bloqueado"; exit 1; }
fi
```

### Camada 2 — Navegação agêntica com visão

1. Suba o app: `npm run dev` (ou build + preview).
2. Dê ao agente a missão de navegação:

```
"sobe o app, navega até a tela X como um usuário e valida:
 1. o fluxo completo funciona;
 2. não há quebra visual (layout, sobreposição, loading infinito);
 3. os estados vazios e de erro são aceitáveis.
 Tire screenshots como evidência e me diga o que encontrou."
```

3. O agente deve produzir **evidência visual** (screenshots) + veredito por critério.
4. Aprenda com o que ele achar: cada achado vira teste E2E novo na Camada 1 — **o loop fecha**: a navegação agêntica encontra, o E2E imortaliza.

## O loop completo

```
build → E2E (gate) → navegação agêntica (visão) → achados → novos testes E2E → ...
```

O app harness não é "QA ou agente" — é **QA e agente**, cada um pegando o que o outro não pega: o E2E é determinístico e barato; a navegação agêntica é exploratória e vê o que o teste não prevê.

## Verificação

- Uma mudança de frontend **sem** teste E2E é bloqueada pelo hook.
- A navegação agêntica produz screenshots + veredito por critério (aceito/rejeitado).
- Pelo menos 1 achado da navegação virou teste E2E novo.

## Entregável

O hook de E2E funcionando no repo + os testes E2E + o registro de uma rodada de navegação agêntica com screenshots e vereditos.

::: tip Status
A versão oficial com triagem de falhas, perf e integração total é o **EPIC C** do curso.
:::

**Próximo projeto**: [04 — Harness de domínio](/pt-BR/projects/project-04).