---
title: Aula 02 — O que é um harness, de fato
---

# Aula 02 — O que é um harness, de fato

> Definição precisa, componentes e a diferença entre harness, prompt e skill.

## Definição

Um **harness** é tudo o que envolve o modelo e o transforma em um agente que trabalha. Formalmente:

> **Harness** = o ambiente de trabalho do agente: as ferramentas que ele pode chamar, o conhecimento que ele carrega, as regras que ele obedece, os mecanismos que verificam o que ele faz e o estado que persiste entre as execuções.

A fórmula deste curso:

```
agente = modelo + harness
```

O modelo é substituível (Claude, GPT, Gemini, DeepSeek, Llama...). O harness é o que dá identidade, previsibilidade e confiabilidade ao trabalho.

## Os componentes de um harness

| Componente | O que é | Exemplo no nosso ecossistema |
|---|---|---|
| **Ferramentas** | Comandos, APIs e ações que o agente pode executar | Bash, gh, git, Playwright, npx |
| **Conhecimento** | Instruções e contexto carregados antes do trabalho | AGENTS.md, CLAUDE.md, docs/ |
| **Skills** | Pacotes de instrução ativados por demanda (`SKILL.md`) | `feature-report`, `feature-quiz`, `qa-playwright-e2e` |
| **Regras/Gates** | Mecanismos que restringem o comportamento | Gatekeeper, pre-commit hooks, policies |
| **Verificação** | Como o agente prova que terminou | Testes, `validate-harness.sh`, evidence |
| **Estado** | O que persiste entre sessões | `feature_list.json`, `progress.md`, `session-handoff.md` |

## Harness ≠ prompt

Um prompt é uma instrução que existe no momento da conversa. Um harness é um **sistema persistente**: ele existe no repositório, é versionado, passa por code review e continua funcionando mesmo quando o modelo muda.

Exemplo concreto: a skill `feature-quiz` é um harness-component. Ela não é "o prompt do quiz" — é um `SKILL.md` versionado em [harness-agent-skills](https://github.com/svslwm/harness-agent-skills) que qualquer agente pode carregar quando a tarefa combina com a descrição. Troque o modelo e a skill continua lá, idêntica.

## Harness não é um produto; é uma camada

O `webmotors-harness-factory` é explícito sobre isso no `AGENTS.md`:

> "Uma **Harness Factory** reutilizável: o sistema operacional que define *como* o trabalho de engenharia agêntica é executado. **NÃO é um repositório de produto.**"

A verdade do produto mora no repositório de produto; o harness mora numa camada separada que **governa o processo**. Essa separação (harness/product isolation) é o que permite o mesmo harness servir a vários projetos — e é a base do modelo multi-team que veremos nas aulas de domínio.

## O harness como sistema de controle

Um harness funciona como um circuito de controle:

```
AGENTE ──age──▶ MUNDO (arquivos, testes, git)
  ▲                  │
  └────◀─verifica────┘
         (gates, testes, evidência)
```

Sem o laço de verificação, o agente é uma caixa que só emite texto. Com o laço, ele é um trabalhador que age, observa o resultado e corrige — o que a Aula 13 formaliza como *loop engineering*.

## Na Webmotors

- **`webmotors-harness-factory`** — o esqueleto de processo: hooks, policies, scripts.
- **`harness-agent-skills`** — o catálogo de skills: artefatos + QA + perf.
- **um workflow engine** — a camada de gestão: itens, flows, gatekeeper, telemetria e Kanban. Opcional, e intercambiável: veja [harness grande](/pt-BR/harness-designs/enterprise-harness).
- **`harness-plannig`** — **este curso**, que é um harness rodando sobre os outros três (dogfooding).

## Principais aprendizados

1. Agente = modelo + harness; o modelo é trocável, o harness é o ativo.
2. Prompt é volátil; harness é persistente, versionado e revisável.
3. Componentes: ferramentas, conhecimento, skills, gates, verificação, estado.
4. Harness governa processo; produto mora no repo de produto.
5. O laço agir→verificar é o coração do sistema.

## Verifique seu aprendizado

```
"quiz me on a Aula 02"
```

**Próxima aula**: [03 — O repositório como sistema de registro](/pt-BR/lectures/lecture-03).