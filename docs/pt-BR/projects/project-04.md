---
title: Projeto 04 — Harness de domínio
---

# Projeto 04 — Harness de domínio

> O mesmo esqueleto do harness, skill packs por área: games, finanças ou comercial. Escolha o seu.

## Objetivo

Construir um **playbook de domínio**: o harness básico (Projeto 02) + o pacote de skills e políticas **do seu domínio**. É a essência do modelo multi-team (EPIC E): o esqueleto não muda; o conhecimento muda.

## A receita universal

```
harness de domínio = harness básico (Projeto 02)
                   + skills do domínio (SKILL.md sob demanda)
                   + verificação do domínio (gates próprios)
                   + artefatos do domínio (o que se entrega)
```

## Três domínios para escolher

### 🎮 Games (ex.: criação de jogo até a publicação no Roblox)

| Peça | Conteúdo |
|---|---|
| Skills | `game-design` (persona, narrativa, storytelling), `asset-pipeline`, `roblox-publish` (Luau, Rojo, validação de plataforma) |
| Feature list | Personagens, mecânicas, narrativas — cada uma com estado |
| Verificação | Playteste simulado: gerar variações → simular → medir → iterar; validação de config de monetização antes do publish |
| Artefato | Design doc HTML da feature (via `feature-report`), playtest report |

### 💰 Finanças (ex.: análise de planilhas)

| Peça | Conteúdo |
|---|---|
| Skills | `spreadsheet-analysis` (pandas/openpyxl), `reconciliation` (esperado vs. real), `report-generation` |
| Feature list | Relatórios a gerar — fonte, prazo, estado |
| Verificação | Validação de fórmulas, conferência de totais, guarda contra dados faltantes |
| Artefato | Relatório HTML publicado (madrugada → café) |

### 📈 Comercial (ex.: apresentações e propostas)

| Peça | Conteúdo |
|---|---|
| Skills | `deck-generation`, `proposal-draft` (briefing + contexto de CRM), `sales-review` |
| Feature list | Entregas de proposta/deck — cliente, data, aprovação |
| Verificação | Check contra requisitos do briefing; revisão cruzada antes do envio |
| Artefato | Deck/proposta versionada + report da feature |

## Passo a passo

### 1. Defina o domínio e a feature list

Escolha UM domínio. Liste 3-5 features reais com estado (Aula 08).

### 2. Escreva 2-3 skills do domínio

Cada skill é um `SKILL.md` com frontmatter (`name`, `description`) e corpo `Gather → Write → Output` (veja [criar uma skill nova](/pt-BR/skills/how-to-create)). Exemplo mínimo:

```markdown
---
name: spreadsheet-analysis
description: Analisa planilhas (Excel/CSV) com pandas: valida totais, detecta
  dados faltantes e gera resumo. Use quando o usuário pedir análise de planilha.
---

# Análise de planilha

## Gather
- Leia o arquivo; liste colunas, tipos e totais.

## Write
- Valide: totais batem? dados faltantes? outliers?

## Output
- Resumo com esperado vs. real + evidência (linhas de output).
```

### 3. Defina a verificação do domínio

O que significa "pronto" **no seu domínio**? (Games: publish validado; Finanças: relatório reconciliado; Comercial: proposta aprovada pelo review.) Escreva no `definition-of-done.md` do domínio.

### 4. Rode uma feature de ponta a ponta

Da feature list até o artefato, com evidência registrada — igual ao Projeto 02, agora com as skills do domínio carregando sob demanda.

## Verificação

- O mesmo esqueleto do Projeto 02, zero alterações de processo.
- As skills do domínio foram acionadas **por demanda** (descrição combinando com a tarefa), não todas no boot.
- O artefato do domínio foi produzido e versionado.

## Entregável

Seu playbook de domínio versionado: esqueleto + skills + verificação + 1 artefato de exemplo.

::: tip Status
Os playbooks oficiais (Games com Roblox, Finanças com execução noturna, Comercial com CRM) são o **EPIC E** do curso.
:::

**Próximo projeto**: [05 — Area Copilot com RAG](/pt-BR/projects/project-05).