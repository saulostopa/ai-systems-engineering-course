#!/usr/bin/env python3
"""build-report-g4.py — relatório final G4 renderizado com os assets v2 (F1).

Dogfooding: o relatório final do projeto usa a mesma skill que o curso ensina
(feature-report v2 — Eleanor, a11y, i18n). Uso: python3 report.py
"""

from __future__ import annotations

import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(ROOT, "..", "..", "skills-artifacts", "assets"))
CSS = open(os.path.join(ASSETS, "system.css"), encoding="utf-8").read()
SKELETON = open(os.path.join(ASSETS, "skeleton.html"), encoding="utf-8").read()

METRICS = """\
    <section class="card" aria-label="O que foi entregue">
      <h2 data-i18n-pt="O que foi entregue" data-i18n-en="What was delivered">O que foi entregue</h2>
      <p>O Harness Foundation Course — um curso completo e <b>sete harnesses funcionais</b> para a Webmotors, construídos e validados com o próprio método que ensinam.</p>
      <p><span class="badge badge-solid">7 EPICs</span> <span class="badge badge-solid">21 stories</span> <span class="badge badge-soft">19 PRs</span> <span class="badge badge-soft">26/28 itens DONE</span></p>
    </section>
    <section class="card" aria-label="Métricas por harness">
      <h2 data-i18n-pt="Métricas por harness" data-i18n-en="Metrics per harness">Métricas por harness</h2>
      <table>
        <thead><tr><th>Harness</th><th>Evidência</th><th>Métrica</th></tr></thead>
        <tbody>
          <tr><td>Básico (B1)</td><td>piloto G1 em repo real</td><td>2→4 testes sem redução; gatekeeper bloqueou 2x corretamente</td></tr>
          <tr><td>Grande (B2)</td><td>blueprint 4 camadas</td><td>governança + workflow + observabilidade documentados</td></tr>
          <tr><td>App (C1+C2)</td><td>piloto G2</td><td>frontend sem E2E BLOQUEADO; com E2E LIBERADO; navegação HTTP 200</td></tr>
          <tr><td>RAG código (D1+D2)</td><td>eval em harness-basic</td><td>precisão@3 = 5/5 (1.0); 7 testes</td></tr>
          <tr><td>Area Copilot (D3)</td><td>eval + piloto G3</td><td>precisão 3/3 (1.0) com fontes citadas</td></tr>
          <tr><td>Finance (E3)</td><td>nightly-run real</td><td>relatório publicado com 9 fontes; gate de saída PASS</td></tr>
          <tr><td>Games (E2)</td><td>playteste simulado</td><td>ACEITO com doc válido; REJEITADO sem critérios</td></tr>
          <tr><td>Comercial (E4)</td><td>proposal-check</td><td>APROVADA (0 falhas) / BLOQUEADA (4) — testes pos/neg</td></tr>
          <tr><td>Skills v2 (F1)</td><td>build-demo mecânico</td><td>4 níveis/12 opções/4 corretas; a11y + i18n + quiz adaptativo</td></tr>
          <tr><td>Intranet (F2)</td><td>E2E com curl</td><td>busca "gatekeeper bloqueia" → docs certos com tools</td></tr>
        </tbody>
      </table>
    </section>
    <section class="card" aria-label="Achados reais que melhoraram os harnesses">
      <h2 data-i18n-pt="Achados reais que melhoraram os harnesses" data-i18n-en="Real findings that improved the harnesses">Achados reais que melhoraram os harnesses</h2>
      <ul>
        <li>G1: gatekeeper bloqueava a própria atualização de feature_list → melhoria recomendada (commits só-de-estado).</li>
        <li>G2: porta 3000 ocupada pelo dev server → parametrizar PORT.</li>
        <li>D2: acentos e camelCase quebravam busca léxica → tokenizer normalizado (2/5 → 5/5).</li>
        <li>E2: grep case-sensitive reprovava docs válidos → fix (-i) achado por teste.</li>
        <li>E3: números fora do bloco FONTE → gate de saída por bloco (awk).</li>
      </ul>
    </section>
    <section class="card" aria-label="Decisões e trade-offs">
      <h2 data-i18n-pt="Decisões e trade-offs" data-i18n-en="Decisions and trade-offs">Decisões e trade-offs</h2>
      <p>Escolhido RAG com NGram local em vez de Ollama/pgvector porque a POC valida arquitetura sem infra, ao custo de semântica real só com provider externo — ligável via OLLAMA_API_URL.</p>
      <p>Escolhida infra pesada adiada (watcher/fila/pgvector) em vez de construir cedo porque a regra do rag-harness.md manda decidir por evidência, ao custo de re-indexação sob demanda até o EPIC G provar a dor.</p>
      <p>Escolhido AgEnFK escopado ao projeto em vez de global porque independência entre agentes é inegociável, ao custo de manter a gestão só neste repo.</p>
    </section>
    <section class="card" aria-label="Perguntas abertas">
      <h2 data-i18n-pt="Perguntas abertas" data-i18n-en="Open questions">Perguntas abertas</h2>
      <p>Quando o RAG de negócio ganha dados reais de uma área Webmotors? Qual área pilota primeiro o Area Copilot (finanças, comercial, games)? O harness básico vira pacote npm/instalador global do time?</p>
    </section>
"""


def build() -> str:
    html = SKELETON
    html = html.replace("/* system.css é injetado AQUI inteiro — nunca via template engine */", CSS)
    marker = "<!-- ═══ CONTEÚDO DO ARTEFATO ═══"
    end = "<!-- Quiz dinâmico:"
    start = html.index(marker)
    end_idx = html.index(end)
    html = html[:start] + marker + "\n         (gerado por report.py — skill feature-report v2)\n\n" + METRICS + "\n\n    " + html[end_idx:]
    return html


def main() -> None:
    out = os.path.join(ROOT, "G4-FINAL-REPORT.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(build())
    print(f"OK {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    main()