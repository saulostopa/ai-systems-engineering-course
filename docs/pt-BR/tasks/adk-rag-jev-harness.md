---
title: Feature — Harness ADK + RAG + Jev
---

# Feature — Harness ADK + RAG + Jev

Status: **ativo** · Responsável: Harness Foundation Course · Alvo: Projeto 06

## Decisão

Criar um projeto separado de composição `adk-rag-harness`. Manter o harness RAG existente independente e tornar o Google ADK a camada de workflow e runtime. Adicionar o Jev como provedor de decisões tipadas para roteamento delimitado, guardrails e decisões de evidências estruturadas nos 4 pilares: **Rotear, Filtrar, Pontuar e Liberar**.

| Camada | Responsabilidade |
|---|---|
| ADK | Ciclo de vida da sessão, grafo de workflow, agentes, ferramentas, retries e integração com runtime |
| Jev | Decisões tipadas delimitadas (`Noul`, `Choice`, `Score`) cobrindo roteamento de modelos, guardrails, autorização de tool calls, reranking e avaliação de resposta |
| Código de política | Limiares tripartites (`executa`, `confirma`, `humano`), fallbacks, escalonamento e regras para ações irreversíveis |
| RAG | Ingestão, chunking, embeddings, recuperação, adaptador de reranking e citações |
| LLM | Modelos estratificados: pequenos para respostas diretas, grandes para raciocínio e síntese final |

## Pilares de Arquitetura (Os 4 Quadrantes do Jev)

A arquitetura do harness implementa os princípios de decisão operacional detalhados na [referência do Jev](/pt-BR/reference/jev):

1. **Rotear (Roteamento de Modelos)**:
   - O Jev avalia a complexidade do prompt: direciona tarefas simples para modelos econômicos ($) e sínteses/raciocínio complexos para modelos maiores ($$$).
2. **Filtrar (Guardrails e Tool Calls)**:
   - *Guardrail pré-LLM*: bloqueia injeções de prompt e abusos antes de acionar modelos generativos.
   - *Autorização de Tool Calls*: intercepta pedidos de ferramentas do agente e avalia deterministicamente entre `permite`, `pergunta` (confirmação HITL) ou `nega`.
3. **Pontuar (Reranking e Evals)**:
   - *Reranking de Evidências*: pontua trechos recuperados para que a LLM de síntese receba apenas o contexto de maior relevância.
   - *Eval Inline de LLM*: pontua a resposta gerada quanto à fundamentação factual e aderência às fontes antes da exibição.
4. **Liberar (Limiares de Certeza Tripartites)**:
   - Alta confiança ($\ge 0.85$): execução automatizada.
   - Média confiança ($0.50$ a $0.84$): requer confirmação interativa do usuário.
   - Baixa confiança ($< 0.50$): escalona para revisão humana (HITL).

## Fatias de Implementação

### Fatia 1 — Política de Recuperação e Evidências (Entregue)
Avalia três decisões delimitadas:
1. Esta requisição precisa de busca externa? (`direct` vs `retrieve` vs `clarify`)
2. Qual coleção de conhecimento ou estratégia de busca deve ser usada?
3. A evidência retornada é suficiente para responder? (`sufficient` vs `insufficient/blocked`)

### Fatia 2 — Guardrail, Roteamento e Gating de Ações (Evolução)
1. Adicionar guardrail de sanitização de entrada antes do despacho para ferramentas.
2. Rotear requisições diretas para modelos locais menores (`llama3.2:3b`) e sínteses RAG complexas para modelos maiores (`qwen2.5:14b` / hospedado).
3. Interceptar execuções de ferramentas com o portão de política `permite` / `pergunta` / `nega`.
4. Aplicar avaliação inline de resposta para detectar alucinações antes de responder na UI.

A implementação inicial está disponível no [projeto independente `adk-rag-harness`](https://github.com/saulostopa/ai-systems-engineering-harnesses/tree/main/adk-rag-harness). Ela fornece os contratos neutros em relação a provedor, política determinística de recuperação, um adaptador Jev sem dependências para o contrato `/v1/systemone` da TypeSafe, um adaptador opcional para o pacote Python oficial `typesafe-sdk`, um adaptador com lista de permissões para o `rag-harness` existente, fallback para falha do provedor e trinta e três testes offline. O adaptador opcional de runtime do Google ADK expõe o workflow delimitado como uma ferramenta estruturada de `LlmAgent` e uma `App`; seu `adk_app/agent.py` é um ponto de entrada ADK executável com o Jev pelo OpenRouter (`typesafe/jev-router`) como modelo padrão de conversa e de decisões tipadas, o Ollama (`llama3.1:8b` e `qwen2.5:14b`) como alternativa local opcional e um provedor opcional com o `rag-harness` real. Instale os extras `adk` e `openrouter` para a aplicação padrão, e acrescente `ollama` e `jev-sdk` para os modos local e TypeSafe oficial.

## Contratos

Introduzir uma interface neutra de decisão para que testes usem um provedor fake e o harness possa comparar o Jev com regras ou outro classificador.

```python
class DecisionProvider(Protocol):
    async def decide(
        self,
        state: DecisionState,
        questions: list[Question],
    ) -> DecisionResult:
        ...
```

O adaptador de RAG expõe um contrato tipado de recuperação contendo query, coleção, filtros, quantidade solicitada de resultados, chunks de evidência, respondibilidade e motivo. Toda resposta preserva referências de origem.

## Guardrails e portão de avaliação

- Limiares de confiança são configuração de política no código, não comportamento do modelo.
- Baixa confiança direciona para fallback determinístico ou escalonamento humano (HITL).
- Evidências e texto fornecido pelo usuário são tratados como entrada não confiável.
- Nenhuma ação irreversível é autorizada somente por um score do Jev.
- Falhas do provedor, timeouts e erros de schema são observáveis e falham em modo fechado (*fail closed*).
- A versão inicial oferece suporte a testes offline sem chave de API.

Mover de planejado para ativo somente após medir classificação de necessidade de busca, roteamento de coleção e estratégia, suficiência de evidências, falsos negativos e positivos, latência, custo, taxa de fallback, completude de citações e qualidade da resposta final.

A decisão é visualizada na [arquitetura ADK + RAG + Jev](https://github.com/saulostopa/ai-systems-engineering-course/blob/main/docs/architecture/adk-harness-architecture.html).

## Referências

- [Google ADK](https://adk.dev/)
- [Integrações do ADK](https://adk.dev/integrations/)
- [Arquitetura de Decisão Jev](/pt-BR/reference/jev)
- [Visão geral do Jev](https://imasters.com.br/inteligencia-artificial/o-que-e-o-jev-e-por-que-eu-comecei-a-usar)
- [Notas sobre o modelo de decisões Jev](https://github.com/dannote/jev/blob/master/guides/introduction/why-jev.md)
