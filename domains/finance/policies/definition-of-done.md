# Definition of Done — domínio Finanças

Uma entrega financeira está pronta quando:

1. **Pipeline executou de verdade** — `scripts/nightly-run.sh <area_root>` rodou (ou o item foi processado manualmente com o mesmo motor).
2. **Reconciliação feita** — totais conferidos: esperado vs. real em tabela; divergência registrada com linha citada, **nunca arredondada**.
3. **Toda fonte citada** — nenhum número sem `FONTE: <arquivo> (linhas X-Y)` (critério de saída do nightly: 0 linhas com número sem fonte).
4. **Artefato publicado** — `relatorios/YYYY-MM-DD-<slug>.md` versionado no playbook.
5. **Evidência registrada** — saída do pipeline anexada; feature em `passing`.

## O que NÃO é "pronto" no domínio
- Relatório com número sem fonte.
- Total "arredondado para bater" — divergência é dado, não bug.
- "O cron deve rodar" — sem a execução registrada de hoje.