---
title: App Harness — QA + navegação agêntica
---

# App Harness — QA + navegação agêntica

> O harness que combina o teste E2E determinístico (camada QA) com a
> exploração agêntica com visão (camada de navegação). Duas camadas, um app.

## As duas camadas

```
┌────────────────────────────────────────────────────────┐
│ Camada 2 — Navegação agêntica (C2)                     │
│ Agente sobe o app, navega, valida com visão,           │
│ produz veredito + screenshots como evidência           │
├────────────────────────────────────────────────────────┤
│ Camada 1 — QA (C1)                                     │
│ E2E Playwright como gate mecânico de commit            │
│ (e2e-gate.sh) + triagem de flaky via trace viewer      │
├────────────────────────────────────────────────────────┤
│ Esqueleto — harness básico (B1)                        │
└────────────────────────────────────────────────────────┘
```

## Camada 1 — QA (E2E como gate)

Entregue em `app-harness/` (Scripts + templates):

- `scripts/e2e-gate.sh` — pre-commit gate: frontend staged sem teste E2E correspondente → **bloqueia** (fail-open sem config).
- `templates/.harness/config.yaml` — declaração de `frontend_paths` / `frontend_extensions` / `e2e_test_path`.
- `templates/e2e/` — Page Object Model + teste com rede interceptada (padrão determinístico).
- Protocolo de triagem: `--trace=retain-on-failure` + `playwright show-trace` — flaky é bug, não sorte.

Padrões exigidos (da skill `qa-playwright-e2e`): locators semânticos, POM,
interceptação de rede, zero CSS/XPath frágil.

## Camada 2 — Navegação agêntica com visão

A camada que distingue o app harness de um "repo com testes". O agente:

1. **Sobe o app** — build + dev server (ou preview do build).
2. **Navega como usuário** — via browser automation (Playwright/agente).
3. **Valida com visão** — o modelo *vê* os screenshots: layout, sobreposição,
   loading infinito, estados vazios e de erro.
4. **Produz veredito por critério** — aceito/rejeitado + screenshots como
   evidência (Aula 09: prova, não opinião).
5. **Fecha o loop** — cada achado da exploração vira teste E2E novo na camada 1
   (o exploratório encontra; o determinístico imortaliza).

A skill que implementa este protocolo está em
`app-harness/skills/agentic-navigation/SKILL.md` — instale-a em
`.claude/skills/` (ou `.agents/skills/`) do projeto do app e acione com:

```
"valida a tela de busca que a gente acabou de implementar"
```

O protocolo da skill: Gather (diff + testes + critérios de aceite) → subir o
app → estado determinístico (interceptação) → percorrer fluxos e estados de
borda → screenshots por passo → **veredito por critério** (ACEITO/REJEITADO
com screenshot). O formato do veredito é tabela + achados com causa provável
— pronto para virar teste E2E na camada 1.

```
build → E2E (gate) → navegação agêntica (visão) → achados → novos testes E2E → ...
```

## Por que as duas camadas

| | E2E (QA) | Navegação agêntica |
|---|---|---|
| Natureza | Determinística, barata, rápida | Exploratória, cara, lenta |
| Pega | Regressões conhecidas | O que ninguém previu |
| Quando | Todo commit (gate) | Antes de aceitar/entregar |
| Evidência | Exit code + output | Screenshots + veredito por critério |

Uma não substitui a outra: o E2E protege a cada commit; a navegação agêntica
valida o que o teste não previu — incluindo o que *parece* certo no teste e
está quebrado de verdade na tela.

## Uso no curso

- **[Projeto 03](/pt-BR/projects/project-03)** constrói o app harness do zero — este
  blueprint é a solução de referência.
- **EPIC G** (pilotos) roda as duas camadas num app Webmotors real.

**Relacionados**: [Harness básico](/pt-BR/harness-designs/basic-harness) · [Harness grande](/pt-BR/harness-designs/enterprise-harness)