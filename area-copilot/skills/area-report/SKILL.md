---
name: area-report
description: Gera o relatório HTML da área com fontes citadas — consome o Area Copilot (contexto de negócio), sintetiza o artefato e anexa FONTE para cada número. Use quando o usuário pedir um relatório, resumo ou análise baseado em planilhas/documentos da área.
---

# Relatório da área com fontes citadas

Produza o artefato da área (relatório, resumo de reunião, análise de metas)
**com cada número rastreável a uma fonte**. Número sem fonte é proibido.

## Gather

1. Consulte o contexto: `python -m area_harness query area_context "<pergunta da área>"`.
2. Abra o arquivo apontado pela FONTE (a linha exata) — confirme o número antes de citar.
3. Leia o `feature_list.json` da área se o relatório envolver estado de features.

## Write

- Cada número do relatório vem com `FONTE: <caminho> (linhas X-Y)` logo abaixo.
- Sem o chunk de origem lido, o dado não entra no relatório.
- Formato: HTML autocontido (mesma base visual do `feature-report`), tabelas para dados tabulares.

## Output

- Salve em `relatorios/YYYY-MM-DD-<slug>.html` e abra.
- Se o contexto da área não respondeu: diga exatamente o que falta (arquivo, aba, linha) — não complete com estimativa.