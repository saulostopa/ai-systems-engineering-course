---
title: RAG Harness & Area Copilots
---

# RAG Harness & Area Copilots

> Context for the agent — code and business. The pattern validated in the POC
> (D1), the code RAG (D2) and the areas' context (D3).

## The pattern (validated by the POC in `rag-harness/`)

```
agentic retrieval:  glob → lexical → semantic → enough? → answer
                            │            │            │
AST-aware chunking    content-hash cache    RRF (lexical + semantic)
(complete unit)       (re-embed only what changed)  into a single list
```

### The three ideas the POC proved (D1)

1. **Structure-based chunking, not size-based** — each chunk is a complete function/class
   (stdlib `ast` for Python; line-based fallback). The search never
   returns code cut in the middle.
2. **Embeddings as a computation cache** — content-hash per file; the second
   indexing pass re-embeds nothing that didn't change (covered by test).
3. **Hybrid with RRF** — lexical search (exact symbol names) and semantic
   (concepts) merge into a single list with Reciprocal Rank Fusion — the
   result for "definition of done" finds `definition-of-done.md`, and the one for
   "gatekeeper pre-commit" finds `gatekeeper.sh`.

### The agentic controller

`AgentController.retrieve()` decides the tool by cost: **cheap first**
(lexical/glob), **semantic last** (the most expensive), and stops when
sufficiency is reached (top result contains a key term). It is the
"retrieval agent" of rag-harness.md — without dumping everything into the prompt. Extension
point for LLM-based decisions: `decide_with_llm()`.

### The POC decision (read the full `POC_REPORT.md`)

- ✅ **Architecture adopted** — portable to pgvector without redesign.
- ❌ **Heavy infra postponed** (watcher/queue/pgvector) — only with evidence from
  EPIC G. The POC runs without infra: on-demand indexing.
- ⚖️ **Priority inverted**: business RAG (D3) has more immediate ROI than the
  watcher.

## D2 — Code RAG (in `rag-harness/`)

Indexing code repos with the pattern above. **D2 functional improvements
(validated by evaluation):**

| Improvement | Why | How |
|---|---|---|
| Indexes `.sh/.yaml/.json` | Scripts and configs are code | `discover_files` with extended exts |
| Accent normalization | `fricção` ≠ `friccao` | `unicodedata` in the tokenizer |
| camelCase splitting | `hooksPath` becomes `hooks path` | regex in the tokenizer |
| File-name boost | `install.sh` answers for "installer" | path tokens count 2x |
| Mutual prefix match | pt-BR ↔ en (`definicao`→`definition`) | `_prefix_match` (min 5 chars) |
| Exact symbol regex | `models.Veiculo`, quoted, snake_case | `AgentController._exact_symbol_patterns` |

**Metric (evidence, Lesson 11)**: precision@3 = **5/5 = 1.0** on the 5 queries of
`tests/queries.json` against `harness-basic` — including "installer that activates
core.hooksPath" → `install.sh` (via file name) and "how to log friccao"
→ `log-event.sh` (via accents + file name).

```sh
cd rag-harness
python tests/test_rag.py                       # 7 tests
python -m rag_harness eval ../harness-basic    # precision@k (health metric)
python -m rag_harness agent ../harness-basic "how does the gatekeeper block commits"
# real semantics (optional, with Ollama):
OLLAMA_API_URL=http://localhost:11434 python -m rag_harness index ../harness-basic
```

## D3 — Area Copilot (business context)

The same engine, the areas' domain: spreadsheets, documents, images, data.
Delivered in `area-copilot/` — functional and evaluated:

| Piece | Deliverable |
|---|---|
| `area_harness/business_chunker.py` | Business chunks with **citable source**: CSV (stdlib), XLSX per sheet (openpyxl optional), Markdown per section |
| `area_harness/__main__.py` | CLI: `index`, `query` (answers with SOURCE + lines), `eval` |
| `templates/AGENTS.area.md` | Area router — golden rule: **a number without a source is forbidden** |
| `skills/area-report/SKILL.md` | Installable skill that generates the area artifact with cited sources |
| `tests/` | Fixture (targets spreadsheet + pricing rule) + 3 tests |

**Metric (evidence)**: precision = **3/3 = 1.0** on the business queries
("july southeast target" → the CSV line with `meta_vendas:1200000`;
"pricing rule" → the section of `precificacao.md`). Every answer comes with
`SOURCE: <path> (lines X-Y)` — the area artifact never carries a number
without origin.

```sh
cd area-copilot
python3 tests/test_area.py                              # 3 tests
python3 -m area_harness index tests/fixtures/area_context --verbose
python3 -m area_harness query tests/fixtures/area_context "qual a meta de julho do sudeste"
python3 -m area_harness eval tests/fixtures/area_context  # precision
```

**Overnight mode** (finance): the domain harness schedules
`area_harness query` + `area-report` via cron — the report is published
with sources when the team arrives (Lesson 13: autonomous loop with exit criterion).

## What it is NOT (honest limits)

- The POC with NGramEmbedder validates **architecture**, not semantics — real
  semantics requires Ollama/embeddings API (set `OLLAMA_API_URL`).
- RAG doesn't replace native agents (grep/glob already exist) — the added
  value is in the **business context** and the **chunking quality** in
  large repos.
- Heavy infra (watcher, pgvector, queue) stays until the evidence asks for it —
  the rag-harness.md rule still applies: **don't build before the recorded
  pain**.

**Related**: [Project 05](/projects/project-05) · [Domain harnesses](/harness-designs/domain-harnesses)
