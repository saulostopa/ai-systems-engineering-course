#!/usr/bin/env python3
"""triage_demo.py — why a 120k-line log is not a grep problem.

Generates a synthetic application log with one real regression buried in it,
then runs the deterministic half of the qa-perf-triage protocol: normalise each
message, cluster by shape, and rank by cost rather than by count.

Deterministic on purpose — it seeds the RNG, needs no API key and no network,
so the numbers in the docs can be reproduced by anyone:

    python3 pilots/qa-perf-demo/triage_demo.py

The LLM summarisation step of the skill (assets/summarize_log.py) runs after
this one and does need a key. It is not what this demo is proving: the point
here is that ranking by frequency finds the noise, and ranking by total time
finds the bug.
"""

from __future__ import annotations

import random
import re
import statistics
from collections import defaultdict

LINES = 120_000
SEED = 20260921

ENDPOINTS = [
    ("/api/vehicles/search", 45, 18),
    ("/api/vehicles/{id}", 30, 12),
    ("/api/dealers/{id}/stock", 15, 40),
    ("/api/fipe/price", 8, 25),
    ("/health", 2, 3),
]

# Noise that any production log is full of, and that a frequency ranking will
# happily put at the top.
NOISE = [
    "cache miss for key vehicles:brand:{n}",
    "retrying upstream call attempt {n}",
    "connection returned to pool size={n}",
]


def build_log(path: str) -> None:
    rng = random.Random(SEED)
    with open(path, "w", encoding="utf-8") as fh:
        for i in range(LINES):
            # The regression: /api/dealers/{id}/stock degrades only above 60%
            # of the run, which is where the ramp-up reaches peak concurrency.
            late = i > LINES * 0.6
            name, weight, base = rng.choices(ENDPOINTS, weights=[e[1] for e in ENDPOINTS])[0]
            ms = max(1, int(rng.gauss(base, base * 0.3)))
            if late and name == "/api/dealers/{id}/stock":
                ms = int(ms * rng.uniform(9, 14))
            fh.write(f"2026-09-21T10:{i % 60:02d}:00Z INFO request {name} took {ms}ms\n")
            if rng.random() < 0.35:
                fh.write(
                    "2026-09-21T10:%02d:00Z WARN %s\n"
                    % (i % 60, rng.choice(NOISE).format(n=rng.randint(1, 9999)))
                )


REQUEST = re.compile(r"request (?P<name>\S+) took (?P<ms>\d+)ms")
NORMALISE = re.compile(r"\d+")


def triage(path: str) -> None:
    timings: dict[str, list[int]] = defaultdict(list)
    shapes: dict[str, int] = defaultdict(int)
    total = 0

    with open(path, encoding="utf-8") as fh:
        for line in fh:
            total += 1
            match = REQUEST.search(line)
            if match:
                timings[match["name"]].append(int(match["ms"]))
            elif " WARN " in line:
                # Collapse every varying number so 9 000 distinct strings become
                # the three shapes they actually are.
                shapes[NORMALISE.sub("N", line.split(" WARN ", 1)[1].strip())] += 1

    print(f"log: {total:,} lines\n")

    print("Ranked by COUNT — what grep would show you first:")
    for shape, n in sorted(shapes.items(), key=lambda kv: -kv[1])[:3]:
        print(f"  {n:>7,}  {shape}")

    print("\nRanked by TOTAL TIME — where the seconds actually went:")
    rows = []
    for name, values in timings.items():
        values.sort()
        p95 = values[int(len(values) * 0.95)]
        rows.append((sum(values), name, len(values), statistics.median(values), p95))
    for total_ms, name, n, p50, p95 in sorted(rows, reverse=True):
        print(f"  {total_ms/1000:>8.1f}s  {name:<28} n={n:<6} p50={p50:>4}ms  p95={p95:>5}ms")

    worst = max(rows)[1]
    print(f"\nThe one to open: {worst} — its p95 is the outlier, and no other")
    print("endpoint moved. That is a contention signature, not a slow query.")


if __name__ == "__main__":
    log = "/tmp/qa-perf-demo.log"
    build_log(log)
    triage(log)
