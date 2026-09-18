# Harness Foundation Course — Webmotors

A **Harness Engineering** course + **seven functional harnesses** for
Webmotors: basic, large (multi-team), App, code RAG, Area Copilot,
multi-domain (games/finance/commercial), artifact skills, and intranet.

An agent is model + harness: this project delivers both sides — the
knowledge to build harnesses and the ready-to-adopt harnesses.

## How to run the 2 environments

### 1. Course site (VitePress)

```sh
npm install        # first time (Node >= 22)
npm run dev        # http://localhost:5173 (or use the port below if busy)
```

If port 5173 is busy:

```sh
npx vitepress dev docs --port 5174
# → http://localhost:5174
```

Production build:

```sh
npm run build && npm run preview
```

The course site is bilingual: English at `/` (default) and Portuguese at
`/pt-BR/`, with a language switcher in the navbar of every page. Browser
titles, navigation labels, and visible interface text follow the selected
locale.

## Repository language convention

This repository is maintained in English — all new user-facing content,
contributor instructions, examples, runtime messages, and generated-report
text must be written in English. Portuguese appears only in intentionally
preserved fixture data, historical examples, or source quotations.

### How to contribute translations

- **Content layout**: English is the default locale and lives directly under
  `docs/`; Portuguese lives under `docs/pt-BR/` mirroring the same folder
  structure. Every course page must have a counterpart in both locales.
- **Authoring**: write pages in the default (English) copy, then create the
  equivalent page under `docs/pt-BR/`. Internal links inside `pt-BR/` pages
  must use the `/pt-BR/` prefix (e.g. `/pt-BR/lectures/lecture-02`) so the
  reader stays in the selected locale.
- **Navigation labels**: locale-specific nav/sidebar/outline/footer text is
  configured in `docs/.vitepress/config.mts` (top level = English, under
  `locales['pt-BR'].themeConfig` = Portuguese).
- **Checks**: `npm run check:i18n` verifies page parity between locales and
  that all internal links resolve within each locale. Run it before pushing.
- Localized learner content was originally tracked in
  [docs/tasks/course-internationalization.md](docs/tasks/course-internationalization.md).

## Extra environments

### 3. Artifacts intranet (RAG search)

```sh
cd artifacts-intranet
python3 -m artifacts_intranet.server --port 8765 --reindex
# → http://localhost:8765
```

### 4. Pilots / live demo

Follow `pilots/g4-metrics/DEMO.md` — 6 blocks of 2-3 minutes with the real
commands (basic harness, app, Area Copilot, intranet, skills, RAG).

### 5. Tests and evaluations

```sh
cd rag-harness && python3 tests/test_rag.py          # 7 RAG engine tests
cd area-copilot && python3 tests/test_area.py        # 3 Area Copilot tests
cd artifacts-intranet && python3 tests/test_intranet.py  # 3 intranet tests
cd rag-harness && python3 -m rag_harness eval ../harness-basic   # precision@k
cd hard-harness && PYTHONPATH=. python3 tests/test_hard_harness.py   # 19 core tests
harness-basic/tests/test_skill_guard.sh              # 13 skill gate tests
```

### 6. Installing an external skill

No third-party skill gets in without passing the scanner
([SkillSpector](https://github.com/NVIDIA/SkillSpector), NVIDIA):

```sh
harness-basic/scripts/gate-skill-scan.sh https://github.com/user/skill   # scan BEFORE downloading
harness-basic/scripts/gate-skill-scan.sh --all                          # all skills in the repo
```

Blocks score > 50 (exit 1). Requires Docker — the image is built on the
first run. See `docs/skills/skill-guard.md` and
`pilots/skillspector-demo/`.

## Structure

| Folder | What it is |
|---|---|
| `docs/` | The course site (lessons, projects, library, designs) |
| `harness-basic/` | Installable basic harness (templates + gates) |
| `app-harness/` | App harness: E2E gate + agentic navigation skill |
| `rag-harness/` | Hybrid RAG engine (AST chunks, cache, RRF, agent) |
| `area-copilot/` | Business-context RAG (cited sources) |
| `domains/` | Multi-domain playbooks (games, finance, commercial) |
| `skills-artifacts/` | v2 artifact skills + quiz (Eleanor, a11y, adaptive) |
| `artifacts-intranet/` | Intranet with RAG search over the artifacts |
| `templates/` | Template package for the basic harness |
| `pilots/` | Evidence from pilots G1–G4 + final demo |
| `hard-harness/` | Executable orchestration: graph, schemas, gates, persistence (19 tests) |

## Workflow

- **Integration branch**: `develop` (default). **Release**: `main`.
- All new work enters via **PR to `develop`**.
- Work can be tracked through GitHub issues, pull requests, and workflows.

## References

- Original plan: [`plan-harness-foundation-course.md`](plan-harness-foundation-course.md)
- Final report: [`pilots/g4-metrics/G4-FINAL-REPORT.html`](pilots/g4-metrics/G4-FINAL-REPORT.html)
- Live demo: [`pilots/g4-metrics/DEMO.md`](pilots/g4-metrics/DEMO.md)