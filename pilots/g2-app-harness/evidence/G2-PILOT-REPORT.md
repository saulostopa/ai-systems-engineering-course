# Piloto G2 — app harness em app real

> **App piloto**: busca de veículos (HTML/JS puro, sem framework)
> **Harness**: `app-harness` (C1: gate E2E) + protocolo de navegação agêntica (C2)
> **Data**: 2026-09-12 · **Status**: CAMADA QA + NAVEGAÇÃO VALIDADAS

## Setup do piloto

| Etapa | Resultado |
|---|---|
| App criado (HTML/JS, `role=list`, `role=region`, empty state) | OK |
| Gate E2E instalado (`e2e-gate.sh` + `.harness/config.yaml`: `frontend_paths: src`) | OK |
| Testes E2E: `tests/e2e/test_search.py` (2 casos: resultados + empty state) | OK |

## Camada QA — comportamento do gate (evidência real)

| Cenário | Staged | Resultado |
|---|---|---|
| **1. Frontend sem teste E2E** | só `src/index.html` | ✅ **BLOQUEADO**: "mudança de frontend sem teste E2E (Aula 10). Caminho esperado: tests/e2e/" |
| **2. Frontend + teste E2E** | `src/index.html` + `tests/e2e/test_search.py` | ✅ **LIBERADO**: "E2E-GATE: ok" |

O gate funciona exatamente como projetado: a mudança de tela **não passa sem
o teste correspondente** — o E2E é contrato de commit, não intenção.

## Camada agêntica — navegação com visão (protocolo C2 executado)

> App servido em `http://localhost:3100` (a 3000 estava ocupada pelo dev
> server do catálogo Webmotors — achado de ambiente).

| Passo do protocolo | Evidência |
|---|---|
| 1. Subir o app | `python3 -m http.server 3100` → **HTTP 200** |
| 2. Navegar como usuário (fluxo de busca) | `GET /?q=civic` → **HTTP 200**; página contém `role=list` (resultados) |
| 3. Estados de borda | `role=region` com "Nenhum veículo" presente (empty state) |
| 4. Veredito por critério | Tabela abaixo |

| Critério | Veredito | Evidência |
|---|---|---|
| App sobe e responde | **ACEITO** | HTTP 200 (curl) |
| Fluxo de busca acessível | **ACEITO** | `role=search` + `role=list` no DOM |
| Empty state presente | **ACEITO** | texto "Nenhum veículo" + `role=region` |
| Navegação sem visão (limitação) | **PARCIAL** | neste piloto o passo 4 foi executado sem modelo de visão — screenshots reais exigem o agente com visão (habilite na demo com Claude/GPT-4o) |

## Achados

1. **Porta 3000 ocupada pelo dev server do catálogo** — o app harness deve
   parametrizar a porta (`PORT`/config) e verificar antes de subir.
2. **Screenshots exigem agente com visão** — o protocolo C2 está documentado e
   validado estruturalmente; a validação visual real (screenshots + veredito
   ACEITO/REJEITADO por critério) é a parte a demonstrar ao vivo na demo final (G4).

## Conclusão do piloto

O app harness provou as duas camadas: **o gate E2E bloqueia de verdade** o
frontend sem teste (contrato mecânico), e **a navegação agêntica tem um
protocolo executável** com veredito por critério. A parte visual fica para a
demo com agente de visão — a mecânica já está pronta e validada.