# Final demo — how to present each harness live

> G4 demo guide. Each block is a 2-3 minute demonstration with the real
> command. Order matters: start with the basic one and build up complexity.

## 0. Prerequisites

```sh
cd /home/svslwm/wm/harness-plannig
python3 -m area_harness index /tmp/opencode/area-financas --verbose   # G3 context (or recreate it)
```

## 1. Basic harness (2 min) — "the gate that blocks the commit"

```sh
cd /tmp/opencode/pilot-g1          # pilot repo with harness-basic installed
./scripts/validate-harness.sh      # → HARNESS OK
# demonstrate the block: feature_list.json with 0 in_progress and try to commit
node -e "const f=require('./feature_list.json');f.features[0].status='not_started';require('fs').writeFileSync('feature_list.json',JSON.stringify(f,null,2))"
git add feature_list.json && git commit -m "sem feature"   # → BLOCKED
```

**Key phrase**: "the harness doesn't stop the agent from making mistakes — it
stops the mistake from entering the repo."

## 2. App harness (3 min) — "the E2E is the commit contract"

```sh
cd /tmp/opencode/pilot-g2
git reset -q && git add src/index.html && bash scripts/e2e-gate.sh
# → BLOCKED (frontend change without an E2E test)
git add tests/e2e/test_search.py && bash scripts/e2e-gate.sh
# → ALLOWED
```

**Key phrase**: "it's not 'don't forget to test' — it's 'there is no frontend
commit without a test'."

## 3. Area Copilot (3 min) — "the harness that works overnight"

```sh
cd /home/svslwm/wm/harness-plannig/area-copilot
HARNESS_QUESTIONS="qual o total de veiculos vendidos no sudeste em julho" \
  ../domains/finance/scripts/nightly-run.sh /tmp/opencode/area-financas
# → report published with FONTE: metas_2026.csv (linhas 2-15)
```

Open `domains/finance/relatorios/YYYY-MM-DD-resumo.md` and point out: **every
number has its source spreadsheet and line**.

**Key phrase**: "finance runs the harness overnight and finds the report ready
in the morning — with proof, not with 'I think so'."

## 4. Artifacts intranet (2 min) — "knowledge becomes a corpus"

```sh
cd /home/svslwm/wm/harness-plannig/artifacts-intranet
python3 -m artifacts_intranet.server --port 8765 --reindex
# open http://localhost:8765 — search: "gatekeeper bloqueia commit"
```

**Key phrase**: "every report the harness generates becomes a searchable card
— over time, that is the company's memory."

## 5. Skills v2 (2 min) — "the crown jewel"

```sh
open /home/svslwm/wm/harness-plannig/skills-artifacts/quizzes/demo-quiz.html
# 4 levels, EN/PT toggle, light/dark theme; answer wrong on purpose →
# the question enters review mode (adaptive)
```

**Key phrase**: "the AI generates the report, the report teaches, and the quiz
stops people from losing their critical thinking."

## 6. Code RAG (2 min) — "the search that finds the source"

```sh
cd /home/svslwm/wm/harness-plannig/rag-harness
python3 -m rag_harness eval ../harness-basic    # → Precision@3: 5/5 = 1.0
python3 -m rag_harness agent ../harness-basic "como o gatekeeper bloqueia commit"
```

## Closing

> "Model is commodity; harness is the advantage. This course delivers both
> sides: the knowledge to build your own and the ready-to-adopt harnesses —
> from the small repo to the Area Copilot of your area."