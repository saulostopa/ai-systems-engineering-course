# Criar uma skill nova

O pipeline de uma skill: **ideia → SKILL.md → teste → publicação**.

1. **Ideia** — veja `ideas/BACKLOG.md` do `harness-agent-skills` antes de começar; sua ideia pode já estar proposta.
2. **SKILL.md** — frontmatter só com `name` e `description`; o corpo em `Gather → Write → Output` (o padrão validado por `feature-report` e `explain`).
3. **Teste** — carregue a skill num harness real (Claude Code, OpenCode) e execute o caso de uso de ponta a ponta.
4. **Publicação** — PR no `harness-agent-skills`; depois de aprovada, vira uma pasta na raiz, no mesmo formato das demais.

E o caminho inverso — **instalar** uma skill que veio de fora:

```sh
harness-basic/scripts/gate-skill-scan.sh <dir-ou-url-do-repo>
```

Escaneie **antes de baixar** e registre o veredito no `skills-lock.json`.
Veja [skill-guard](/skills/skill-guard).

::: tip Regra de ouro
"Build mechanically, don't re-type" — a skill deve montar os artefatos a partir
do que foi lido/verificado, nunca recriar conteúdo de memória.
:::