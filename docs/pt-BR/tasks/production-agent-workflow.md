---
title: Backlog — fluxo de produção para agentes de programação
---

# Backlog — fluxo de produção para agentes de programação

Status: **backlog** · Priority: **P1** · Escopo: capacidade transversal do curso e dos harnesses

## Fonte e decisão

O post compara quatro formas de usar agentes de programação em produção e
conclui que o fluxo mais confiável é alinhar o design primeiro, dividir o
trabalho em fatias verticais e só então permitir a implementação e a
verificação pelo agente. O vídeo do LinkedIn não pôde ser acessado diretamente;
este registro usa o roteiro e o resumo fornecidos na solicitação.

Isso deve entrar como um **fluxo de produção para agentes** compartilhado, e
não como um novo harness. Implementação de uma tacada continua adequada para
mudanças pequenas e reversíveis, mas não deve ser o padrão para features de
produto.

## Contrato do fluxo

Features maiores que uma mudança local devem passar por estados explícitos:

1. **Pesquisa** — inspecionar repositório, restrições, dependências,
   comportamento atual e evidências.
2. **Design** — alinhar comportamento, limites, fluxo de dados, riscos e
   verificação antes de implementar.
3. **Fatias verticais** — dividir o trabalho em incrementos pequenos, cada um
   com resultado observável e critérios de aceite.
4. **Implementação** — executar uma fatia autorizada por vez, mantendo o
   escopo declarado.
5. **Verificação** — executar testes proporcionais, inspecionar o resultado,
   registrar evidências e fazer a revisão independente quando exigida.

O plano deve manter separadas implementação, modo de execução e revisão
independente. A aprovação do design não autoriza trabalho não relacionado, e um
teste passando não substitui evidência ou revisão.

## Contrato proposto

```yaml
workflow:
  mode: design_first
  phases: [research, design, vertical_slices, implement, verify]
  design:
    required: true
    path: docs/exec-plans/<feature-id>/design.md
  slices:
    required: true
    path: docs/exec-plans/<feature-id>/slices.md
  review:
    independent: true
    brief_path: docs/reviews/<feature-id>/brief.md
    report_path: docs/reviews/<feature-id>/report.json
```

O schema final deve ser independente de fornecedor e opcional para planos
existentes. Planos atuais continuam válidos até serem migrados. O fluxo só deve
recusar um plano incompleto quando ele declarar explicitamente `design_first`.

## Adoção por harness

| Harness | Adoção |
|---|---|
| Basic | Ensinar pesquisa, design e fatias; manter a aprovação leve. |
| App | Exigir design e fatias para mudanças de UI, API, autenticação e E2E. |
| RAG / Area Copilot | Exigir design de limites de dados, recuperação e citações. |
| Domain | Exigir regras de negócio, invariantes e exemplos de aceite. |
| Hard | Usar design-first como padrão e bloquear conclusão sem evidência das fatias. |
| Enterprise | Adicionar mapa de dependências entre repositórios e rollout gradual. |
| ADK + RAG + Jev | Exigir design de roteamento, evidências, fallback e autorização de ferramentas. |

## Escopo multiagente

A ideia de um “herder” deve ser uma capacidade posterior, não um requisito da
primeira versão. Um coordenador só deve distribuir tarefas quando o plano
declarar limites, entradas, saídas e ordem de integração. Ele não deve
multiplicar agentes para uma fatia fortemente acoplada nem permitir edições
paralelas sem regras de ownership.

A primeira implementação deve funcionar com um único agente, transições de fase
explícitas e um revisor opcional em contexto novo. Isso captura a parte mais
confiável do fluxo sem adicionar complexidade de orquestração cedo demais.

## Skills para avaliar

As referências abaixo devem ser avaliadas como material de implementação deste
fluxo:

- [AI Hero Skills](https://www.aihero.dev/skills) apresenta um conjunto
  composável de 27 skills licenciadas em MIT, compatíveis com vários agentes.
  A cadeia principal é `grill-with-docs → to-spec → to-tickets → implement →
  code-review → retro`.
- [Repositório de skills do Matt Pocock](https://github.com/mattpocock/skills)
  é o repositório fonte e documenta instalação para Codex, Claude, Gemini CLI,
  Copilot e outros agentes.

As candidatas mais relevantes para o curso são:

| Skill | Uso possível nos harnesses | Decisão inicial |
|---|---|---|
| `setup-matt-pocock-skills` | Configurar vocabulário, tracker e caminhos de documentos | Avaliar no Basic e nos harnesses de projeto |
| `grill-with-docs` | Entrevista de pesquisa, decisões e ADR antes da implementação | Avaliar em todos os fluxos design-first |
| `to-spec` | Transformar conversa alinhada em especificação revisável | Avaliar no App, Domain e Enterprise |
| `to-tickets` | Dividir a especificação em fatias verticais | Avaliar no Hard e Enterprise |
| `implement` + `tdd` | Implementação test-first e ciclos de feedback | Comparar com os gates atuais |
| `code-review` + `pr` | Revisar diff contra o plano e preparar PR | Integrar apenas se continuar independente de fornecedor |
| `research` + `wayfinder` | Pesquisa com citações e mapa de decisões | Avaliar no ADK + RAG + Jev e Enterprise |
| `handoff` + `retro` | Preservar continuidade e melhorar o harness após a entrega | Avaliar como extensões de produtividade |
| `implement-spec` | Implementar uma especificação completa com subagentes paralelos | Manter experimental até existirem gates de ownership e merge |

Não instalar o conjunto completo por padrão. Primeiro comparar as instruções de
cada skill com os contratos do curso, remover gates duplicados e manter o
harness como autoridade para escopo, permissões, evidências, testes e estado de
conclusão.

## Gate de avaliação e segurança

Antes de adotar uma skill, inspecionar sua fonte em uma revisão fixada e
registrar:

- entradas lidas e arquivos escritos;
- comandos, rede, credenciais e serviços externos solicitados;
- se altera o estado da feature ou declara conclusão sem evidência do harness;
- conflitos com `AGENTS.md`, políticas do curso, Archify e revisão independente;
- custo de tokens, compatibilidade de provider e comportamento com Codex,
  Claude e agentes locais.

Skills são instruções não confiáveis até serem revisadas. Elas não devem receber
segredos, sobrescrever políticas do repositório, executar saída arbitrária do
modelo como shell ou código, nem autorizar ações destrutivas ou externas. A
preferência é copiar somente skills selecionadas, fixar a revisão e validar os
arquivos em um worktree limpo. A avaliação deve incluir casos de prompt
injection no conteúdo das skills, nos documentos recuperados e nas saídas de
ferramentas.

O resultado desta tarefa é uma matriz de compatibilidade e uma decisão de
adoção, não uma instalação em massa.

## Relação com features existentes

- Estende [execução e revisão independente](/tasks/independent-review-execution)
  com gate de design e contrato de fatias verticais.
- Complementa [feature-archify](/pt-BR/skills/feature-archify), que valida o fluxo
  depois do design e da implementação.
- Aplica-se ao [ADK + RAG + Jev](/tasks/adk-rag-jev-harness) antes de alterar
  roteamento, thresholds, evidências, ferramentas ou fallbacks.
- Não substitui a decisão entre RAG, CAG e KAG.

## Sequência de implementação

1. Definir o schema de plano para pesquisa, design e fatias.
2. Adicionar o fluxo `design_first` ao Basic com defaults compatíveis.
3. Adicionar gates ao Hard, Enterprise e ADK + RAG + Jev.
4. Criar templates e aulas mostrando uma feature da pesquisa à revisão.
5. Avaliar as skills referenciadas contra a matriz e os gates atuais do curso.
6. Adicionar contrato opcional para trabalho multiagente delimitado.
7. Avaliar o fluxo em uma feature de UI, uma de backend e uma de RAG ou ADK.

## Critérios de aceite

- Uma feature pode declarar `design_first` sem depender de modelo, CLI ou
  fornecedor específico.
- O plano registra pesquisa, decisões de design, fatias, critérios de aceite e
  comandos de verificação.
- Cada fatia possui escopo limitado e resultado observável.
- Hard, Enterprise e ADK + RAG + Jev não podem marcar como passing uma feature
  opt-in sem as evidências de design, fatias e revisão.
- Planos existentes continuam compatíveis até migração explícita.
- Execução multiagente registra ownership, dependências, saídas e ordem de
  integração, sem expandir o escopo silenciosamente.
- O curso contém um exemplo completo e explica quando uma implementação de uma
  tacada ainda é apropriada.
- As skills selecionadas possuem revisão fixada, resultado de compatibilidade e
  registro explícito de riscos residuais antes da adoção.
- Nenhuma skill de terceiros pode ignorar gates de escopo, autorização,
  evidência ou revisão.

## Referência

- [Post original no LinkedIn](https://www.linkedin.com/posts/pau-labarta-bajo_how-to-do-you-use-ai-coding-agents-for-production-ugcPost-7516471983887425536-cjpA/)
- [AI Hero Skills](https://www.aihero.dev/skills)
- [Repositório de skills do Matt Pocock](https://github.com/mattpocock/skills)
