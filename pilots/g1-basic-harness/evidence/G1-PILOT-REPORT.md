# Pilot G1 — basic harness in a real repo

> **Pilot repo**: `pricing-cli` (simplified FIPE price calculator, Python)
> **Harness**: `harness-basic` (B1) installed via `install.sh`
> **Date**: 2026-09-12 · **Status**: FEATURE DELIVERED WITH EVIDENCE

## Pilot setup

| Step | Command | Result |
|---|---|---|
| Repo created | `git init + pricing.py + 2 tests` | baseline with 2 green tests |
| Harness installed | `install.sh <repo>` | templates + scripts + hooks; `core.hooksPath=.githooks` |
| Feature declared | `feature_list.json f1: in_progress` | commit allowed (gatekeeper: OK, 1 feature) |
| Implementation | `pricing.py` + 2 new tests | **4 green tests** (2→4, no reduction) |
| Validation | `./scripts/validate-harness.sh` | **HARNESS OK — 0 failures, 0 warnings** |
| Conclusion | `f1: passing` | evidence recorded |

## Gate behavior (real evidence)

| Scenario | Observed result |
|---|---|
| Commit with 1 feature `in_progress` | ✅ allowed |
| Commit with 0 features | ✅ **BLOCKED** ("no feature in_progress — declare a feature") |
| Frontend change without E2E | (n/a — Python repo; E2E gate belongs to the app harness, G2) |
| Updating `feature_list.json` itself with 0 in_progress | ✅ **BLOCKED** — real finding (see below) |
| `validate-harness.sh` before push | ✅ HARNESS OK |

## Metrics (baseline vs. harness)

| Metric | Value |
|---|---|
| Tests before | 2 |
| Tests after | 4 (+2 for the feature, none weakened) |
| Feature commits | 3 (declare → implement → passing) |
| Gatekeeper blocks | 2 (both correct; 1 with finding) |
| Evidence recorded | build/test (unittest OK), validate-harness OK |

## Real finding (becomes a harness improvement)

**The gatekeeper blocks until `feature_list.json` is updated** when no feature
is `in_progress` — which prevents the very transition to `passing`. Current
mitigation: conscious bypass (`.harness/skip-gatekeeper`, 5 min). Recommended
harness improvement: the gatekeeper should **allow commits that touch only
`feature_list.json`/`policies/`** (state change is not code change) — item for
the B1 evolution.

## Pilot conclusion

The basic harness delivered exactly what the course teaches: **an end-to-end
feature with evidence, real mechanical gates, and one concrete improvement
finding** — proof that the harness works and that it is itself a product in
evolution (Lesson 11: observability feeds improvement).