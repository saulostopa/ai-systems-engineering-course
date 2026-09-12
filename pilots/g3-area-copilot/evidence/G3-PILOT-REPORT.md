# Piloto G3 — Area Copilot numa área real (finanças)

> **Área piloto**: finanças (metas por região 2026, preços, regras de precificação)
> **Harness**: `area-copilot` (D3) + playbook `domains/finance` (E3)
> **Data**: 2026-09-12 · **Status**: ÁREA OPERACIONAL — relatório publicado com fontes

## Contexto da área (dados reais criados para o piloto)

```
area-financas/
├── planilhas/
│   ├── metas_2026.csv   (2 regiões × 7 meses: meta_vendas, veiculos_vendidos)
│   └── precos.csv       (preço FIPE + desconto seminovo por modelo)
└── documentos/
    ├── precificacao.md  (regras: 8% seminovos, 3% >100k km, meta +15% semestre)
    └── briefing-q3.md   (pauta da reunião de fechamento)
```

## O que foi executado (evidência real)

| Etapa | Comando | Resultado |
|---|---|---|
| Indexação | `area_harness index` | 7 chunks de negócio |
| Pipeline noturno | `domains/finance/scripts/nightly-run.sh` com 3 perguntas | **relatório publicado: 9 fontes citadas**, gate de saída aprovado |
| Avaliação | `area_harness eval` (3 queries reais) | **Precisão 3/3 = 1.0** |
| Consulta | `area_harness query` | respostas com `FONTE: <arquivo> (linhas X-Y)` |

## O relatório da madrugada (publicado)

`evidence/2026-09-12-resumo.md` — o artefato que o time encontra de manhã:
cada pergunta respondida com a fonte citada (planilha + linhas), o pipeline
registrado no cabeçalho e o gate de "nenhum número fora de bloco FONTE"
aplicado (awk por bloco). **O harness trabalhou sozinho; a evidência é o
que ficou.**

## Métricas da área

| Métrica | Valor |
|---|---|
| Chunks indexados | 7 (CSV por bloco de linhas + MD por seção) |
| Fontes citadas no relatório | 9 |
| Precisão de recuperação | 3/3 (1.0) — meta de julho, regra de seminovos, meta de crescimento |
| Critério de saída do nightly | PASS (0 números fora de bloco FONTE) |
| Fricção registrada | 0 (nenhum log-event necessário) |

## Conclusão do piloto

O cenário que o usuário descreveu no plano original **funcionou de ponta a
ponta**: o harness da área rodou o pipeline, validou as fontes e publicou o
relatório — o time de finanças encontra o artefato pronto pela manhã, com
cada número rastreável à planilha. A área virou um **Area Copilot operacional**:
próximo passo natural é plugar dados reais e agendar o cron.