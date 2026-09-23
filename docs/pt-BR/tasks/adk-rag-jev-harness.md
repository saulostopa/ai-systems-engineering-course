---
title: Feature — harness ADK + RAG + Jev
---

# Feature — harness ADK + RAG + Jev

Statuso: **ativo** · Responsável: Harness Foundation Course · Alvo: Projeto 06

## Decisão

Criar um projeto de composição separado, `adk-rag-harness`. O RAG existente continua independente, o Google ADK será a camada de workflow e runtime, e o Jev será o provedor de decisões tipadas para roteamento e avaliação de evidências.

| Camada | Responsabilidade |
|---|---|
| ADK | Ciclo da sessão, grafo de workflow, agentes, ferramentas, retries e runtime |
| Jev | Decisões Noul, Choice e Score com confiança |
| Código de política | Limiares, fallbacks, escalação e regras para ações irreversíveis |
| RAG | Ingestão, chunking, embeddings, recuperação, reranking e citações |
| LLM | Reescrita da consulta, síntese e geração da resposta |

## Primeiro recorte

Avaliar três decisões:

1. A solicitação precisa de recuperação?
2. Qual coleção ou estratégia de recuperação deve ser usada?
3. As evidências retornadas são suficientes para responder?

O Jev não deve gerar prosa, substituir a busca semântica nem ser a única barreira de segurança. O código mantém um fallback determinístico para indisponibilidade, baixa confiança ou evidências contraditórias.

A implementação inicial está em `adk-rag-harness/`. Ela fornece os contratos independentes do provedor, a política determinística de recuperação, um adapter Jev sem dependências para o contrato `/v1/systemone` da TypeSafe, um adapter opcional para o pacote Python oficial `typesafe-sdk`, um adapter com coleções permitidas para o `rag-harness` existente, fallback para falha do provedor e doze testes offline. O adapter opcional do runtime Google ADK expõe o workflow limitado como uma tool estruturada de `LlmAgent` e um `App`; `adk-rag-harness/adk_app/agent.py` agora é um entrypoint executável do ADK com modo demo offline ativado por padrão. Instale `adk-rag-harness[adk,jev-sdk]` somente ao executar com o Google ADK e o SDK oficial.

## Guardrails e avaliação

- Limiares são configuração de política, não comportamento implícito do modelo.
- Baixa confiança segue para fallback determinístico ou pedido de esclarecimento.
- Texto do usuário e evidências são entradas não confiáveis.
- Nenhuma ação irreversível é autorizada somente por um score do Jev.
- Falhas, timeouts e erros de schema são observáveis e falham de forma segura.
- A versão inicial deve funcionar em testes sem chave de API.

A feature só passa de planejada para ativa depois de medir classificação de necessidade de RAG, roteamento de coleção, suficiência das evidências, falsos positivos e negativos, latência, custo, fallback, completude das citações e qualidade da resposta final.

Veja o [diagrama de arquitetura ADK + RAG + Jev](https://github.com/svslwm/harness-plannig/blob/develop/docs/architecture/adk-harness-architecture.html).

## Referências

- [Google ADK](https://adk.dev/)
- [Integrações do ADK](https://adk.dev/integrations/)
- [Visão geral do Jev](https://imasters.com.br/inteligencia-artificial/o-que-e-o-jev-e-por-que-eu-comecei-a-usar)
- [Notas sobre o modelo de decisões Jev](https://github.com/dannote/jev/blob/master/guides/introduction/why-jev.md)
