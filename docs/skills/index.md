# Skills

O catálogo de skills do ecossistema Webmotors. Skills são pacotes de instrução
(`SKILL.md`) que o harness carrega quando a tarefa combina com a descrição —
versionados, revisáveis em PR e instaláveis em qualquer harness que leia
`SKILL.md` (Claude Code, Cursor, Codex, Gemini, OpenCode...).

| Skill | O que faz |
|-------|-----------|
| [feature-report](/skills/feature-report) | Relatório HTML autocontido do que foi entregue numa feature. |
| [feature-quiz](/skills/feature-quiz) | Quiz graduado em 4 níveis sobre a feature — a "peça de ouro". |
| [feature-flowchart](/skills/feature-flowchart) | Flowchart HTML do processo da feature. |
| [feature-animation](/skills/feature-animation) | Animação HTML de um dado atravessando a feature. |
| [qa-playwright-e2e](/skills/qa-playwright-e2e) | Testes E2E com Playwright (Python), locators semânticos. |
| [qa-perf-triage](/skills/qa-perf-triage) | Diagnóstico de regressões de latência sob carga. |
| [feature-archify](/skills/feature-archify) | Diagramas verificáveis (Archify) da feature concluída — o mapa que ensina o fluxo. |
| [skill-guard](/skills/skill-guard) | **Escaneia uma skill antes de instalar** (SkillSpector) — o gate de supply chain do catálogo. |
| [Criar uma skill nova](/skills/how-to-create) | O pipeline: ideia → SKILL.md → teste → publicação. |

::: tip Status
A evolução destas skills (design system Eleanor, acessibilidade, quiz adaptativo)
é o **EPIC F** do projeto. A página de cada skill descreve seu design atual.
:::

::: warning Antes de instalar qualquer skill de fora
Skill é instrução que o agente executa com confiança implícita — 26,1% das
skills analisadas pela NVIDIA têm vulnerabilidade e 5,2% têm sinal de intenção
maliciosa. Passe pelo gate primeiro:

```sh
harness-basic/scripts/gate-skill-scan.sh <dir-ou-url>
```

Veja [skill-guard](/skills/skill-guard).
:::