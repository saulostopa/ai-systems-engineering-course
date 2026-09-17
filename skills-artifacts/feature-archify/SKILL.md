---
name: feature-archify
description: Gera diagramas verificáveis (workflow, sequence, dataflow, architecture, lifecycle) de uma feature recém-concluída, usando o Archify — para ensinar quem usa o harness o que foi construído e como flui. Use quando o usuário pedir diagrama, gráfico, flowchart ou mapa visual de uma feature/trabalho que acabou de ser concluído.
---

# Feature Archify — diagramas pós-conclusão

Quando um trabalho é concluído, o harness entrega dois artefatos de
aprendizado: o `feature-report` (o que foi entregue) e este — **o diagrama
que ensina como o que foi construído funciona**. Um diagrama Archify é
verificável (validado antes de entregar), interativo e autocontido (um HTML).

## Gather

- O relatório da feature (`reports/<slug>.html` da skill feature-report) — os fatos vêm dele.
- O diff/testes — para o tipo certo de diagrama (veja abaixo).
- A skill Archify instalada em `.agents/skills/archify/` (instale com `npx skills add tt-a1i/archify`).

## Escolha o tipo certo

| Trabalho concluído | Tipo de diagrama |
|---|---|
| Mudou um fluxo/pipeline (CI, aprovações, gates) | `workflow` |
| Mudou uma interação (API, cache, auth, async) | `sequence` |
| Mudou movimento de dados (ETL, lineage, PII) | `dataflow` |
| Mudou o sistema (componentes, serviços, fronteiras) | `architecture` |
| Mudou estados (retries, waits, terminais) | `lifecycle` |

## Write — o contrato de qualidade (lições deste curso)

1. **Leia um schema** (`schemas/<tipo>.schema.json` + `common.schema.json`) e **um exemplo** (`examples/<tipo>*.json`) antes de escrever — use o exemplo para a forma dos campos, nunca para os fatos.
2. **IDs novos, palavras do domínio, layout próprio** — nada de copiar geometria.
3. **mainPath só anda para frente** (col não decresce); loops e retornos viram arestas `role: branch/error` fora do mainPath.
4. **Sem sobreposição** (mesma lane + mesma col = conflito) e **sem longas verticais cruzando o meio** — se um gate de composição reclamar, ajuste a topologia (mova o nó de lane/col, roteie pela última coluna com `fromSide/toSide: right` + `route: outside-right` como no exemplo da skill), nunca ignore o diagnóstico.
5. **Cartões** (cards) para o detalhe que não cabe em arestas — inclusive o **que o leitor deve aprender** com o diagrama.

## Output — o ciclo obrigatório

```sh
node .agents/skills/archify/bin/archify.mjs validate workflow <slug>.json --quality showcase --json
# → corrija TODOS os diagnostics (cada um traz o supportedFixes) — revalide até válido
node .agents/skills/archify/bin/archify.mjs deliver workflow <slug>.json <slug>.html --quality showcase
# → "9/9 artifact checks; composition showcase: pass" é o critério de saída
```

- Salve o JSON (fonte reproduzível) e o HTML em `flowcharts/YYYY-MM-DD-<slug>/` (JSON + HTML).
- O HTML é o artefato: interativo, tema claro/escuro, exportação PNG/SVG.
- Aponte o leitor para as **views** (`#view=<id>`) — o caminho feliz e o caminho dos gates.

## Regras

- Nunca entregue HTML sem o `validate --json` com `composition: pass` — o renderizador bloqueia artefato ruim (é o gate da skill).
- Fatos do diagrama vêm do diff/relatório; nada de topologia inventada.
- Se o tipo de diagrama não está claro, prefira `workflow` (fluxo do trabalho) — é o que mais ensina.