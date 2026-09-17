---
title: Harness grande (multi-time)
---

# Harness grande (multi-time)

> O harness para projetos onde muitas equipes trabalham: o básico + camadas de
> governança, fluxo e observabilidade. Referência de implementação: o AgEnFK.

## Para quem é

Projetos grandes, múltiplas equipes, muitos agentes em paralelo, necessidade de
auditoria e medição. O harness grande não substitui o básico — **ele o envolve**:
cada equipe continua com seu esqueleto; a camada enterprise adiciona fluxo,
gatekeepers, telemetria e relatórios.

## As camadas

```
┌─────────────────────────────────────────────────────┐
│ 4. Observabilidade  (telemetria, log-friction,      │
│    dashboards, health check do harness)             │
├─────────────────────────────────────────────────────┤
│ 3. Workflow engine  (itens, flows, gatekeeper,      │
│    evidência, DONE só com validação)                │
├─────────────────────────────────────────────────────┤
│ 2. Governança       (políticas, gates mecânicos,    │
│    hooks, revisão cruzada)                          │
├─────────────────────────────────────────────────────┤
│ 1. Esqueleto        (harness básico por projeto:    │
│    AGENTS.md, feature list, policies)               │
└─────────────────────────────────────────────────────┘
```

### Camada 1 — Esqueleto (por projeto)

O [harness básico](/harness-designs/basic-harness). Cada equipe tem o seu, com
a feature list da sua área. Nada muda aqui quando você sobe de tamanho.

### Camada 2 — Governança

O que o básico já tem (gatekeeper de commit, validação) vira **contrato
organizacional**:

| Mecanismo | Básico | Grande |
|---|---|---|
| Gate de commit | UMA feature in_progress | + escopo declarado obrigatório (policies/scope-control.md) |
| Gate de push | Harness saudável | + relatório de PR obrigatório, CI com validação |
| Verificação | Build + testes | + E2E gate para frontend (factory: `frontend-qa-gate.sh`) + revisão cruzada por fluxo |
| Exceção | Bypass consciente local | Bypass registrado e auditável (log + motivo) |

A regra da governança: **se o processo depende de boa vontade, não acontece**
(Aula 07). Tudo vira script, hook ou etapa de fluxo.

### Camada 3 — Workflow engine

É aqui que o AgEnFK entra como referência de implementação. O que ele resolve:

- **Itens com hierarquia e tipo** (EPIC → STORY → TASK/BUG) — o `feature_list.json`
  vira um sistema com parentesco e fluxo.
- **Flows configuráveis** — cada tipo de trabalho tem etapas com critérios de
  saída obrigatórios (Aula 13: loops com critério verificável).
- **Gatekeeper mecânico** — edição só dentro de item ativo; **DONE inalcançável
  por atalho** (só via `validate_progress` no passo final, com evidência).
- **Evidência e teste como etapas** — `log-test PASSED/FAILED` antes de concluir;
  o auto-engano da Aula 09 vira falha de fluxo.
- **Trilha auditável** — histórico de status, comentários, evidências: o "quem,
  quando, por quê" de cada item.

### Camada 4 — Observabilidade

A camada que distingue harness de processo burocrático de sistema de melhoria
contínua (Aula 11):

| Métrica | Fonte |
|---|---|
| Tempo por etapa/item | timestamps do workflow |
| Fricção (retries, loops, travadas) | `log-friction` / `log-event.sh` |
| Custo por feature | telemetria de tokens |
| Saúde do harness | `validate-harness.sh` + health check da camada 3 |
| Qualidade | testes falhando antes do green, retomadas |

Regra de ouro: **fricção não registrada é dívida de observabilidade**. Todo
atrito vira entrada de log — e cada entrada de log é um candidato a melhoria
do harness.

## O modelo multi-team

Cada equipe = um projeto com seus itens e fluxos, **no mesmo framework**:

```
Equipe Catalogo  (projeto A) ──┐
Equipe Fipe      (projeto B) ──┼──▶ AgEnFK (workflow engine compartilhado)
Equipe Finanças  (projeto C) ──┘        │
                                       ├── telemetria central
                                       └── relatório por equipe
```

Benefícios: o padrão é um só (curva de aprendizado única), a telemetria
agrega por time, e a governança escala sem reinventar.

## Scoping — o harness grande só onde você quer

O harness grande precisa de uma decisão de **escopo**: ele só deve agir nos
projetos que aderiram. A mecânica:

- o gatekeeper **verifica o caminho do arquivo** contra `.agenfk/project.json`
  e só age dentro de projetos gerenciados (fail-open fora deles);
- regras e skills são instaladas **no projeto** (`.claude/skills/`, `AGENTS.md`
  do repo), não globalmente;
- fora do projeto: agente 100% independente; dentro: workflow completo.

Foi exatamente o que fizemos neste curso ao escopar o AgEnFK para o
`harness-plannig` — a independência entre agentes na máquina não é negociável.

## Relação com o factory e o AgEnFK

| Repositório | Papel no harness grande |
|---|---|
| `webmotors-harness-factory` | Camadas 1-2: esqueleto, policies, hooks, scripts de validação |
| `agenfk` | Camadas 3-4: itens, flows, gatekeeper, evidência, telemetria, UI |
| `harness-agent-skills` | Skills compartilhadas: artefatos, QA, perf (EPIC F) |
| `harness-plannig` | O curso + este blueprint (dogfooding) |

## Próximos passos deste projeto

O harness grande completo (documentado e demonstrado) se concretiza nos pilotos
do EPIC G — quando o harness básico e o workflow engine rodarem juntos num repo
real com métricas registradas.

**Relacionados**: [Harness básico](/harness-designs/basic-harness) ·
[App Harness](/harness-designs/app-harness) · [Harnesses de domínio](/harness-designs/domain-harnesses)