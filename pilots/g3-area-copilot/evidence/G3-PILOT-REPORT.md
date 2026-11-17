# Pilot G3 — Area Copilot in a real area (finance)

> **Pilot area**: finance (2026 goals by region, prices, pricing rules)
> **Harness**: `area-copilot` (D3) + playbook `domains/finance` (E3)
> **Date**: 2026-09-12 · **Status**: AREA OPERATIONAL — report published with sources

## Area context (real data created for the pilot)

```
area-financas/
├── planilhas/
│   ├── metas_2026.csv   (2 regions x 7 months: meta_vendas, veiculos_vendidos)
│   └── precos.csv       (FIPE price + used discount per model)
└── documentos/
    ├── precificacao.md  (rules: 8% used cars, 3% >100k km, +15% half-year goal)
    └── briefing-q3.md   (closing meeting agenda)
```

## What was executed (real evidence)

| Step | Command | Result |
|---|---|---|
| Indexing | `area_harness index` | 7 business chunks |
| Nightly pipeline | `domains/finance/scripts/nightly-run.sh` with 3 questions | **report published: 9 sources cited**, output gate approved |
| Evaluation | `area_harness eval` (3 real queries) | **Precision 3/3 = 1.0** |
| Query | `area_harness query` | answers with `FONTE: <file> (lines X-Y)` |

## The overnight report (published)

`evidence/2026-09-12-resumo.md` — the artifact the team finds in the morning:
each question answered with the cited source (spreadsheet + lines), the
pipeline recorded in the header, and the "no number outside a FONTE block"
gate applied (awk per block). **The harness worked on its own; the evidence
is what was left behind.**

## Area metrics

| Metric | Value |
|---|---|
| Chunks indexed | 7 (CSV per line block + MD per section) |
| Sources cited in the report | 9 |
| Retrieval precision | 3/3 (1.0) — July goal, used-car rule, growth goal |
| Nightly output criterion | PASS (0 numbers outside a FONTE block) |
| Friction recorded | 0 (no log-event needed) |

## Pilot conclusion

The scenario the user described in the original plan **worked end to end**: the
area harness ran the pipeline, validated the sources, and published the
report — the finance team finds the artifact ready in the morning, with every
number traceable to the spreadsheet. The area became an **operational Area
Copilot**: the natural next step is plugging in real data and scheduling the
cron.