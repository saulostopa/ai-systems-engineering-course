---
title: Harnesses de domínio (multi-team)
---

# Harnesses de domínio (multi-team)

> Um esqueleto, N playbooks. O harness não muda entre domínios — só o
> conhecimento (skills) e a verificação específica. Games, finanças,
> comercial e o que vier depois.

## O princípio (EPIC E)

O harness de domínio é a aplicação do modelo multi-team:

```
harness de domínio = esqueleto multi-domínio (E1)
                   + skills do domínio (E2/E3/E4, SKILL.md sob demanda)
                   + feature list do domínio
                   + verificação própria (definition-of-done do domínio)
                   + artefatos com fonte citada (skills de artefato)
```

O esqueleto é **idêntico** para todos — é isso que permite uma única curva de
aprendizado e uma única governança (EPIC B2) para áreas completamente
diferentes.

## A fábrica (E1 — `domains/factory/new-playbook.sh`)

Gera o esqueleto de um playbook novo em segundos:

```sh
./domains/factory/new-playbook.sh <dominio>
domains/<dominio>/
├── AGENTS.md                  # roteador do domínio (processo = mesmo de todos)
├── feature_list.json          # entregas do domínio com estado
├── policies/                  # escopo, DoD, evidência
├── skills/                    # preenchido pelo domínio (E2/E3/E4)
└── scripts/validate-playbook.sh  # saúde do playbook (Aula 11)
```

O `validate-playbook.sh` exige estrutura obrigatória + **pelo menos uma skill**
+ JSON válido com no máximo 1 feature `in_progress`. Um playbook sem skills é
um playbook quebrado — conhecimento é o que diferencia domínios, não processo.

## Os playbooks entregues

| Domínio | Skills | Verificação própria | Artefato |
|---|---|---|---|
| [Games](/pt-BR/harness-designs/domain-harnesses) (E2) | game-design, roblox-publish | playteste simulado + validação de publish | design doc da feature |
| [Finanças](/pt-BR/harness-designs/domain-harnesses) (E3) | spreadsheet-analysis, report-generation | reconciliação esperado vs. real | relatório publicado (madrugada) |
| [Comercial](/pt-BR/harness-designs/domain-harnesses) (E4) | deck-generation, proposal-workflow | check contra briefing + revisão cruzada | deck/proposta versionada |

## Regra de ouro compartilhada

Do Area Copilot (D3) para todos os domínios: **todo artefato cita a fonte**.
Um número de relatório sem `FONTE: <arquivo> (linhas X-Y)` não existe. O
playbook é o mesmo — a honestidade com o dado também.

## Como criar um domínio novo (receita)

1. `./domains/factory/new-playbook.sh <nome>` — esqueleto pronto.
2. Escreva 2-3 skills em `skills/<nome>/SKILL.md` (frontmatter + Gather/Write/Output).
3. Preencha `feature_list.json` com as entregas reais do domínio.
4. Defina o "pronto" do domínio em `policies/definition-of-done.md`.
5. `scripts/validate-playbook.sh` — deve terminar com `PLAYBOOK OK`.

**Relacionados**: [Harness grande](/pt-BR/harness-designs/enterprise-harness) · [RAG Harness](/pt-BR/harness-designs/rag-harness) · [Projeto 04](/pt-BR/projects/project-04)