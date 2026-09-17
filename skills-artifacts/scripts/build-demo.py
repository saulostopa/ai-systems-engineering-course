#!/usr/bin/env python3
"""build-demo.py — prova mecânica dos assets v2 (Eleanor + a11y + i18n).

Monta o artefato do mesmo jeito que a skill faz: injeta system.css no bloco
<style> do skeleton.html e o conteúdo no <main>. Gera report + quiz demo.

Uso: python3 scripts/build-demo.py
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSS = open(os.path.join(ROOT, "assets", "system.css"), encoding="utf-8").read()
SKELETON = open(os.path.join(ROOT, "assets", "skeleton.html"), encoding="utf-8").read()

REPORT_BODY = """\
    <section class="card" aria-label="O que foi entregue">
      <h2 data-i18n="s1" data-i18n-pt="O que foi entregue" data-i18n-en="What was delivered">O que foi entregue</h2>
      <p>Adicionada validação de e-mail no formulário de busca de concessionárias.</p>
      <p><span class="badge badge-solid">ENTREGUE</span> <span class="badge badge-soft">sem regressão</span></p>
    </section>
    <section class="card" aria-label="Decisões e trade-offs">
      <h2 data-i18n="s2" data-i18n-pt="Decisões e trade-offs" data-i18n-en="Decisions and trade-offs">Decisões e trade-offs</h2>
      <p>Escolhido regex do lado do cliente em vez de validação por API porque o endpoint já existia sem esse contrato, ao custo de duplicar a regra entre clientes.</p>
    </section>
    <section class="card" aria-label="Verificação">
      <h2 data-i18n="s3" data-i18n-pt="Verificação" data-i18n-en="Verification">Verificação</h2>
      <table>
        <thead><tr><th>Comando</th><th>Esperado</th><th>Real</th></tr></thead>
        <tbody>
          <tr><td><code>npm run build</code></td><td>exit 0</td><td>exit 0</td></tr>
          <tr><td><code>npm test</code></td><td>12 testes verdes</td><td>12 verdes (sem redução)</td></tr>
          <tr><td><code>pytest tests/e2e -q</code></td><td>2 verdes</td><td>2 verdes</td></tr>
        </tbody>
      </table>
    </section>
    <section class="card" aria-label="Perguntas abertas">
      <h2 data-i18n="s4" data-i18n-pt="Perguntas abertas" data-i18n-en="Open questions">Perguntas abertas</h2>
      <p>A regra deve migrar para a API quando o contrato existir? Quem decide o limite de formato (ex.: domínios punycode)?</p>
    </section>
"""

QUIZ_BODY = """\
      <div id="quiz-levels">
      <div class="quiz-level" data-level="tier-1" data-level-label="Básico" data-level-hint="revise o que a feature faz">
        <h3>Básico</h3><span class="quiz-level-score badge badge-soft"></span>
        <p class="quiz-stem" data-i18n-pt="O que a feature valida?" data-i18n-en="What does the feature validate?">O que a feature valida?</p>
        <button type="button" class="quiz-opt" data-correct="true" data-i18n-pt="Formato de e-mail no formulário" data-i18n-en="Email format in the form">Formato de e-mail no formulário</button>
        <button type="button" class="quiz-opt" data-i18n-pt="Senha forte" data-i18n-en="Strong password">Senha forte</button>
        <button type="button" class="quiz-opt" data-i18n-pt="CEP válido" data-i18n-en="Valid ZIP code">CEP válido</button>
        <p class="quiz-why" data-i18n-pt="O relatório declara a entrega como validação de e-mail." data-i18n-en="The report declares the delivery as email validation.">O relatório declara a entrega como validação de e-mail.</p>
      </div>
      <div class="quiz-level" data-level="tier-2" data-level-label="Intermediário" data-level-hint="revise a mecânica da validação">
        <h3>Intermediário</h3><span class="quiz-level-score badge badge-soft"></span>
        <p class="quiz-stem" data-i18n-pt="Onde a regra vive?" data-i18n-en="Where does the rule live?">Onde a regra vive?</p>
        <button type="button" class="quiz-opt" data-i18n-pt="Somente na API" data-i18n-en="API only">Somente na API</button>
        <button type="button" class="quiz-opt" data-correct="true" data-i18n-pt="No cliente (duplicando a regra)" data-i18n-en="Client-side (duplicating the rule)">No cliente (duplicando a regra)</button>
        <button type="button" class="quiz-opt" data-i18n-pt="Num serviço externo" data-i18n-en="External service">Num serviço externo</button>
        <p class="quiz-why" data-i18n-pt="Decisão registrada: cliente por falta de contrato na API." data-i18n-en="Decision recorded: client-side because the API has no contract.">Decisão registrada: cliente por falta de contrato na API.</p>
      </div>
      <div class="quiz-level" data-level="tier-3" data-level-label="Avançado" data-level-hint="revise o trade-off aceito">
        <h3>Avançado</h3><span class="quiz-level-score badge badge-soft"></span>
        <p class="quiz-stem" data-i18n-pt="Qual trade-off foi aceito?" data-i18n-en="Which trade-off was accepted?">Qual trade-off foi aceito?</p>
        <button type="button" class="quiz-opt" data-i18n-pt="Latência maior" data-i18n-en="Higher latency">Latência maior</button>
        <button type="button" class="quiz-opt" data-correct="true" data-i18n-pt="Regra duplicada entre clientes" data-i18n-en="Rule duplicated across clients">Regra duplicada entre clientes</button>
        <button type="button" class="quiz-opt" data-i18n-pt="Mais chamadas de rede" data-i18n-en="More network calls">Mais chamadas de rede</button>
        <p class="quiz-why" data-i18n-pt="O trade-off está no relatório, formato causal." data-i18n-en="The trade-off is in the report, causal format.">O trade-off está no relatório, formato causal.</p>
      </div>
      <div class="quiz-level" data-level="tier-4" data-level-label="Difícil" data-level-hint="revise as bordas e falhas">
        <h3>Difícil</h3><span class="quiz-level-score badge badge-soft"></span>
        <p class="quiz-stem" data-i18n-pt="Qual borda quebraria a validação atual?" data-i18n-en="Which edge case would break the current validation?">Qual borda quebraria a validação atual?</p>
        <button type="button" class="quiz-opt" data-i18n-pt="E-mail com acento" data-i18n-en="Accented email">E-mail com acento</button>
        <button type="button" class="quiz-opt" data-i18n-pt="Maiúsculas" data-i18n-en="Uppercase">Maiúsculas</button>
        <button type="button" class="quiz-opt" data-correct="true" data-i18n-pt="Domínio punycode" data-i18n-en="Punycode domain">Domínio punycode</button>
        <p class="quiz-why" data-i18n-pt="Punycode está citado como pergunta aberta no relatório — borda real, não pegadinha." data-i18n-en="Punycode is cited as an open question in the report — a real edge, not a trick.">Punycode está citado como pergunta aberta no relatório — borda real, não pegadinha.</p>
      </div>
      </div>
"""


def build(kind: str, body: str) -> str:
    html = SKELETON
    html = html.replace("/* system.css é injetado AQUI inteiro — nunca via template engine */", CSS)
    marker = "<!-- ═══ CONTEÚDO DO ARTEFATO ═══"
    end = "<!-- Quiz dinâmico:"
    start = html.index(marker)
    end_idx = html.index(end)
    html = html[:start] + marker + "\n         (gerado mecanicamente por build-demo.py)\n\n" + body + "\n\n    " + html[end_idx:]
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