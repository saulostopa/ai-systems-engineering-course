# Intranet de artefatos — pacote

```
artifacts-intranet/
├── artifacts_intranet/
│   ├── __init__.py        # path setup (motor rag_harness)
│   ├── indexer.py         # varre dirs de artefatos, indexa (HTML/MD/TXT) no rag_harness
│   └── server.py          # servidor stdlib: / (UI) e /search?q= (JSON)
├── index.html             # UI Eleanor (system.css v2 reutilizado)
├── tests/test_intranet.py # 3 testes
└── README.md
```

## Uso

```sh
python3 -m artifacts_intranet index   # indexa os dirs configurados (repo)
python3 -m artifacts_intranet serve   # http://localhost:8765
# UI: busca com RAG híbrido (léxico + semântico + RRF)
# API: GET /search?q=gatekeeper bloqueia
```

## Idéia (Story F2)

Os artefatos (reports, quizzes, flowcharts, relatórios de área) viram o
**corpus de conhecimento da empresa** (Aula 03: repo como sistema de registro;
Aula 11: observabilidade). A intranet é a porta de entrada: busca RAG sobre
tudo que o harness gerou — com fonte citada, como tudo neste projeto.