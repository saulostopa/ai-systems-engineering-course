---
title: qa-playwright-e2e
---

# qa-playwright-e2e — o teste que o gate cobra

> O único teste E2E que vale escrever é o que falha por um motivo real. Esta
> skill escreve testes contra **papéis, não CSS** — para que um refactor que
> muda um nome de classe não vire um build vermelho em que ninguém acredita.

## O gate que cobra

Esta é a única skill do catálogo que o harness exige *antes* do commit, não
depois da entrega. O `scripts/e2e-gate.sh` roda no `pre-commit`:

```
E2E-GATE: frontend files detected:
  src/components/btn.tsx
E2E-GATE: BLOCKED — frontend change without an E2E test (Lesson 10).
  Expected path: e2e/
  Use the qa-playwright-e2e skill to write the test.
  Conscious bypass: .harness/skip-e2e-gate (expires in 5 min)
```

Traga o teste junto e ele sai da frente:

```
E2E-GATE: ok
```

Ele é **opt-in por projeto**, porque um repo sem frontend não deve pagar nada
por isso. Preencha o bloco `qa:` do `.harness/config.yaml` e ele começa a agir:

```yaml
qa:
  frontend_paths: "src"
  frontend_extensions: "tsx ts jsx js"
  e2e_test_path: "e2e"
```

::: warning O bug que este gate tinha
O parser do config ancorava no fim da linha, então um **comentário inline**
fazia o padrão não casar — a variável virava a linha inteira, o filtro de
arquivos não pegava nada, e o gate imprimia `ok` liberando todo commit. Um gate
que falha aberto num config que não consegue ler é pior que gate nenhum, porque
ele reporta sucesso. O `tests/test_e2e_gate.sh` agora trava o comportamento com
um config que tem comentários, e falha de parsing bloqueia em vez de liberar.
:::

## Como é um teste bom

O `app-harness/templates/e2e/` traz o padrão que a skill escreve. Três regras
carregam quase todo o valor:

**Locators semânticos.** O único contato com o DOM é por papel e rótulo — o
mesmo que um leitor de tela usa:

```python
self.search_input  = page.get_by_role("searchbox", name="Buscar veículos")
self.search_button = page.get_by_role("button", name="Buscar")
```

Não `page.locator(".search-form > input:nth-child(2)")`. Um teste escrito contra
estrutura quebra quando a estrutura muda, que é exatamente quando você menos
quer estar depurando seus testes.

**Page Object Model.** Uma tela, uma classe, um método por fluxo. O teste diz o
que está verificando, nunca como clicar.

**Rede interceptada.** A fixture responde a requisição com um payload fixo, para
o teste não falhar porque uma API de staging está tendo uma tarde ruim:

```python
page.route("**/api/v1/search?*", lambda route: route.fulfill(json={"results": FIXTURE_RESULTS}))
```

Determinismo não é luxo aqui — uma suíte instável é silenciada, e uma suíte
silenciada é pior que suíte nenhuma.

## Triagem de flaky

Flaky é bug, não azar. O protocolo é capturar, não re-rodar:

```sh
pytest tests/e2e --trace=retain-on-failure
playwright show-trace <artifact>.zip
```

O trace viewer reproduz a execução com o DOM a cada passo. "Passou no retry" não
é diagnóstico.

## Instalação

```sh
npx skills add <a skill qa-playwright-e2e> --agent opencode --copy
```

**Relacionados**: [qa-perf-triage](/pt-BR/skills/qa-perf-triage) · [App Harness](/pt-BR/harness-designs/app-harness) ·
[Aula 10 — Testes de ponta a ponta mudam o resultado](/pt-BR/lectures/lecture-10)
