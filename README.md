# Harness Foundation Course

A **Harness Engineering** course + **seven functional harnesses** for
Harnesses for product teams: basic, large (multi-team), App, code RAG, Area Copilot,
multi-domain (games/finance/commercial), artifact skills, and intranet.

An agent is model + harness: this project delivers both sides — the
knowledge to build harnesses and the ready-to-adopt harnesses.

The runnable projects are also published separately at
[github.com/saulostopa/harnesses](https://github.com/saulostopa/harnesses), for
teams that want to download and use the harnesses without cloning the course.

## Quick View: How it Works

[Open the code memory flow](https://claude.ai/artifact/GRLxiHpRE9oML4ngJAyvnb) to see, in Portuguese, how one question travels
with Jev and without it. In the course site, it is on the home page.

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

## Runnable harness projects

The executable harnesses are maintained in the separate
[standalone catalog](https://github.com/saulostopa/harnesses). Clone that
repository when you want to install or run a harness without the course site.
Each project has its own README with dependencies, configuration and tests.

### 3. Pilots / live demo

Follow `pilots/g4-metrics/DEMO.md` — 6 blocks of 2-3 minutes with the real
commands (basic harness, app, Area Copilot, intranet, skills, RAG).

### 4. Installing an external skill

No third-party skill gets in without passing the scanner
([SkillSpector](https://github.com/NVIDIA/SkillSpector), NVIDIA):

After cloning the standalone catalog beside this repository, run the scanner
from the course root:

```sh
../harnesses/harness-basic/scripts/gate-skill-scan.sh https://github.com/user/skill   # scan BEFORE downloading
../harnesses/harness-basic/scripts/gate-skill-scan.sh --all                          # all skills in the repo
```

Blocks score > 50 (exit 1). Requires Docker — the image is built on the
first run. See `docs/skills/skill-guard.md` and
`pilots/skillspector-demo/`.

## Structure

| Folder | What it is |
|---|---|
| `docs/` | The course site (lessons, projects, library, designs) |
| `skills-artifacts/` | v2 artifact skills + quiz (SSTT, a11y, adaptive) |
| `templates/` | Template package for the basic harness |
| `pilots/` | Evidence from pilots G1–G4 + final demo |
| [Standalone harness catalog](https://github.com/saulostopa/harnesses) | Runnable basic, App, RAG, domain, ADK, PostgreSQL and enterprise harnesses |

## Workflow

- **Integration branch**: `develop` (default). **Release**: `main`.
- All new work enters via **PR to `develop`**.
- Work can be tracked through GitHub issues, pull requests, and workflows.

## References

- Original plan: [`plan-harness-foundation-course.md`](plan-harness-foundation-course.md)
- Final report: [`pilots/g4-metrics/G4-FINAL-REPORT.html`](pilots/g4-metrics/G4-FINAL-REPORT.html)
- Live demo: [`pilots/g4-metrics/DEMO.md`](pilots/g4-metrics/DEMO.md)
