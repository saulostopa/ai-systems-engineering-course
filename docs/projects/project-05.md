---
title: Project 05 — Area Copilot with RAG
---

# Project 05 — Area Copilot with RAG

> The harness that gives the agent your area's context: spreadsheets, documents, images and data — for non-technical teams to manage features with AI.

## Objective

Assemble an **Area Copilot**: a harness where people from any area (finance, sales, operations, games) keep the context of their own work — business files, spreadsheets, images, data — and use an agent with **retrieval (RAG)** to manage features and produce artifacts.

It is Story **D3** of the course (business RAG) in practical form.

## What is different from everything so far

In the previous projects, the context was **code** (repo, AGENTS.md, tests). Here the context is **area knowledge**:

- pricing spreadsheets, targets, history;
- briefing documents, business rules;
- images (screen captures, listings, creative assets);
- exported data (CSV, JSON).

The agent needs to find the right context **when the task asks for it** — that is what RAG solves.

## Minimal architecture (no database, to start)

You don't need pgvector on day one. The minimal version is **RAG by convention**:

```
area-context/                    # the area's "memory" (versioned!)
├── planilhas/                   # data sources
├── documentos/                  # briefings, rules
├── imagens/                     # visual evidence
└── index.md                     # map: what exists and where
```

And `index.md` is the trick: a **semantic index written by the agent** that maps each context with tags and summaries. The agent reads the index (cheap) and opens only the file the task asks for (expensive, on demand) — the same router pattern from Lesson 04.

## Step by step

### 1. Set up the `area-context` folder

Put 5-10 real files from your area (even anonymized). Anonymize first — the repo is versioned.

### 2. Generate the `index.md`

Ask the agent:

```
"generate an index of the area-context folder: for each file, tags, a 1-line
summary and when it's worth opening. Save it to area-context/index.md"
```

### 3. Write the area's `AGENTS.md`

```markdown
# AGENTS.md — Harness for the [name] area

## 1. How to work
- Before any task, read area-context/index.md.
- Specific context? Open the file pointed by the index (don't guess).
- Never invent numbers: every cited datum comes from a read file.

## 2. How to verify
- Every artifact cites its source (file + line/tab when applicable).
- "I don't know" is a valid answer; an invented number is not.

## 3. State
- The area's features live in feature_list.json.
```

### 4. Run an area feature

Finance example: *"analyze last month's targets spreadsheet and generate the summary for the meeting"*. The agent must: consult the index → open the spreadsheet → validate → generate the artifact with cited sources.

### 5. (Optional) Evolve into real RAG

When volume grows, migrate the manual index to **hybrid RAG** (vectors + text search) — the architecture is in the `harness-factory`'s `rag-harness.md`: structure-based chunking, pgvector + full-text with RRF fusion, and agentic retrieval (the agent decides which search tool to use). The trigger to migrate: the manual index started failing (Lesson 11 — decide by evidence).

## Verification

- An area task is completed with **all sources cited** and no invented numbers.
- A new context (added file) shows up in the index after regenerating it.
- You can answer: "where did the agent find that?" for any claim in the artifact.

## Deliverable

The versioned `area-context/` + `index.md` + area `AGENTS.md` + 1 example artifact with cited sources.

::: tip Status
The version with vector database, image OCR and scheduled execution is **EPIC D** of the course.
:::

**Next project**: [06 — Enterprise harness (multi-team)](/projects/project-06) — the step out of a single repository into many.
