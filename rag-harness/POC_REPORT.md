# POC do RAG híbrido — decisão (D1)

> Status: **POC validada**. Reabre a proposta do `rag-harness.md` (webmotors-harness-factory)
> com uma implementação mínima e funcional. O que ficou validado, o que ficou
> de fora e por quê — decida por evidência (Aula 11), não por intuição.

## O que foi construído

```
rag-harness/
├── rag_harness/
│   ├── chunker.py      # chunking AST-aware (stdlib ast) — funções/classes completas
│   ├── embeddings.py   # NGramEmbedder (local, determinístico) OU Ollama (nomic-embed-text)
│   ├── indexer.py      # cache por content-hash: re-embed só o que mudou
│   ├── retrieval.py    # léxico (BM25-ish) + semântico (coseno) + RRF
│   ├── agentic.py      # Agent Controller: glob→léxico→semântica, suficiente? decide
│   └── __main__.py     # CLI: index / query / hybrid / agent
└── tests/test_rag.py   # 5 testes (pytest ou python direto)
```

## O que a POC validou (vs. o rag-harness.md)

| Idéia do rag-harness.md | Status na POC | Evidência |
|---|---|---|
| Chunking por AST (unidade completa) | ✅ validado | `test_chunk_python_extrai_funcoes_e_classes` — toda função/ classe é um chunk íntegro |
| Embeddings como cache de computação (content-hash) | ✅ validado | `indexer.py` re-usa vetores de chunks inalterados; 2ª indexação não re-embed |
| Híbrido léxico+semântico com RRF | ✅ validado | `rrf_merge` + `hybrid_search`; teste cobre a fusão |
| Recuperação agêntica (ferramentas + suficiência) | ✅ validado | `AgentController.retrieve` — barato primeiro, escala sob demanda |
| Sem provider hardcoded | ✅ validado | `make_embedder()`: Ollama se alcançável, senão NGram local |

## O que ficou DE FORA (intencional) — e por quê

| Peça do rag-harness.md | Fora da POC | Motivo |
|---|---|---|
| File watcher (Rust/Go, inotify) | Sim | POC roda indexação sob demanda; watcher é otimização de escala, não de validade |
| Fila (LISTEN/NOTIFY, Redis) | Sim | Sem workers concorrentes na POC — não há o que enfileirar |
| Postgres + pgvector | Sim | SQLite/JSON serve para validar o *padrão*; pgvector resolve volume |
| OCR de imagens | Sim | D3 (Area Copilot) cobre negócio; OCR é item separado |
| Decisão de ferramenta via LLM | Parcial | `decide_with_llm` é o ponto de extensão; a heurística já decide bem na POC |

## Condições de reabertura (do rag-harness.md) — revisitadas

1. **Harness em uso real em código grande** — ❌ ainda não (pilotos no EPIC G).
2. **Fricção real de recuperação registrada** — ⚠️ parcial: a POC mede a *qualidade*
   de recuperação (pode-se medir precisão@k), mas o custo-benefício de *adotar*
   depende do EPIC G.
3. **Agentes em uso não resolvem nativamente** — ⚠️ a decidir: os agentes modernos
   já trazem glob/grep nativos; a POC mostra que o valor agregado do RAG híbrido
   está no **contexto de negócio** (D3) e na **qualidade do chunking** para grandes
   repos, não na busca de código simples.

## Decisão

- **Adotar a arquitetura**: sim, como base de código do RAG — o padrão
  (AST chunks + cache hash + RRF + agência) está validado e é portável para
  pgvector sem redesenho.
- **Adotar em produção (watcher+pg)**: **não ainda** — aguardar evidência do
  EPIC G (condição 1-2). A POC já roda sem infra: indexação sob demanda.
- **Prioridade de valor**: inverter a ordem do plano — o **RAG de negócio (D3)**
  tem mais ROI imediato que o watcher; a infra pesada só quando o volume pedir.

## Como rodar

```sh
cd rag-harness
python tests/test_rag.py                    # testes (stdlib)
python -m rag_harness index ../harness-basic --verbose
python -m rag_harness hybrid ../harness-basic "gatekeeper pre-commit"
python -m rag_harness agent ../harness-basic "como validar o harness"
# com Ollama (semântica real):
OLLAMA_API_URL=http://localhost:11434 python -m rag_harness index ../harness-basic
```