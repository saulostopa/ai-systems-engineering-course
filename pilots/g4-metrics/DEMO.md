# Demo final — como apresentar cada harness ao vivo

> Guia da demo G4. Cada bloco é uma demonstração de 2-3 minutos com o
> comando real. A ordem conta: comece pelo básico e suba a complexidade.

## 0. Pré-requisitos

```sh
cd /home/svslwm/wm/harness-plannig
python3 -m area_harness index /tmp/opencode/area-financas --verbose   # contexto G3 (ou recrie)
```

## 1. Harness básico (2 min) — "o gate que trava o commit"

```sh
cd /tmp/opencode/pilot-g1          # repo piloto com harness-basic instalado
./scripts/validate-harness.sh      # → HARNESS OK
# demonstre o bloqueio: feature_list.json com 0 in_progress e tente commitar
node -e "const f=require('./feature_list.json');f.features[0].status='not_started';require('fs').writeFileSync('feature_list.json',JSON.stringify(f,null,2))"
git add feature_list.json && git commit -m "sem feature"   # → BLOQUEADO
```

**Frase-chave**: "o harness não impede o agente de errar — impede o erro de
entrar no repo."

## 2. App harness (3 min) — "o E2E é contrato de commit"

```sh
cd /tmp/opencode/pilot-g2
git reset -q && git add src/index.html && bash scripts/e2e-gate.sh
# → BLOQUEADO (mudança de frontend sem teste E2E)
git add tests/e2e/test_search.py && bash scripts/e2e-gate.sh
# → LIBERADO
```

**Frase-chave**: "não é 'não esqueça de testar' — é 'não existe commit de
frontend sem teste'."

## 3. Area Copilot (3 min) — "o harness que trabalha de madrugada"

```sh
cd /home/svslwm/wm/harness-plannig/area-copilot
HARNESS_QUESTIONS="qual o total de veiculos vendidos no sudeste em julho" \
  ../domains/finance/scripts/nightly-run.sh /tmp/opencode/area-financas
# → relatório publicado com FONTE: metas_2026.csv (linhas 2-15)
```

Abra `domains/finance/relatorios/YYYY-MM-DD-resumo.md` e aponte: **cada número
tem a planilha e a linha de origem**.

**Frase-chave**: "finanças roda o harness de madrugada e acha o relatório
pronto de manhã — com prova, não com 'acho que'."

## 4. Intranet de artefatos (2 min) — "o conhecimento vira corpus"

```sh
cd /home/svslwm/wm/harness-plannig/artifacts-intranet
python3 -m artifacts_intranet.server --port 8765 --reindex
# abre http://localhost:8765 — busca: "gatekeeper bloqueia commit"
```

**Frase-chave**: "cada relatório que o harness gera vira um card pesquisável —
com o tempo, isso é a memória da empresa."

## 5. Skills v2 (2 min) — "a peça de ouro"

```sh
open /home/svslwm/wm/harness-plannig/skills-artifacts/quizzes/demo-quiz.html
# 4 níveis, toggle EN/PT, tema claro/escuro; responda errado de propósito →
# a questão entra no modo de revisão (adaptativo)
```

**Frase-chave**: "a IA gera o relatório, o relatório ensina, e o quiz impede
que a pessoa perca a capacidade crítica."

## 6. RAG de código (2 min) — "a busca que acha a fonte"

```sh
cd /home/svslwm/wm/harness-plannig/rag-harness
python3 -m rag_harness eval ../harness-basic    # → Precisão@3: 5/5 = 1.0
python3 -m rag_harness agent ../harness-basic "como o gatekeeper bloqueia commit"
```

## Encerramento

> "Modelo é commodity; harness é a vantagem. Este curso entrega os dois lados:
> o conhecimento para construir o seu e os harnesses prontos para adotar —
> do repo pequeno ao Area Copilot da sua área."