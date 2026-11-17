#!/usr/bin/env python3
"""build-report-g4.py — final G4 report rendered with the v2 assets (F1).

Dogfooding: the project's final report uses the same skill the course teaches
(feature-report v2 — SSTT, a11y, i18n). Usage: python3 report.py
"""

from __future__ import annotations

import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(ROOT, "..", "..", "skills-artifacts", "assets"))
CSS = open(os.path.join(ASSETS, "system.css"), encoding="utf-8").read()
SKELETON = open(os.path.join(ASSETS, "skeleton.html"), encoding="utf-8").read()

METRICS = """\
    <section class="card" aria-label="What was delivered">
      <h2 data-i18n-pt="O que foi entregue" data-i18n-en="What was delivered">What was delivered</h2>
      <p>The Harness Foundation Course — a complete course and <b>seven functional harnesses</b> for product teams, built and validated with the very method they teach.</p>
      <p><span class="badge badge-solid">7 EPICs</span> <span class="badge badge-solid">21 stories</span> <span class="badge badge-soft">19 PRs</span> <span class="badge badge-soft">26/28 items DONE</span></p>
    </section>
    <section class="card" aria-label="Metrics per harness">
      <h2 data-i18n-pt="Métricas por harness" data-i18n-en="Metrics per harness">Metrics per harness</h2>
      <table>
        <thead><tr><th>Harness</th><th>Evidence</th><th>Metric</th></tr></thead>
        <tbody>
          <tr><td>Basic (B1)</td><td>G1 pilot on a real repo</td><td>2→4 tests without reduction; gatekeeper correctly blocked 2x</td></tr>
          <tr><td>Large (B2)</td><td>4-layer blueprint</td><td>governance + workflow + observability documented</td></tr>
          <tr><td>App (C1+C2)</td><td>G2 pilot</td><td>frontend without E2E BLOCKED; with E2E RELEASED; navigation HTTP 200</td></tr>
          <tr><td>RAG code (D1+D2)</td><td>eval in harness-basic</td><td>precision@3 = 5/5 (1.0); 7 tests</td></tr>
          <tr><td>Area Copilot (D3)</td><td>eval + G3 pilot</td><td>precision 3/3 (1.0) with cited sources</td></tr>
          <tr><td>Finance (E3)</td><td>real nightly run</td><td>report published with 9 sources; output gate PASS</td></tr>
          <tr><td>Games (E2)</td><td>simulated playtest</td><td>ACCEPTED with valid doc; REJECTED without criteria</td></tr>
          <tr><td>Commercial (E4)</td><td>proposal-check</td><td>APPROVED (0 failures) / BLOCKED (4) — pos/neg tests</td></tr>
          <tr><td>Skills v2 (F1)</td><td>mechanical build-demo</td><td>4 levels/12 options/4 correct; a11y + i18n + adaptive quiz</td></tr>
          <tr><td>Intranet (F2)</td><td>E2E with curl</td><td>search "gatekeeper blocks" → right docs with tools</td></tr>
        </tbody>
      </table>
    </section>
    <section class="card" aria-label="Real findings that improved the harnesses">
      <h2 data-i18n-pt="Achados reais que melhoraram os harnesses" data-i18n-en="Real findings that improved the harnesses">Real findings that improved the harnesses</h2>
      <ul>
        <li>G1: gatekeeper blocked updating feature_list itself → improvement recommended (state-only commits).</li>
        <li>G2: port 3000 taken by the dev server → parameterize PORT.</li>
        <li>D2: accents and camelCase broke lexical search → normalized tokenizer (2/5 → 5/5).</li>
        <li>E2: case-sensitive grep rejected valid docs → fix (-i) found by a test.</li>
        <li>E3: numbers outside the SOURCE block → block-based output gate (awk).</li>
      </ul>
    </section>
    <section class="card" aria-label="Decisions and trade-offs">
      <h2 data-i18n-pt="Decisões e trade-offs" data-i18n-en="Decisions and trade-offs">Decisions and trade-offs</h2>
      <p>Chose local NGram RAG instead of Ollama/pgvector because the POC validates architecture without infrastructure, at the cost of real semantics only with an external provider — connectable via OLLAMA_API_URL.</p>
      <p>Chose to postpone heavy infrastructure (watcher/queue/pgvector) instead of building it early because the rag-harness.md rule mandates deciding by evidence, at the cost of on-demand re-indexing until EPIC G proves the pain.</p>
      <p>Chose AgEnFK scoped to the project instead of global because independence between agents is non-negotiable, at the cost of keeping the management only in this repo.</p>
    </section>
    <section class="card" aria-label="Open questions">
      <h2 data-i18n-pt="Perguntas abertas" data-i18n-en="Open questions">Open questions</h2>
      <p>When does the business RAG get real data from a team area? Which area pilots Area Copilot first (finance, commercial, games)? Does the basic harness become an npm package/global team installer?</p>
    </section>
"""


def build() -> str:
    html = SKELETON
    html = html.replace("/* system.css is injected HERE whole — never via template engine */", CSS)
    marker = "<!-- ═══ ARTIFACT CONTENT ═══"
    end = "<!-- Dynamic quiz:"
    start = html.index(marker)
    end_idx = html.index(end)
    html = html[:start] + marker + "\n         (generated by report.py — feature-report skill v2)\n\n" + METRICS + "\n\n    " + html[end_idx:]
    return html


def main() -> None:
    out = os.path.join(ROOT, "G4-FINAL-REPORT.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(build())
    print(f"OK {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    main()
