# Piloto G1 — harness básico em repo real

> **Repo piloto**: `pricing-cli` (calculadora de preço FIPE simplificada, Python)
> **Harness**: `harness-basic` (B1) instalado via `install.sh`
> **Data**: 2026-09-12 · **Status**: FEATURE ENTREGUE COM EVIDÊNCIA

## Setup do piloto

| Etapa | Comando | Resultado |
|---|---|---|
| Repo criado | `git init + pricing.py + 2 testes` | baseline com 2 testes verdes |
| Harness instalado | `install.sh <repo>` | templates + scripts + hooks; `core.hooksPath=.githooks` |
| Feature declarada | `feature_list.json f1: in_progress` | commit liberado (gatekeeper: OK, 1 feature) |
| Implementação | `pricing.py` + 2 testes novos | **4 testes verdes** (2→4, sem redução) |
| Validação | `./scripts/validate-harness.sh` | **HARNESS OK — 0 falhas, 0 avisos** |
| Conclusão | `f1: passing` | evidência registrada |

## Comportamento dos gates (evidência real)

| Cenário | Resultado observado |
|---|---|
| Commit com 1 feature `in_progress` | ✅ liberado |
| Commit com 0 features | ✅ **BLOQUEADO** ("nenhuma feature in_progress — declare a feature") |
| Mudança de frontend sem E2E | (n/a — repo Python; gate E2E é do app harness, G2) |
| Update da própria `feature_list.json` com 0 in_progress | ✅ **BLOQUEADO** — achado real (ver abaixo) |
| `validate-harness.sh` antes do push | ✅ HARNESS OK |

## Métricas (baseline vs. harness)

| Métrica | Valor |
|---|---|
| Testes antes | 2 |
| Testes depois | 4 (+2 para a feature, nenhum enfraquecido) |
| Commits da feature | 3 (declara → implementa → passing) |
| Bloqueios do gatekeeper | 2 (ambos corretos; 1 com achado) |
| Evidência registrada | build/teste (unittest OK), validate-harness OK |

## Achado real (vira melhoria do harness)

**O gatekeeper bloqueia até a atualização da `feature_list.json`** quando
nenhuma feature está `in_progress` — o que impede a própria transição para
`passing`. Mitigação atual: bypass consciente (`.harness/skip-gatekeeper`,
5 min). Melhoria recomendada para o harness: o gatekeeper deveria **permitir
commits que tocam apenas `feature_list.json`/`policies/`** (mudança de estado
não é mudança de código) — item para a evolução do B1.

## Conclusão do piloto

O harness básico entregou exatamente o que o curso ensina: **uma feature de
ponta a ponta com evidência, gates mecânicos reais e um achado de melhoria
concreto** — a prova de que o harness funciona e de que ele próprio é um
produto em evolução (Aula 11: observabilidade alimenta melhoria).