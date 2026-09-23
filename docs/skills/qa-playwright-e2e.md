---
title: qa-playwright-e2e
---

# qa-playwright-e2e — the test the gate asks for

> The only E2E test worth writing is one that fails for a real reason. This
> skill writes tests against **roles, not CSS** — so a refactor that changes a
> class name does not turn into a red build nobody believes.

## The gate that asks for it

This is the one skill in the catalog the harness demands *before* you commit,
not after you deliver. `scripts/e2e-gate.sh` runs on `pre-commit`:

```
E2E-GATE: frontend files detected:
  src/components/btn.tsx
E2E-GATE: BLOCKED — frontend change without an E2E test (Lesson 10).
  Expected path: e2e/
  Use the qa-playwright-e2e skill to write the test.
  Conscious bypass: .harness/skip-e2e-gate (expires in 5 min)
```

Bring the test along and it steps aside:

```
E2E-GATE: ok
```

It is **opt-in per project**, because a repo with no frontend should pay nothing
for it. Fill in the `qa:` block of `.harness/config.yaml` and it starts working:

```yaml
qa:
  frontend_paths: "src"
  frontend_extensions: "tsx ts jsx js"
  e2e_test_path: "e2e"
```

::: warning The bug this gate had
The config parser anchored on the end of the line, so an **inline comment**
made the pattern miss — the variable became the whole line, the file filter
matched nothing, and the gate printed `ok` while waving every commit through.
A gate that fails open on a config it cannot parse is worse than no gate,
because it reports success. `tests/test_e2e_gate.sh` now pins the behaviour with
a config that has comments in it, and a parse failure blocks instead of passing.
:::

## What a good test looks like

`app-harness/templates/e2e/` ships the pattern the skill writes to. Three rules
carry almost all of the value:

**Semantic locators.** The only contact with the DOM is through roles and
labels — the same thing a screen reader uses:

```python
self.search_input  = page.get_by_role("searchbox", name="Buscar veículos")
self.search_button = page.get_by_role("button", name="Buscar")
```

Not `page.locator(".search-form > input:nth-child(2)")`. A test written against
structure breaks when structure changes, which is exactly when you least want to
be debugging your tests.

**Page Object Model.** One screen, one class, one method per flow. The test says
what it is checking, never how to click it.

**Intercepted network.** The fixture fulfils the request with a fixed payload,
so the test does not fail because a staging API is having a bad afternoon:

```python
page.route("**/api/v1/search?*", lambda route: route.fulfill(json={"results": FIXTURE_RESULTS}))
```

Determinism is not a nicety here — a flaky suite gets muted, and a muted suite
is worse than no suite.

## Triaging a flake

Flaky is a bug, not luck. The protocol is to capture, not to re-run:

```sh
pytest tests/e2e --trace=retain-on-failure
playwright show-trace <artifact>.zip
```

The trace viewer replays the run with the DOM at each step. "It passed on retry"
is not a diagnosis.

## Install

```sh
npx skills add <the qa-playwright-e2e skill> --agent opencode --copy
```

**Related**: [qa-perf-triage](/skills/qa-perf-triage) · [App Harness](/harness-designs/app-harness) ·
[Lesson 10 — End-to-end tests change the outcome](/lectures/lecture-10)
