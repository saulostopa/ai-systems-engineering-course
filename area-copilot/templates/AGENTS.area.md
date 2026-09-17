# AGENTS.md — Harness da área (template Area Copilot)

> Copie para a raiz da área. Regra de ouro: **número sem fonte é proibido**.

## 1. Como trabalhar

- Antes de qualquer tarefa, leia `area_context/index.md` (o mapa da área).
- Contexto específico? Use o Area Copilot (`python -m area_harness query area_context "<pergunta>"`) ou abra o arquivo apontado pelo índice — **nunca adivinhe**.
- Todo dado citado vem de um arquivo lido: planilha, documento ou imagem.

## 2. Como verificar

- Todo artefato cita a fonte: `FONTE: <caminho> (linhas X-Y)`.
- "Não sei" é resposta válida; **número inventado não é**.
- Nenhum número sai sem o chunk de origem anexado.

## 3. Estado

- As features da área vivem em `feature_list.json` (uma `in_progress` por vez).
- Relatórios agendados (modo madrugada) publicam em `relatorios/` com data no nome.

## 4. Onde mora o contexto

| Pasta | O que contém |
|---|---|
| `area_context/planilhas/` | Dados tabulares (CSV/XLSX) |
| `area_context/documentos/` | Briefings, regras, processos |
| `area_context/imagens/` | Evidência visual (prints, peças) |
| `area_context/index.md` | Mapa da área (tags + resumos) — regenere quando adicionar arquivos |