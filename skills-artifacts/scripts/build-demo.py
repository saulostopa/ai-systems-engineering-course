#!/usr/bin/env python3
"""build-demo.py — mechanical proof of the v2 assets (Eleanor + a11y + i18n).

Assembles the artifact the same way the skill does: injects system.css into
the <style> block of skeleton.html and the content into <main>. Generates a
report + quiz demo.

Usage: python3 scripts/build-demo.py
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSS = open(os.path.join(ROOT, "assets", "system.css"), encoding="utf-8").read()
SKELETON = open(os.path.join(ROOT, "assets", "skeleton.html"), encoding="utf-8").read()

REPORT_BODY = """\
    <section class="card" aria-label="What was delivered">
      <h2 data-i18n="s1" data-i18n-pt="O que foi entregue" data-i18n-en="What was delivered">What was delivered</h2>
      <p>Added email validation to the dealership search form.</p>
      <p><span class="badge badge-solid">DELIVERED</span> <span class="badge badge-soft">no regression</span></p>
    </section>
    <section class="card" aria-label="Decisions and trade-offs">
      <h2 data-i18n="s2" data-i18n-pt="Decisões e trade-offs" data-i18n-en="Decisions and trade-offs">Decisions and trade-offs</h2>
      <p>Chose client-side regex instead of API validation because the endpoint already existed without that contract, at the cost of duplicating the rule across clients.</p>
    </section>
    <section class="card" aria-label="Verification">
      <h2 data-i18n="s3" data-i18n-pt="Verificação" data-i18n-en="Verification">Verification</h2>
      <table>
        <thead><tr><th>Command</th><th>Expected</th><th>Actual</th></tr></thead>
        <tbody>
          <tr><td><code>npm run build</code></td><td>exit 0</td><td>exit 0</td></tr>
          <tr><td><code>npm test</code></td><td>12 tests green</td><td>12 green (no reduction)</td></tr>
          <tr><td><code>pytest tests/e2e -q</code></td><td>2 green</td><td>2 green</td></tr>
        </tbody>
      </table>
    </section>
    <section class="card" aria-label="Open questions">
      <h2 data-i18n="s4" data-i18n-pt="Perguntas abertas" data-i18n-en="Open questions">Open questions</h2>
      <p>Should the rule migrate to the API once the contract exists? Who decides the format limits (e.g. punycode domains)?</p>
    </section>
"""

QUIZ_BODY = """\
      <div id="quiz-levels">
      <div class="quiz-level" data-level="tier-1" data-level-label="Basic" data-level-hint="review what the feature does">
        <h3>Basic</h3><span class="quiz-level-score badge badge-soft"></span>
        <p class="quiz-stem" data-i18n-pt="O que a feature valida?" data-i18n-en="What does the feature validate?">What does the feature validate?</p>
        <button type="button" class="quiz-opt" data-correct="true" data-i18n-pt="Formato de e-mail no formulário" data-i18n-en="Email format in the form">Email format in the form</button>
        <button type="button" class="quiz-opt" data-i18n-pt="Senha forte" data-i18n-en="Strong password">Strong password</button>
        <button type="button" class="quiz-opt" data-i18n-pt="CEP válido" data-i18n-en="Valid ZIP code">Valid ZIP code</button>
        <p class="quiz-why" data-i18n-pt="O relatório declara a entrega como validação de e-mail." data-i18n-en="The report declares the delivery as email validation.">The report declares the delivery as email validation.</p>
      </div>
      <div class="quiz-level" data-level="tier-2" data-level-label="Intermediate" data-level-hint="review the validation mechanics">
        <h3>Intermediate</h3><span class="quiz-level-score badge badge-soft"></span>
        <p class="quiz-stem" data-i18n-pt="Onde a regra vive?" data-i18n-en="Where does the rule live?">Where does the rule live?</p>
        <button type="button" class="quiz-opt" data-i18n-pt="Somente na API" data-i18n-en="API only">API only</button>
        <button type="button" class="quiz-opt" data-correct="true" data-i18n-pt="No cliente (duplicando a regra)" data-i18n-en="Client-side (duplicating the rule)">Client-side (duplicating the rule)</button>
        <button type="button" class="quiz-opt" data-i18n-pt="Num serviço externo" data-i18n-en="External service">External service</button>
        <p class="quiz-why" data-i18n-pt="Decisão registrada: cliente por falta de contrato na API." data-i18n-en="Decision recorded: client-side because the API has no contract.">Decision recorded: client-side because the API has no contract.</p>
      </div>
      <div class="quiz-level" data-level="tier-3" data-level-label="Advanced" data-level-hint="review the accepted trade-off">
        <h3>Advanced</h3><span class="quiz-level-score badge badge-soft"></span>
        <p class="quiz-stem" data-i18n-pt="Qual trade-off foi aceito?" data-i18n-en="Which trade-off was accepted?">Which trade-off was accepted?</p>
        <button type="button" class="quiz-opt" data-i18n-pt="Latência maior" data-i18n-en="Higher latency">Higher latency</button>
        <button type="button" class="quiz-opt" data-correct="true" data-i18n-pt="Regra duplicada entre clientes" data-i18n-en="Rule duplicated across clients">Rule duplicated across clients</button>
        <button type="button" class="quiz-opt" data-i18n-pt="Mais chamadas de rede" data-i18n-en="More network calls">More network calls</button>
        <p class="quiz-why" data-i18n-pt="O trade-off está no relatório, formato causal." data-i18n-en="The trade-off is in the report, causal format.">The trade-off is in the report, causal format.</p>
      </div>
      <div class="quiz-level" data-level="tier-4" data-level-label="Hard" data-level-hint="review the edges and failures">
        <h3>Hard</h3><span class="quiz-level-score badge badge-soft"></span>
        <p class="quiz-stem" data-i18n-pt="Qual borda quebraria a validação atual?" data-i18n-en="Which edge case would break the current validation?">Which edge case would break the current validation?</p>
        <button type="button" class="quiz-opt" data-i18n-pt="E-mail com acento" data-i18n-en="Accented email">Accented email</button>
        <button type="button" class="quiz-opt" data-i18n-pt="Maiúsculas" data-i18n-en="Uppercase">Uppercase</button>
        <button type="button" class="quiz-opt" data-correct="true" data-i18n-pt="Domínio punycode" data-i18n-en="Punycode domain">Punycode domain</button>
        <p class="quiz-why" data-i18n-pt="Punycode está citado como pergunta aberta no relatório — borda real, não pegadinha." data-i18n-en="Punycode is cited as an open question in the report — a real edge, not a trick.">Punycode is cited as an open question in the report — a real edge, not a trick.</p>
      </div>
      </div>
"""


def build(kind: str, body: str) -> str:
    html = SKELETON
    html = html.replace("/* system.css is injected HERE whole — never via template engine */", CSS)
    marker = "<!-- ═══ ARTIFACT CONTENT ═══"
    end = "<!-- Dynamic quiz:"
    start = html.index(marker)
    end_idx = html.index(end)
    html = html[:start] + marker + "\n         (mechanically generated by build-demo.py)\n\n" + body + "\n\n    " + html[end_idx:]
    return html


def main() -> None:
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "quizzes"), exist_ok=True)
    report = build("report", REPORT_BODY)
    quiz = build("quiz", QUIZ_BODY)
    report_path = os.path.join(ROOT, "reports", "demo-report.html")
    quiz_path = os.path.join(ROOT, "quizzes", "demo-quiz.html")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report)
    with open(quiz_path, "w", encoding="utf-8") as fh:
        fh.write(quiz)
    for p in (report_path, quiz_path):
        size = os.path.getsize(p)
        print(f"OK {p} ({size} bytes)")


if __name__ == "__main__":
    sys.exit(main())
