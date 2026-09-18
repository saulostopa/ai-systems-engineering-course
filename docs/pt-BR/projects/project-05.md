---
title: Projeto 05 — Area Copilot com RAG
---

# Projeto 05 — Area Copilot com RAG

> O harness que dá contexto da sua área ao agente: planilhas, documentos, imagens e dados — para times não-técnicos gerenciarem features com IA.

## Objetivo

Montar um **Area Copilot**: um harness onde pessoas de qualquer área (finanças, comercial, operação, games) guardam o contexto do próprio trabalho — arquivos de negócio, planilhas, imagens, dados — e usam um agente com **recuperação (RAG)** para gerenciar features e produzir artefatos.

É a Story **D3** do curso (RAG de negócio) em versão prática.

## O que é diferente de tudo até aqui

Nos projetos anteriores, o contexto era **código** (repo, AGENTS.md, testes). Aqui o contexto é **conhecimento da área**:

- planilhas de precificação, metas, histórico;
- documentos de briefing, regras de negócio;
- imagens (prints de tela, anúncios, peças);
- dados exportados (CSV, JSON).

O agente precisa achar o contexto certo **quando a tarefa pede** — é isso que o RAG resolve.

## Arquitetura mínima (sem banco, começando)

Você não precisa de pgvector no primeiro dia. A versão mínima é **RAG por convenção**:

```
area-context/                    # a "memória" da área (versionada!)
├── planilhas/                   # fontes de dados
├── documentos/                  # briefings, regras
├── imagens/                     # evidência visual
└── index.md                     # mapa: o que existe e onde
```

E o `index.md` é o truque: um **índice semântico escrito pelo agente** que mapeia cada contexto com tags e resumos. O agente lê o índice (barato) e abre só o arquivo que a tarefa pede (caro sob demanda) — o mesmo padrão roteador da Aula 04.

## Passo a passo

### 1. Monte a pasta `area-context`

Coloque 5-10 arquivos reais da sua área (mesmo que anonimizados). Anonimize antes — o repo é versionado.

### 2. Gere o `index.md`

Peça ao agente:

```
"gera um índice da pasta area-context: para cada arquivo, tags, resumo em 1
linha e quando vale a pena abrir. Salva em area-context/index.md"
```

### 3. Escreva o `AGENTS.md` da área

```markdown
# AGENTS.md — Harness da área de [nome]

## 1. Como trabalhar
- Antes de qualquer tarefa, leia area-context/index.md.
- Contexto específico? Abra o arquivo apontado pelo índice (não adivinhe).
- Nunca invente número: todo dado citado vem de um arquivo lido.

## 2. Como verificar
- Todo artefato cita a fonte (arquivo + linha/aba quando aplicável).
- "Não sei" é resposta válida; número inventado não é.

## 3. Estado
- As features da área vivem em feature_list.json.
```

### 4. Rode uma feature da área

Exemplo finanças: *"analisa a planilha de metas do mês passado e gera o resumo para a reunião"*. O agente deve: consultar o índice → abrir a planilha → validar → gerar o artefato com fontes citadas.

### 5. (Opcional) Evolua para RAG real

Quando o volume crescer, migre o índice manual para **RAG híbrido** (vetores + busca textual) — a arquitetura está no `rag-harness.md` do `webmotors-harness-factory`: chunking por estrutura, pgvector + full-text com fusão RRF, e recuperação agêntica (o agente decide qual ferramenta de busca usar). O gatilho para migrar: o índice manual começou a falhar (Aula 11 — decida por evidência).

## Verificação

- Uma tarefa da área é concluída com **todas as fontes citadas** e nenhum número inventado.
- Um contexto novo (arquivo adicionado) aparece no índice após regerá-lo.
- Você consegue responder: "onde o agente achou isso?" para qualquer afirmação do artefato.

## Entregável

O `area-context/` + `index.md` + `AGENTS.md` da área versionados + 1 artefato de exemplo com fontes citadas.

::: tip Status
A versão com banco de vetores, OCR de imagens e execução agendada é o **EPIC D** do curso.
:::

**Você terminou os projetos!** Revise as [Aulas](/pt-BR/lectures/) ou explore os [Designs de Harnesses](/pt-BR/harness-designs/) para ver onde cada peça se encaixa no plano completo.