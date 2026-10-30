---
title: Backlog — code memory on Postgres
---

# Backlog — code memory on Postgres

Status: **in progress** · Priority: **P1** · Scope: `adk-rag-postgres-harness`, with and without Jev

## Why this belongs in the harness backlog

Coding agents lose what they learned about a repository between sessions, and
grep only finds what the agent already knows how to name. Cursor addresses this
with a code index that the agent queries by meaning. According to its public
documentation, it honors ignore files, splits code along its syntax, syncs
incrementally through a tree of file hashes, returns a path and line range that
the client reads locally, and exposes semantic search as one agent tool beside
grep.

The harnesses already have parts of this. `rag-harness` discovers files through
Git and `.ragignore`, caches embeddings by hash and has an agentic controller,
but stores its index in JSON files and only chunks Python by syntax.
[`adk-rag-postgres-harness`](/harness-designs/adk-rag-postgres-harness) has
Docker and pgvector, but it is a sketch:

- It replaces a whole collection on every indexing run.
- Its search scores every row and mixes an unnormalized text rank with cosine
  distance, so it never uses the HNSW index.
- It fixes the vector size at 768, and it embeds one chunk at a time without a
  cache.
- It ignores `.ragignore` and the Git file list.
- `adk web` cannot select it: `HARNESS_RAG_PROVIDER` only accepts `demo` and
  `index`.
- It has no symbols or memory, and only two tests.

## Goal

Turn `adk-rag-postgres-harness` into a code memory on Postgres and Docker,
built from open source parts, with one core and two entry points:

- **Without Jev:** an MCP server plus a CLI, so Claude Code, Codex and agy use
  the memory through their subscriptions and decide by themselves what to search.
- **With Jev:** `HARNESS_RAG_PROVIDER=postgres` in `adk web`, where Jev chooses
  collection and strategy and the confidence gates still apply.

## Decisions

Made with the course owner on 2026-10-30.

| Topic | Decision | Reason |
|---|---|---|
| Location | Evolve `adk-rag-postgres-harness` | No new package; ADK becomes an optional extra, so the path without Jev does not install it |
| Entry without Jev | MCP server + CLI | The CLI is needed for indexing anyway; MCP makes the tools visible to the agent beside grep |
| Embeddings | Open source, starting with `qwen3-embedding:4b` on Ollama | Zero API cost; its score is close to the `8b` at about half the size |
| TS, TSX and JS chunks | tree-sitter | Biometrik is React Native; line chunks split components and functions |
| Memory scope | Code + decisions and handoffs | Decisions and conventions are what agents lose between sessions |
| Search results | Path and lines, reread from disk | The agent never receives stale code |

## Proposed evolution

1. **Postgres core.** Tables `projects`, `files` (path, hash, language), `chunks`
   (lines, content hash, generated `tsvector`), `embeddings` (content hash,
   model, vector), `symbols`, `edges`, `memories` and `queries`. Sync by file
   hash and embed only what changed, in batches. Search with reciprocal rank
   fusion over the top 50 from HNSW and the top 50 from full text.
2. **Code-aware chunks.** tree-sitter for TS, TSX and JS, the existing AST
   chunker for Python, and extraction of symbols and imports to answer "where is
   X used".
3. **Memory.** Store decisions, conventions and handoffs with their source, and
   mark a memory as replaced when a newer one supersedes it. Import feature
   `progress` and `handoff` files. Each `remember` also writes to a text file in
   the repository, such as `docs/harness/memories.jsonl`, without vectors, and
   refuses content that looks like a credential. Git is the backup, and `index`
   restores memories from that file on a new machine.
4. **Entry without Jev.** CLI commands for indexing and search, and an MCP server
   with `search_code`, `find_symbol`, `read_lines`, `remember` and `recall`, over
   the same functions. Register it for Biometrik.
5. **Entry with Jev.** Wire the existing adapter into the ADK app through
   `HARNESS_RAG_PROVIDER=postgres`.
6. **Evaluation.** Golden questions from Biometrik compare `qwen3-embedding:4b`,
   `qwen3-embedding:8b` and `voyageai/voyage-code-4`, the JSON index against
   Postgres, and Jev against the agent deciding alone. Report hit@k, MRR, latency
   and cost, and fix the default model from that evidence.
7. **Course.** Update the harness design and the related lessons, in English and
   Brazilian Portuguese.

## Progress

**Phase 1 is done** (2026-10-30, branch `feature/code-memory-postgres` of the
harnesses repository). Measured on Biometrik, with 505 files and 728 unique
chunks, on an M1 Max with `qwen3-embedding:4b`:

- The first indexing run took 26 minutes, and a run with no changes took 0.7 s.
- A search took about 0.6 s from the CLI, including the query embedding.
- PostgreSQL chose an exact scan at this size, which is correct for so few rows.
  In a synthetic test with 20,000 rows it chose the HNSW index, and the database
  part of the search took 0.07 s.
- A search with no `--collection` is crowded by harness documents, and line
  chunks still cut components. Phase 2 and the evaluation address this.

**Phase 2 is done** (same branch). tree-sitter split the 385 TS and JS files of
Biometrik into definitions of at most 80 lines, for 1,467 unique chunks in the
repository:

- The new index reused 201 vectors and embedded 1,266 chunks in 13 minutes.
- `uses useUser` returned the 20 files that grep finds beyond the definition.
- All 1,324 imports of local modules resolved, including `tsconfig.json` aliases.
- Code-only searches now point to whole components, such as `Login` and
  `UserProvider`. Without `--collection`, harness documents still come first, and
  the evaluation in step 6 has to measure and fix this.

## Embedding model

Vectors from different models live in different spaces, so they cannot be
converted: changing models means embedding the text again. Because `embeddings`
is keyed by content hash and model, vectors from several models can coexist and
returning to a model already used recomputes nothing. The Biometrik JSON indexes
use Voyage and must be regenerated, not imported.

The `qwen3-embedding` tags can output more dimensions than the 2,000 that a
pgvector `vector` HNSW index accepts. The plan truncates vectors to 1,024
dimensions and normalizes them again.

The authors report nDCG@10 of 80.06 for the 4B model and 80.68 for the 8B model
on MTEB Code. That is their own result, so step 6 decides on real questions.

Still to confirm when the work starts:

- How `voyage-code-4` dimensions fit the shared vector column.
- Whether `nomic-embed-code` is available on Ollama, as another candidate.

## Acceptance criteria

- `docker compose up` and one CLI command index a real repository, and a second
  run embeds only the files that changed.
- Search can use the HNSW index, confirmed with `EXPLAIN` on a table large enough
  for the planner to prefer it, and returns path and line range with content
  reread from disk.
- TS and TSX files are chunked by syntax, and `find_symbol` finds Biometrik
  components and functions.
- Memories record their source and a superseded memory is not returned as current.
- After dropping the database, `index` restores every memory from the versioned
  file, and chunks and embeddings are rebuilt from the repository.
- Claude Code uses the MCP tools on Biometrik with no paid API call beyond any
  embedding model that was explicitly chosen.
- `adk web` runs with `HARNESS_RAG_PROVIDER=postgres`; retrieval failures end in
  `blocked` with `human_review`.
- The path without Jev installs and runs without Google ADK.
- The evaluation report fixes the default embedding model, and the reason is
  recorded in the harness README and the course.
- No credential or `.env` value reaches the database, logs or evaluation output.

## Dependencies

- Docker and Ollama on the development machine.
- The token and cost ledger, so the comparison reports cost from the same source
  as daily use.

## References

- [Postgres harness design](/harness-designs/adk-rag-postgres-harness)
- [RAG harness design](/harness-designs/rag-harness)
- [Current ADK + RAG + Jev feature](/tasks/adk-rag-jev-harness)
- [Token and cost ledger](/tasks/token-cost-ledger)
- [Qwen3 Embedding on Ollama](https://ollama.com/library/qwen3-embedding)
- [Qwen3 Embedding paper](https://arxiv.org/abs/2506.05176)
