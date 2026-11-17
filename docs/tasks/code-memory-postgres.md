---
title: Backlog — code memory on Postgres
---

# Backlog — code memory on Postgres

Status: **in progress** · Priority: **P1** · Scope: `adk-rag-postgres-harness`, with and without Jev

**Quick View: How it Works:** <a href="/demos/code-memory-postgres-jev.html" target="_blank" rel="noopener">open the flow</a> (in Portuguese) of one question, with Jev and without it.

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
8. **Other agents (last cut).** Test the MCP server with Codex on Biometrik, when it is
   time to do so. Claude Code and agy have been tested.

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

**Phase 3 is done** (same branch). `remember` writes to the versioned file and the
database, and `recall` searches memories and feature logs:

- A real run with `qwen3-embedding:4b` on a temporary repository restored both
  memories after the database was dropped, and the replaced decision stayed hidden.
- `recall` reads progress and handoff files through their indexed chunks instead of
  importing a second copy, so they never go stale.
- The credential check uses patterns, so it reduces the risk but does not replace
  reviewing the file in the diff.
- On Biometrik, the logs still use 100-line chunks, and the removal feature's
  progress came fourth for "why did we remove Supabase". The evaluation in step 6
  has to measure this.

**Phase 4 is done** (same branch). The MCP server exposes the five tools over the
same functions as the CLI, and it is registered for Biometrik in the private `local`
scope of Claude Code, so the Biometrik repository did not change:

- By default, Claude Code hid the tools behind its tool search, and the agent answered
  with grep and Read alone. With `anthropic/alwaysLoad`, the same question used
  `search_code`, `recall`, `find_symbol` and `read_lines`.
- That run is not a comparison. The agent tried grep first and turned to the MCP tools
  after grep waited for an approval, so step 6 has to measure how often it chooses them.
- Over real stdio, a search took 0.2 s once the model was loaded, and 5.9 s on the first
  call. Without Ollama, `search_code` fails with a clear error and `remember` still saves.
- The server does not reindex, so new files stay out of the results until the next
  `index`, and it reads the indexed folder rather than the agent's worktree.

**The independent test of phase 4 led to a batch of fixes** (same branch). A tester
with no context found four serious bugs, all reproduced and now covered by tests:

- One large file stopped the whole `index`. Problem files are now listed and skipped,
  with no effect on the 505 Biometrik files.
- A line separator such as U+2028 made the memory file unreadable, and common formats
  such as `DB_PASSWORD=` passed the credential check.
- Symbolic links reached the database and got past `read_lines`. They are no longer
  indexed or read.
- `index` also refuses a missing folder or an unexpected one, replaced decisions no
  longer come back, and `uses` finds scoped packages.
- Moved to step 6: documents crowding searches without `--collection`, handlers inside
  components, `recall` without Ollama and HNSW candidates in a shared database.

**Phase 5 is done** (same branch). `HARNESS_RAG_PROVIDER=postgres` with
`HARNESS_RAG_PROJECT` selects the index in `adk web`:

- The adapter ignored the strategy Jev chose, so `semantic` and `keyword` now really
  change the search. Memories became a third collection beside `code` and `docs`.
- On Biometrik, real Jev chose `code` for the login question and `memory` for the
  Supabase question, and it cited the right files. Three questions cost US$ 0.035,
  all of it from Jev and the conversation model.
- With PostgreSQL down, `adk web` ended in `blocked` with `human_review`. With Ollama
  down, the workflow did the same for `hybrid`, while `keyword` still answered.
- For "where is the hook useUser", Jev chose `keyword` and the evidence had only its
  uses, so the agent said it had not found the definition. This path has no
  `find_symbol`, and step 6 has to measure this.
- Local models routed worse: `qwen2.5:14b` answered the login question without
  searching, and `llama3.1:8b` made up an answer. Step 6 compares them with Jev.

**Phase 6 measured the search and the agents; the fixes await a decision** (same
branch, `evals/`). On 32 Biometrik questions with an answer, counting the right file in
the top 5:

| Search | `4b` | `8b` | `voyage-code-4` | JSON index |
|---|---|---|---|---|
| Right collection, hybrid | 94% | 84% | 81% | 72% |
| Right collection, semantic | 91% | 94% | 78% | 84% |
| No collection, hybrid (MCP default) | 56% | 62% | 69% | not applicable |
| No collection, semantic | 91% | 84% | 62% | not applicable |

- `qwen3-embedding:4b` stays the default. The `8b` took 38 minutes to index and uses
  9.3 GB, with no clear gain. The Voyage run sends no query or document type, so it may
  be underrated.
- The default search is the main problem: full text matches any word and favors long
  documents. In a read-only test, semantic search with exact names first kept 91% and
  put all six name questions first.
- Real Jev found the right file in 20 of 32, at US$ 0.10 for 34 questions. It skipped the
  search in four questions, and three of those got generic answers unrelated to the repository.
- Claude Code used the MCP tools in 3 of 10 questions and cited the expected file in 8.
  It also caught that the `home-streak-progress` handoff was out of date. In a repository
  this size, grep and Read are still enough, so the gain from MCP is not proven.
- With 32 questions written after reading the code, small differences may be chance.

**The fixes from phase 6 are applied** (same branch). A search without a collection now
goes by meaning, names in code style return their definition first, and the triage says
the questions are about the repository:

- The default search rose from 56% to 91% at hit@5. With the right collection, hybrid
  stayed at 94% and the right file in first place rose from 56% to 66%.
- Real Jev rose from 20 to 26 of 32, and from 3 to 6 of 6 on names. It searched in every
  question and still admitted when the repository had no answer.
- Rules are still its weak spot, with 2 of 5, because it sends some of them to `memory` or `code`.
- The numbers use the same questions that guided the fixes, so they may be slightly optimistic.

**The system is ready for a period of real use** (same branch, and
`feature/jev-adk-rag-harness` on Biometrik). `npm run assistente` now uses this memory by
default, with `ASSISTENTE_RAG=json` as the way back. The index updates after each commit,
merge and branch switch, and searches are recorded locally. Further tuning waits for 2 to 4
weeks of real questions, which also become the next evaluation set. Before indexing a second
large project, review the HNSW candidates in a shared database.

**Phase 7 is done, and agy is tested** (same branch). The harness design and Project 06B now
describe the code memory and what the evaluation taught, in both languages.

- agy reached the tools and answered correctly when the question named `find_symbol`.
- Asked the same 10 questions as Claude Code without naming a tool, it chose MCP in none. It gave
  6 answers, citing the expected file in 5, and 4 answers came back empty because headless agy denied
  shell commands. That is a limit of this test, not of the answers.
- agy has no setting per repository, so a server fixed on one project would answer in all of them.
  The registration was removed after the test.
- Codex is postponed.

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
- agy can use the MCP tools on Biometrik.
- Codex uses the MCP tools on Biometrik (postponed).
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
