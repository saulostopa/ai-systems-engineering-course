---
title: RAG Harness & Area Copilots
---

# RAG Harness & Area Copilots

> Contexto para o agente — de código e de negócio. O padrão validado na POC
> (D1), o RAG de código (D2) e o contexto das áreas (D3).

## O padrão (validado pela POC em `rag-harness/`)

```
recuperação agêntica:  glob → léxico → semântica → suficiente? → responde
                            │            │            │
chunking AST-aware    cache por content-hash   RRF (léxico + semântica)
(unidade completa)    (re-embed só o que mudou)   numa lista só
```

### As três idéias que a POC provou (D1)

1. **Chunking por estrutura, não por tamanho** — cada chunk é uma função/classe
   completa (stdlib `ast` para Python; fallback por linhas). A busca nunca
   retorna código cortado no meio.
2. **Embeddings como cache de computação** — content-hash por arquivo; a segunda
   indexação não re-embed nada que não mudou (teste coberto).
3. **Híbrido com RRF** — a busca léxica (nomes exatos de símbolos) e a semântica
   (conceitos) se fundem numa lista única com Reciprocal Rank Fusion — o
   resultado de "definition of done" acha o `definition-of-done.md`, e o de
   "gatekeeper pre-commit" acha o `gatekeeper.sh`.

### O controlador agêntico

`AgentController.retrieve()` decide a ferramenta por custo: **barato primeiro**
(léxico/glob), **semântica por último** (a mais cara), e para quando a
suficiência é atingida (top resultado contém termo chave). É o "agente de
recuperação" do rag-harness.md — sem despejar tudo no prompt. Ponto de
extensão para decisão via LLM: `decide_with_llm()`.

### Decisão da POC (leia o `POC_REPORT.md` completo)

- ✅ **Arquitetura adotada** — portável para pgvector sem redesenho.
- ❌ **Infra pesada adiada** (watcher/fila/pgvector) — só com evidência do
  EPIC G. A POC roda sem infra: indexação sob demanda.
- ⚖️ **Prioridade invertida**: RAG de negócio (D3) tem mais ROI imediato que o
  watcher.

## D2 — RAG de código (em `rag-harness/`)

Indexação de repos de código com o padrão acima. **Melhorias funcionais do D2
(validadas por avaliação):**

| Melhoria | Por quê | Como |
|---|---|---|
| Índexa `.sh/.yaml/.json` | Scripts e configs são código | `discover_files` com exts ampliadas |
| Normalização de acentos | `fricção` ≠ `friccao` | `unicodedata` no tokenizer |
| Split de camelCase | `hooksPath` vira `hooks path` | regex no tokenizer |
| Boost por nome de arquivo | `install.sh` responde por "instalador" | tokens do path valem 2x |
| Prefix match mútuo | pt-BR ↔ en (`definicao`→`definition`) | `_prefix_match` (min 5 chars) |
| Regex de símbolo exato | `models.Veiculo`, quoted, snake_case | `AgentController._exact_symbol_patterns` |

**Métrica (evidência, Aula 11)**: precisão@3 = **5/5 = 1.0** nas 5 queries do
`tests/queries.json` contra o `harness-basic` — incluindo "instalador que ativa
core.hooksPath" → `install.sh` (via nome de arquivo) e "como registrar friccao"
→ `log-event.sh` (via acentos + nome de arquivo).

```sh
cd rag-harness
python tests/test_rag.py                       # 7 testes
python -m rag_harness eval ../harness-basic    # precisão@k (métrica de saúde)
python -m rag_harness agent ../harness-basic "como o gatekeeper bloqueia commit"
# semântica real (opcional, com Ollama):
OLLAMA_API_URL=http://localhost:11434 python -m rag_harness index ../harness-basic
```

## D3 — Area Copilot (contexto de negócio)

O mesmo motor, o domínio das áreas: planilhas, documentos, imagens, dados.
O padrão por convenção (índice + fontes) está no
[Projeto 05](/projects/project-05); o motor híbrido deste EPIC substitui o
índice manual quando o volume cresce:

| Peça | Negócio |
|---|---|
| Chunker | por arquivo/aba/planilha (CSV/stdlib; openpyxl opcional) |
| Índice | `area-context/index.md` (por convenção) → `rag_harness` (por volume) |
| Verificação | artefato cita a fonte (arquivo + linha/aba) — nunca número inventado |
| Skill | `area-report` (o artefato da área com fontes citadas) |

## O que NÃO é (limites honestos)

- A POC com NGramEmbedder valida **arquitetura**, não semântica — semântica
  real exige Ollama/API de embeddings (ligue `OLLAMA_API_URL`).
- O RAG não substitui os agentes nativos (grep/glob já existem) — o valor
  agregado está no **contexto de negócio** e na **qualidade de chunking** em
  repos grandes.
- Infra pesada (watcher, pgvector, fila) fica para quando a evidência pedir —
  a regra do `rag-harness.md` continua valendo: **não construa antes da dor
  registrada**.

**Relacionados**: [Projeto 05](/projects/project-05) · [Harnesses de domínio](/harness-designs/domain-harnesses)