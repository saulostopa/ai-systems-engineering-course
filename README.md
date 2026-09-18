# Harness Foundation Course — Webmotors

Curso de **Harness Engineering** + **sete harnesses funcionais** para a
Webmotors: básico, grande (multi-time), App, RAG de código, Area Copilot,
multi-domínio (games/finanças/comercial), skills de artefato e intranet.

Um agente é modelo + harness: este projeto entrega os dois lados — o
conhecimento para construir harnesses e os harnesses prontos para adotar.

## Como subir os 2 ambientes

### 1. Site do curso (VitePress)

```sh
npm install        # primeira vez (Node >= 22)
npm run dev        # http://localhost:5173 (ou use a porta abaixo se ocupada)
```

Se a porta 5173 estiver ocupada:

```sh
npx vitepress dev docs --port 5174
# → http://localhost:5174
```

Build de produção:

```sh
npm run build && npm run preview
```

## Ambientes extras

### 3. Intranet de artefatos (busca RAG)

```sh
cd artifacts-intranet
python3 -m artifacts_intranet.server --port 8765 --reindex
# → http://localhost:8765
```

### 4. Pilotos / demo ao vivo

Siga o `pilots/g4-metrics/DEMO.md` — 6 blocos de 2-3 minutos com os comandos
reais (harness básico, app, Area Copilot, intranet, skills, RAG).

### 5. Testes e avaliações

```sh
cd rag-harness && python3 tests/test_rag.py          # 7 testes do motor RAG
cd area-copilot && python3 tests/test_area.py        # 3 testes do Area Copilot
cd artifacts-intranet && python3 tests/test_intranet.py  # 3 testes da intranet
cd rag-harness && python3 -m rag_harness eval ../harness-basic   # precisão@k
cd hard-harness && PYTHONPATH=. python3 tests/test_hard_harness.py   # 19 testes do núcleo
harness-basic/tests/test_skill_guard.sh              # 13 testes do gate de skills
```

### 6. Instalar uma skill de fora

Nenhuma skill de terceiro entra sem passar pelo scanner
([SkillSpector](https://github.com/NVIDIA/SkillSpector), NVIDIA):

```sh
harness-basic/scripts/gate-skill-scan.sh https://github.com/user/skill   # escaneie ANTES de baixar
harness-basic/scripts/gate-skill-scan.sh --all                          # todas as skills do repo
```

Bloqueia score > 50 (exit 1). Requer Docker — a imagem é construída na
primeira execução. Veja `docs/skills/skill-guard.md` e
`pilots/skillspector-demo/`.

## Estrutura

| Pasta | O que é |
|---|---|
| `docs/` | O site do curso (aulas, projetos, biblioteca, designs) |
| `harness-basic/` | Harness básico instalável (templates + gates) |
| `app-harness/` | App harness: gate E2E + skill de navegação agêntica |
| `rag-harness/` | Motor RAG híbrido (AST chunks, cache, RRF, agente) |
| `area-copilot/` | RAG de contexto de negócio (fontes citadas) |
| `domains/` | Playbooks multi-domínio (games, finanças, comercial) |
| `skills-artifacts/` | Skills v2 de artefato + quiz (Eleanor, a11y, adaptativo) |
| `artifacts-intranet/` | Intranet com busca RAG sobre os artefatos |
| `templates/` | Pacote de templates do harness básico |
| `pilots/` | Evidências dos pilotos G1–G4 + demo final |
| `hard-harness/` | Orquestração executável: grafo, schemas, gates, persistência (19 testes) |

## Fluxo de trabalho

- **Branch de integração**: `develop` (default). **Release**: `main`.
- Todo trabalho novo entra por **PR para `develop`**.
- O trabalho pode ser acompanhado pelas issues, pull requests e workflows do
  GitHub.

## Referências

- Plano original: [`plan-harness-foundation-course.md`](plan-harness-foundation-course.md)
- Relatório final: [`pilots/g4-metrics/G4-FINAL-REPORT.html`](pilots/g4-metrics/G4-FINAL-REPORT.html)
- Demo ao vivo: [`pilots/g4-metrics/DEMO.md`](pilots/g4-metrics/DEMO.md)
