---
name: spreadsheet-analysis
description: Analisa planilhas (CSV/XLSX) com validação de totais, detecção de dados faltantes e resumo com fontes citadas. Use quando o usuário pedir análise, reconciliação ou resumo de planilha/dados tabulares.
---

# Análise de planilha com fontes

Consome o motor do Area Copilot (rag_harness): o contexto da planilha vem com
`FONTE: <arquivo> (linhas X-Y)` — número sem fonte é proibido (regra do domínio).

## Gather

1. Indexe o contexto: `python3 -m area_harness index <area_root> --verbose` (ou confirme que o índice existe).
2. Consulte: `python3 -m area_harness query <area_root> "<pergunta da análise>"`.
3. Abra o arquivo apontado pela FONTE e confirme o número na linha exata antes de citar.

## Write

- **Validação de totais**: some a coluna da fonte e compare com o total declarado — esperado vs. real em tabela.
- **Dados faltantes**: conte células vazias por coluna e reporte com a linha.
- **Outliers**: valores além de ±3 desvios da média da coluna — cite a linha de cada um.
- Cada número do resumo acompanha `FONTE: <caminho> (linhas X-Y)`.

## Output

- Resumo em Markdown pronto para o relatório (ou HTML via feature-report).
- Se a reconciliação falhou (totais não batem): o relatório sai com **status RECONCILIAÇÃO FALHOU** e a lista de divergências com linhas — nunca "arredondado para bater".