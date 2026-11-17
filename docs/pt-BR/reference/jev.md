---
title: Jev — Camada de Decisão Operacional
---

# Jev — Camada de Decisão Operacional

> "O LLM escreve, o Jev decide": arquitetura de decisão rápida para custo, latência e escala.

Estamos vivendo uma explosão de modelos de IA, e o desafio central na engenharia de harnesses não é apenas escolher a inteligência: é avaliar **custo, latência e autonomia de decisão**.

Em operações de grande escala (como observabilidade, telecomunicações e eventos contínuos de sistemas), o volume de dados, logs, alarmes e sinais é gigantesco. A pergunta arquitetural correta não é *"como colocar uma LLM em tudo?"*, mas sim:

> **"Quando realmente precisamos de uma LLM, e qual modelo devemos utilizar?"**

É nesse ponto que a arquitetura do **Jev** ganha relevância. A proposta é colocar uma camada de decisão antes e ao redor da execução da LLM:

$$\text{Evento} \longrightarrow \text{Jev} \longrightarrow \text{Decisão} \longrightarrow \text{LLM adequada} \longrightarrow \text{Ação}$$

![Onde o Jev substitui um LLM](/images/jev.png)

## Os 4 Pilares do Jev

Conforme ilustrado no diagrama acima, o Jev atua em quatro quadrantes fundamentais substituindo ou delimitando o uso de LLMs:

### 1. Rotear (Roteamento de Modelos)
Em vez de enviar todos os prompts para o mesmo modelo de ponta, o Jev analisa a complexidade da intenção e direciona:
- Prompts simples (ex.: traduções rotineiras, saudações, extração direta) $\rightarrow$ **LLM pequeno** (\$).
- Prompts intermediários $\rightarrow$ **LLM médio** (\$\$).
- Raciocínio denso, arquitetura e revisão contratual complexa $\rightarrow$ **LLM grande** (\$\$\$).

### 2. Filtrar (Guardrail & Tool Calls)
- **Guardrail de entrada**: Intercepta injeções de prompt e abusos antes de acionar a LLM, bloqueando requisições perigosas sem gastar tokens.
- **Filtro de Tool Calls**: Quando o agente propõe uma ação (`tool call`), o Jev atua como barreira determinística decidindo entre:
  - `permite`: execução direta autorizada;
  - `pergunta`: exige confirmação do usuário (Human-in-the-Loop);
  - `nega`: bloqueia ações não autorizadas ou destrutivas.

### 3. Pontuar (Reranking, Labeling & Evals)
- **Reranking**: Ranqueia trechos recuperados pelo RAG para que a LLM leia apenas os trechos mais relevantes, economizando janela de contexto e evitando dispersão.
- **Labeling em massa**: Classifica e pontua grandes bases de dados ou eventos linha a linha com altíssima velocidade e baixo custo.
- **Eval de LLM**: Atua como triagem rápida pós-geração, avaliando aderência e consistência da resposta gerada pela LLM antes de exibi-la.

### 4. Liberar (Limiares de Certeza & Tempo Real)
- **Limiar de certeza tripartite**: O código do harness define o limiar de liberação, e não a LLM:
  - *Alta confiança* $\rightarrow$ executa automaticamente.
  - *Média confiança* $\rightarrow$ solicita confirmação.
  - *Baixa confiança* $\rightarrow$ escala para decisão humana (HITL).
- **Tempo real (~300ms)**: Ciclo ágil de estado $\rightarrow$ Jev $\rightarrow$ ação para interfaces reativas, voz, bots e navegação contínua, onde o tempo de resposta de uma LLM generativa inviabilizaria a experiência.

## Os Três Ganhos da Equação

1. **Custo**: Reservar modelos caros exclusivamente para situações cognitivamente exigentes reduz dramaticamente o consumo de tokens e a infraestrutura.
2. **Velocidade**: Tarefas rotineiras são resolvidas por decisões tipadas ou modelos ultra-rápidos, reduzindo latência operacional para a casa dos milissegundos.
3. **Escala**: Viabiliza projetos corporativos com milhões de eventos, mantendo a operação previsível e auditável.

## Diretriz de Adoção nos Harnesses

Comece simples (harness básico puramente LLM). Conforme a complexidade do sistema cresce, adicione RAG para evidências e introduza o **Jev** para decisões tipadas, roteamento e guardrails nos harnesses avançados. A autonomia agêntica total só deve ser concedida onde houver valor e ganho comprovado de pelo menos 10x em relação ao processo determinístico.
