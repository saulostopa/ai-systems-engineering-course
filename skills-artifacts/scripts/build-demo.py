#!/usr/bin/env python3
"""build-demo.py — mechanical proof of the v2 assets (SSTT + a11y + i18n).

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

# One real trip, four stages. Four and not five: the track is a single row, and
# the v1 demo put its fifth stage off-screen on load — a stage a reader never
# sees is a stage that is not in the artifact.
ANIMATION_BODY = """\
    <section class="card" id="flow-root" aria-label="Flow">
      <h2 data-i18n="flow-title" data-i18n-pt="Um commit atravessando os gates" data-i18n-en="One commit travelling through the gates">One commit travelling through the gates</h2>
      <div class="flow-track" id="flow-track">
        <div class="flow-packet" id="flow-packet" aria-hidden="true"></div>
      <div class="flow-stage" data-caption-en="The developer stages a component change. Nothing has been verified yet — this is just intent." data-caption-pt="A pessoa prepara uma mudança de componente. Nada foi verificado ainda — isto é só intenção.">
        <div class="stage-label">git commit</div>
        <div class="stage-data">src/components/price-tag.tsx</div>
      </div>
      <span class="flow-arrow" aria-hidden="true">&#8594;</span>
      <div class="flow-stage" data-caption-en="The gatekeeper reads feature_list.json: exactly one feature in_progress, so the scope was declared before the edit." data-caption-pt="O gatekeeper lê o feature_list.json: exatamente uma feature in_progress, então o escopo foi declarado antes da edição.">
        <div class="stage-label">gatekeeper.sh</div>
        <div class="stage-data">1 in_progress &#10003;</div>
      </div>
      <span class="flow-arrow" aria-hidden="true">&#8594;</span>
      <div class="flow-stage" data-caption-en="A frontend file was staged, so the E2E gate looks for the test that covers it — and finds it in the same commit." data-caption-pt="Um arquivo de frontend foi preparado, então o gate de E2E procura o teste que o cobre — e acha no mesmo commit.">
        <div class="stage-label">e2e-gate.sh</div>
        <div class="stage-data">e2e/test_price.py &#10003;</div>
      </div>
      <span class="flow-arrow" aria-hidden="true">&#8594;</span>
      <div class="flow-stage" data-caption-en="Both gates agreed, so the commit exists. Nothing here trusted a promise: each step read a file." data-caption-pt="Os dois gates concordaram, então o commit existe. Nada aqui confiou numa promessa: cada passo leu um arquivo.">
        <div class="stage-label">commit</div>
        <div class="stage-data">a1b2c3d feature/OEM-123</div>
      </div>
      </div>
      <div class="flow-controls">
        <button type="button" class="flow-btn" id="flow-play">
          <span data-i18n="flow-play" data-i18n-pt="Reproduzir" data-i18n-en="Play">Play</span>
        </button>
        <button type="button" class="flow-btn" id="flow-step">
          <span data-i18n="flow-step" data-i18n-pt="Avan&ccedil;ar" data-i18n-en="Step">Step</span>
        </button>
        <p class="flow-caption" id="flow-caption" role="status" aria-live="polite">Step 1 of 4 &#8212; The developer stages a component change. Nothing has been verified yet — this is just intent.</p>
      </div>
    </section>
"""

# The consent-to-identity journey, as the product team bridge actually implements
# it — the Fuse CMP over IAB TCF v2, not the AdFixus sample banner. Grounded in
# ignition-adfixus-tag-docs; the caveat card is the measured Brazilian result,
# and it is the whole reason this artifact is worth having.
CONSENT_BODY = """\
    <section class="card" id="flow-root" aria-label="Flow">
      <h2 data-i18n="flow-title" data-i18n-pt="Do consentimento &agrave; identidade" data-i18n-en="From consent to identity">From consent to identity</h2>
      <div class="flow-track" id="flow-track">
        <div class="flow-packet" id="flow-packet" aria-hidden="true"></div>
      <div class="flow-stage" data-caption-en="The page registers a listener on the CMP. Nothing has been asked of the visitor yet — this is the bridge waiting." data-caption-pt="A página registra um listener no CMP. Nada foi perguntado ao visitante ainda — esta é a ponte esperando.">
        <div class="stage-label">__tcfapi</div>
        <div class="stage-data">addEventListener</div>
      </div>
      <span class="flow-arrow" aria-hidden="true">&#8594;</span>
      <div class="flow-stage" data-caption-en="The visitor answered the banner. The CMP fires with a TC string, and the bridge reads Purpose 1 from it." data-caption-pt="O visitante respondeu ao banner. O CMP dispara com uma TC string, e a ponte lê o Purpose 1 dela.">
        <div class="stage-label">Fuse CMP</div>
        <div class="stage-data">useractioncomplete</div>
      </div>
      <span class="flow-arrow" aria-hidden="true">&#8594;</span>
      <div class="flow-stage" data-caption-en="Purpose 1 is granted, so the bridge calls AfxIdentity. A Deny here would call doNotTrack() instead — the same branch, the other way." data-caption-pt="O Purpose 1 foi concedido, então a ponte chama o AfxIdentity. Um Deny aqui chamaria doNotTrack() — o mesmo ramo, para o outro lado.">
        <div class="stage-label">anonymousLogin()</div>
        <div class="stage-data">Purpose 1 granted</div>
      </div>
      <span class="flow-arrow" aria-hidden="true">&#8594;</span>
      <div class="flow-stage" data-caption-en="AdFixus issues the durable identifier and writes the profile cookie. From here the visitor is the same person across sessions." data-caption-pt="O AdFixus emite o identificador durável e grava o cookie de perfil. Daqui em diante o visitante é a mesma pessoa entre sessões.">
        <div class="stage-label">afx_profile</div>
        <div class="stage-data">acid issued</div>
      </div>
      <span class="flow-arrow" aria-hidden="true">&#8594;</span>
      <div class="flow-stage" data-caption-en="enablePpid() pushes the acid into GAM as the PPID. That is the moment the identity stops being ours alone." data-caption-pt="O enablePpid() empurra o acid para o GAM como PPID. É o momento em que a identidade deixa de ser só nossa.">
        <div class="stage-label">GAM</div>
        <div class="stage-data">setPublisherProvidedId(acid)</div>
      </div>
      </div>
      <div class="flow-controls">
        <button type="button" class="flow-btn" id="flow-play">
          <span data-i18n="flow-play" data-i18n-pt="Reproduzir" data-i18n-en="Play">Play</span>
        </button>
        <button type="button" class="flow-btn" id="flow-step">
          <span data-i18n="flow-step" data-i18n-pt="Avan&ccedil;ar" data-i18n-en="Step">Step</span>
        </button>
        <p class="flow-caption" id="flow-caption" role="status" aria-live="polite">Step 1 of 5 &#8212; The page registers a listener on the CMP. Nothing has been asked of the visitor yet — this is the bridge waiting.</p>
      </div>
    </section>
    <section class="card" aria-label="Where this stops today">
      <h2 data-i18n="caveat-title" data-i18n-pt="Onde isso para hoje, no Brasil" data-i18n-en="Where this stops today, in Brazil">Where this stops today, in Brazil</h2>
      <p data-i18n="caveat-1" data-i18n-pt="Medido em 15/09/2026, de S&atilde;o Paulo: o CMP invoca o listener exatamente uma vez, com gdprApplies: false, sem objeto de purposes e sem tcString. Nenhum banner &eacute; renderizado, porque o CMP decide corretamente que o GDPR est&aacute; fora de escopo para um visitante brasileiro." data-i18n-en="Measured on 2026-09-15 from S&atilde;o Paulo: the CMP invokes the listener exactly once, with gdprApplies: false, no purpose object and no tcString. No banner is rendered, because the CMP correctly decides GDPR is out of scope for a Brazilian visitor.">Measured on 2026-09-15 from S&atilde;o Paulo: the CMP invokes the listener exactly once, with gdprApplies: false, no purpose object and no tcString. No banner is rendered, because the CMP correctly decides GDPR is out of scope for a Brazilian visitor.</p>
      <p data-i18n="caveat-2" data-i18n-pt="A ponte filtra por eventStatus 'tcloaded' ou 'useractioncomplete', e nenhum dos dois chega. A jornada acima nunca passa do passo 1 para a nossa maior audi&ecirc;ncia. N&atilde;o &eacute; defeito do c&oacute;digo: TCF &eacute; um instrumento de GDPR, e o Brasil &eacute; regido pela LGPD, que o TCF n&atilde;o modela." data-i18n-en="The bridge filters on eventStatus 'tcloaded' or 'useractioncomplete', and neither ever arrives. The journey above never gets past stage 1 for our largest audience. This is not a defect in the code: TCF is a GDPR instrument, and Brazil is governed by the LGPD, which TCF does not model.">The bridge filters on eventStatus 'tcloaded' or 'useractioncomplete', and neither ever arrives. The journey above never gets past stage 1 for our largest audience. This is not a defect in the code: TCF is a GDPR instrument, and Brazil is governed by the LGPD, which TCF does not model.</p>
      <p><span class="badge badge-solid">OPEN</span> <span class="badge badge-soft" data-i18n="caveat-3" data-i18n-pt="pergunta em aberto com o AdFixus" data-i18n-en="open question with AdFixus">open question with AdFixus</span></p>
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
    # The marker is the OPENING of an HTML comment. Re-emitting it without
    # closing it swallowed every generated section into that comment — the file
    # looked fine (18 KB, "OK") and rendered an empty shell. Close it here.
    html = (
        html[:start]
        + marker
        + "\n         (mechanically generated by build-demo.py) -->\n\n"
        + body
        + "\n\n    "
        + html[end_idx:]
    )
    return html


COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def verify(kind: str, html: str) -> None:
    """Assert the content actually survives outside HTML comments.

    Writing bytes is not evidence that a browser will show them. This checks
    the rendered-visible portion, which is the only thing a reader gets.
    """
    if html.count("<!--") != html.count("-->"):
        raise SystemExit(f"FAIL {kind}: unbalanced HTML comments — content would be swallowed")

    visible = COMMENT.sub("", html)
    expected = {
        "report": [("section class=\"card\"", 5), ("<table", 1)],
        "quiz": [("quiz-level\"", 4), ("quiz-opt", 12)],
        "animation": [("flow-stage\"", 4), ("data-caption-en", 4), ("flow-arrow", 3)],
        "consent": [("flow-stage\"", 5), ("data-caption-en", 5), ("flow-arrow", 4)],
    }[kind]
    for needle, minimum in expected:
        found = visible.count(needle)
        if found < minimum:
            raise SystemExit(
                f"FAIL {kind}: expected >= {minimum} of {needle!r} outside comments, found {found}"
            )
    print(f"   verified: {kind} content is visible (not inside a comment)")


def main() -> None:
    # The site serves docs/public/demos, so that is where a rendered demo
    # lives — full stop. Keeping a second copy under skills-artifacts meant two
    # byte-identical files in git and a guarantee they would drift.
    out = os.path.join(os.path.dirname(ROOT), "docs", "public", "demos")
    os.makedirs(out, exist_ok=True)
    report = build("report", REPORT_BODY)
    quiz = build("quiz", QUIZ_BODY)
    animation = build("animation", ANIMATION_BODY)
    consent = build("consent", CONSENT_BODY)
    # Verify before writing: an artifact that fails the check must never reach
    # disk, or the next reader inherits a file that looks delivered.
    verify("report", report)
    verify("quiz", quiz)
    verify("animation", animation)
    verify("consent", consent)
    report_path = os.path.join(out, "demo-report.html")
    quiz_path = os.path.join(out, "demo-quiz.html")
    animation_path = os.path.join(out, "demo-animation.html")
    consent_path = os.path.join(out, "demo-consent-journey.html")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report)
    with open(quiz_path, "w", encoding="utf-8") as fh:
        fh.write(quiz)
    with open(animation_path, "w", encoding="utf-8") as fh:
        fh.write(animation)
    with open(consent_path, "w", encoding="utf-8") as fh:
        fh.write(consent)
    for p in (report_path, quiz_path, animation_path, consent_path):
        size = os.path.getsize(p)
        print(f"OK {p} ({size} bytes)")


if __name__ == "__main__":
    sys.exit(main())
