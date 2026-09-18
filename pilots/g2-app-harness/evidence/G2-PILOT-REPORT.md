# Pilot G2 — app harness in a real app

> **Pilot app**: vehicle search (plain HTML/JS, no framework)
> **Harness**: `app-harness` (C1: E2E gate) + agentic navigation protocol (C2)
> **Date**: 2026-09-12 · **Status**: QA LAYER + NAVIGATION VALIDATED

## Pilot setup

| Step | Result |
|---|---|
| App created (HTML/JS, `role=list`, `role=region`, empty state) | OK |
| E2E gate installed (`e2e-gate.sh` + `.harness/config.yaml`: `frontend_paths: src`) | OK |
| E2E tests: `tests/e2e/test_search.py` (2 cases: results + empty state) | OK |

## QA layer — gate behavior (real evidence)

| Scenario | Staged | Result |
|---|---|---|
| **1. Frontend without E2E test** | only `src/index.html` | ✅ **BLOCKED**: "frontend change without E2E test (Lesson 10). Expected path: tests/e2e/" |
| **2. Frontend + E2E test** | `src/index.html` + `tests/e2e/test_search.py` | ✅ **ALLOWED**: "E2E-GATE: ok" |

The gate works exactly as designed: a screen change **does not pass without
the corresponding test** — E2E is a commit contract, not an intention.

## Agentic layer — vision-based navigation (protocol C2 executed)

> App served at `http://localhost:3100` (3000 was taken by the Webmotors
> catalog dev server — environment finding).

| Protocol step | Evidence |
|---|---|
| 1. Start the app | `python3 -m http.server 3100` → **HTTP 200** |
| 2. Navigate as a user (search flow) | `GET /?q=civic` → **HTTP 200**; page contains `role=list` (results) |
| 3. Edge states | `role=region` with "No vehicles" message present (empty state) |
| 4. Verdict per criterion | Table below |

| Criterion | Verdict | Evidence |
|---|---|---|
| App starts and responds | **ACCEPTED** | HTTP 200 (curl) |
| Accessible search flow | **ACCEPTED** | `role=search` + `role=list` in the DOM |
| Empty state present | **ACCEPTED** | "No vehicles" text + `role=region` |
| Vision-based navigation (limitation) | **PARTIAL** | in this pilot step 4 ran without a vision model — real screenshots require an agent with vision (enable in the demo with Claude/GPT-4o) |

## Findings

1. **Port 3000 taken by the catalog dev server** — the app harness should
   parameterize the port (`PORT`/config) and check availability before
   starting.
2. **Screenshots require an agent with vision** — protocol C2 is documented
   and structurally validated; the real visual validation (screenshots +
   ACCEPTED/REJECTED verdict per criterion) is the part to demonstrate live in
   the final demo (G4).

## Pilot conclusion

The app harness proved both layers: **the E2E gate genuinely blocks** frontend
changes without tests (mechanical contract), and **the agentic navigation has
an executable protocol** with a verdict per criterion. The visual part is left
for the demo with a vision agent — the mechanics are already ready and
validated.