---
title: qa-perf-triage
---

# qa-perf-triage — when the graphs are flat and it is still slow

> CPU is fine. Memory is fine. p99 tripled. This skill is for the bug that only
> exists under concurrency, and for the 120,000-line log that holds the answer
> somewhere.

## Why grep does not find this

Run the demo — it is deterministic, needs no API key and no network:

```sh
python3 pilots/qa-perf-demo/triage_demo.py
```

It builds a synthetic 162k-line log with one real regression buried in it, then
ranks it two ways. **Ranked by count**, which is what a grep habit gives you:

```
 14,199  cache miss for key vehicles:brand:N
 14,009  connection returned to pool size=N
 13,809  retrying upstream call attempt N
```

Three shapes of noise, tens of thousands of lines, and not one of them is the
bug. **Ranked by total time:**

```
  3685.4s  /api/dealers/{id}/stock      n=17980  p50=51ms   p95=630ms
   945.7s  /api/vehicles/search         n=54104  p50=17ms   p95= 26ms
   412.5s  /api/vehicles/{id}           n=35895  p50=12ms   p95= 17ms
```

`/api/dealers/{id}/stock` serves **three times fewer requests** than search and
burns **four times more wall clock**. Its p95 is 24× its own p50 while every
other endpoint stays flat — one endpoint degrading alone under load is a
contention signature, not a slow query.

The two moves that produced that: **normalise before counting** (collapse every
varying number so 9,000 distinct strings become the 3 shapes they are), and
**rank by cost, not by frequency**.

## Why the load test ramps

A flat load test at low concurrency will not reproduce this. The skill's
`locustfile` ramps 10 → 100 → 300 users on purpose:

```python
stages = [
    {"duration":  60, "users":  10, "spawn_rate":  1},
    {"duration": 180, "users": 100, "spawn_rate":  5},
    {"duration": 300, "users": 300, "spawn_rate": 10},
]
```

Contention bugs — pool exhaustion, lock convoys, N+1 under parallel reads —
appear at a threshold. A test that never crosses it reports green and teaches
you nothing.

## The AI step, and its limit

After the deterministic pass narrows the field, `summarize_log.py` chunks what
is left and asks a model for anomaly clusters. Two things to know before running
it:

- **It needs an API key**, which is why it is not part of the demo above.
- **It redacts before sending** — bearer tokens, `api_key`/`secret`/`password`
  assignments, emails and card numbers. That is best-effort, not a guarantee:
  a log with an app-specific secret format still needs scrubbing at the source.
  Read the patterns before pointing it at a production log.

## This one is not wired into the delivery

Every other skill in the catalog is [demanded by a flow](/harness-designs/enterprise-harness)
when a feature closes. This one is not, deliberately: it is a **diagnostic**,
reached for when something is already wrong. Making every delivery owe a load
test would add minutes to every merge to catch a problem most features do not
have — and a gate people resent is a gate people bypass.

What the harness does instead is keep the evidence: `log-event.sh` records the
friction, so the second time this happens you are not starting from zero.

## Install

```sh
npx skills add <the qa-perf-triage skill> --agent opencode --copy
```

**Related**: [qa-playwright-e2e](/skills/qa-playwright-e2e) ·
[Lesson 11 — Observability inside the harness](/lectures/lecture-11)
