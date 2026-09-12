# App Harness — camada QA (E2E)

> Gate mecânico de E2E para o app harness: mudança de frontend sem teste
> correspondente = commit bloqueado. Modelado no `frontend-qa-gate.sh` do factory.

## O que está aqui

```
app-harness/
├── scripts/
│   └── e2e-gate.sh              # pre-commit gate (fail-open sem config)
├── templates/
│   ├── .harness/config.yaml     # config: paths de frontend + suíte E2E
│   └── e2e/
│       ├── pages/search_page.py # exemplo de Page Object Model
│       └── test_search.py       # exemplo de teste com rede interceptada
└── skills/                      # (C2) navegação agêntica com visão
```

## Instalação (em cima do harness básico)

```sh
cp app-harness/scripts/e2e-gate.sh <projeto>/scripts/
cp app-harness/templates/.harness/config.yaml <projeto>/.harness/config.yaml
# adiciona o gate ao pre-commit:
echo 'exec "$(dirname "$0")/../scripts/e2e-gate.sh"' >> <projeto>/.githooks/pre-commit
```

## Como funciona o gate

1. Config ausente (`fail-open`): nada a checar — o harness de conteúdo não quebra.
2. Frontend staged (ex.: `src/*.tsx`)? Sem teste E2E staged em `tests/e2e/` → **bloqueia**.
3. `pytest` disponível? Roda a suíte tocada — falha → **bloqueia** (com triagem via trace viewer).
4. Bypass consciente: `.harness/skip-e2e-gate` (expira em 5 min) — registrado, não silencioso.

## Padrões exigidos dos testes (skill qa-playwright-e2e)

- Locators semânticos (`get_by_role`, `get_by_label`) — nunca CSS/XPath frágil.
- Page Object Model — um arquivo por tela.
- Interceptação de rede (`page.route`) — setup determinístico, sem depender da API.
- Flaky é bug: triar com `playwright show-trace`, nunca "re-rodar até passar".

## Triagem de flaky — o protocolo

```
pytest tests/e2e -q --trace=retain-on-failure   # captura trace na falha
playwright show-trace trace.zip                 # inspeciona passo a passo
```

Perguntas da triagem: o locator era semântico? O setup era determinístico
(interceptado)? O estado anterior da tela era esperado? Se a resposta é "não",
o teste é o bug — não o app.

## Verificação

- Mudança de frontend sem E2E: commit bloqueado com mensagem clara.
- Com E2E: suíte roda e o commit passa.
- `validate-harness.sh` continua verde (gate novo não quebra o harness).

**Camada 2 (agêntica)**: [navegação agêntica com visão](/harness-designs/app-harness) — C2.