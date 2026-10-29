---
title: Projeto 06 — harness ADK + RAG + Jev
---

# Projeto 06 — harness ADK + RAG + Jev

> Um workflow agêntico determinístico em que decisões tipadas escolhem políticas de recuperação, roteiam modelos e filtram ferramentas enquanto o código permanece no controle.

## Objetivo

Construir o `adk-rag-harness` como um projeto de composição implementando o princípio central: **"O LLM escreve, o Jev decide"** (veja a [referência do Jev](/pt-BR/reference/jev)). O Google ADK controla o grafo de workflow e o runtime agêntico, o subsistema RAG controla a recuperação de evidências, e o Jev avalia decisões delimitadas através dos 4 pilares operacionais (**Rotear, Filtrar, Pontuar e Liberar**) antes do código rotear a execução.

O `rag-harness` existente continua utilizável sem ADK ou Jev. Este projeto adiciona uma fronteira de adapter sem mover os internals de RAG para a camada de orquestração.

## Arquitetura e Fatias

### Fatia 1 — Política de Recuperação e Portão de Evidências
Implementar e avaliar:
1. se a recuperação externa é necessária (`direct` vs `retrieve` vs `clarify`);
2. qual coleção ou estratégia de busca usar;
3. se as evidências são suficientes para responder (`sufficient` vs `blocked`).

Usar as decisões tipadas Noul, Choice e Score do Jev. Aplicar limiares no código e manter caminhos determinísticos para baixa confiança, falhas do provedor e evidências contraditórias.

### Fatia 2 — Evolução dos 4 Pilares de Decisão
1. **Rotear**: Roteamento dinâmico de modelos avaliando a complexidade da intenção para escolher LLM Pequeno ($) vs LLM Grande ($$$).
2. **Filtrar**: Guardrail pré-LLM bloqueando injeções de prompt sem queimar tokens generativos; Filtro de Tool Calls autorizando entre `permite`, `pergunta` (confirmação HITL) ou `nega`.
3. **Pontuar**: Reranking de trechos recuperados pelo RAG; avaliação inline de resposta validando aderência factual contra as fontes.
4. **Liberar**: Portão de execução tripartite no código de política:
   - alta confiança ($\ge 0.85$): executa;
   - média confiança ($0.50$ a $0.84$): confirma com o usuário;
   - baixa confiança ($< 0.50$): revisão humana (HITL).

## Estrutura sugerida

```text
adk-rag-harness/
├── adk_rag_harness/
│   ├── agent.py
│   ├── workflow.py
│   ├── decision/
│   │   ├── interface.py
│   │   ├── jev_adapter.py
│   │   ├── guardrail.py
│   │   └── model_router.py
│   ├── policies/
│   │   ├── tripartite_threshold.py
│   │   └── tool_policy.py
│   ├── tools/rag_tool.py
│   └── validators/
├── rag_adapter/client.py
└── tests/
    ├── test_decision_policy.py
    ├── test_retrieval_routing.py
    ├── test_guardrail_filter.py
    ├── test_model_routing.py
    ├── test_tool_call_gate.py
    ├── test_low_confidence_fallback.py
    ├── test_adversarial_state.py
    └── test_full_trajectory.py
```

## Critérios de conclusão

- A interface do provedor funciona em testes sem rede.
- As decisões registram pergunta, resposta, confiança, limiar e rota escolhida.
- Entradas adversariais e injeções de prompt são bloqueadas pelo guardrail sem consumo de tokens de LLM.
- Requisições diretas simples são roteadas para um modelo leve enquanto sínteses densas vão para o tier de raciocínio.
- Chamadas de ferramentas impõem as fronteiras de `permite` / `pergunta` / `nega`.
- Cada resultado de recuperação mantém referências às fontes e passa por reranking antes da síntese.
- Limiares de confiança tripartites (`executa`, `confirma`, `humano`) são aplicados no código.
- A avaliação informa precisão do roteamento, qualidade da recuperação, citações, latência, custo e taxa de fallback.

## Implementação atual

A fatia local está no [projeto standalone `adk-rag-harness`](https://github.com/saulostopa/harnesses/tree/main/adk-rag-harness) e inclui o entrypoint do Dev UI do
ADK. Depois de clonar o catálogo standalone, instale com `uv sync --extra adk --extra openrouter` e inicie
com `uv run adk web`. Por padrão, tanto o modelo de conversa quanto o provider
de decisão tipada (`openrouter-system-one`) usam o Jev pelo OpenRouter
(`typesafe/jev-router`); basta uma chave do OpenRouter em `OPENROUTER_API_KEY`
ou em `~/.local/share/opencode/auth.json`.
Defina `HARNESS_RAG_PROVIDER=rag-harness` depois de criar o índice local do
curso para trocar a evidência de demonstração por fontes reais do repositório.
A [aula do Dev UI com Ollama](/pt-BR/lectures/lecture-18) roda o mesmo app
totalmente local e traz a sequência completa de prompts, screenshots e
checklist de evidências.

Execute a suíte offline completa com `python3 -m unittest discover -s tests -v`
a partir desse diretório. Ela inclui as evals de contrato dos prompts dourados e
não exige chave de API em nuvem.

Veja o [registro da feature](/pt-BR/tasks/adk-rag-jev-harness) para as decisões e guardrails adotados.

**Designs**: [ADK + RAG + Jev](/pt-BR/harness-designs/adk-rag-jev-harness) ·
[ADK RAG PostgreSQL](/pt-BR/harness-designs/adk-rag-postgres-harness) ·
[Projeto 06B](/pt-BR/projects/project-06-postgres)
