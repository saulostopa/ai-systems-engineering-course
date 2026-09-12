# Relatório de métricas e demo final — G4

> O fechamento do projeto: todas as evidências dos pilotos, a métrica
> consolidada e o guia de demonstração ao vivo. O relatório completo está
> renderizado em **G4-FINAL-REPORT.html** (gerado pela própria skill v2 —
> dogfooding da peça de ouro).

## Números consolidados

| Métrica | Valor |
|---|---|
| EPICs entregues | 7 (A–G) |
| Stories entregues | 21, todas DONE (26/28 itens no quadro) |
| PRs | 19 (7 mergeados na develop, 12 aguardando merge em ordem) |
| Testes do motor RAG | 7/7 PASS |
| Testes do Area Copilot | 3/3 PASS |
| Testes da intranet | 3/3 PASS |
| Avaliação RAG de código | precisão@3 = 5/5 (1.0) |
| Avaliação Area Copilot | precisão = 3/3 (1.0) — ×2 (D3 + piloto G3) |
| Piloto básico (G1) | 2→4 testes, gatekeeper validado, 1 achado |
| Piloto app (G2) | gate E2E bloqueia/libera corretamente, navegação HTTP 200 |
| Piloto área (G3) | relatório noturno com 9 fontes, gate de saída PASS |
| Builds do site | vitepress OK em todas as branches |

## Evidências por piloto

| Piloto | Artefato |
|---|---|
| G1 — básico | `pilots/g1-basic-harness/evidence/G1-PILOT-REPORT.md` |
| G2 — app | `pilots/g2-app-harness/evidence/G2-PILOT-REPORT.md` |
| G3 — área | `pilots/g3-area-copilot/evidence/G3-PILOT-REPORT.md` + relatório publicado |
| G4 — final | `G4-FINAL-REPORT.html` + `DEMO.md` |

## Demo

Siga o `DEMO.md`: 6 blocos de 2-3 minutos (básico → app → área → intranet →
skills → RAG), cada um com o comando real e a frase-chave.

## Conclusão

O projeto entregou o que o plano original prometia: um curso que ensina
harness engineering **e** os harnesses funcionais para demonstrar na prática
— básico, grande, app, RAG, Area Copilot, multi-domínio, skills e intranet.
O método foi o próprio objeto: gates, evidência e métricas usados para
construir os artefatos que ensinam os gates, a evidência e as métricas.