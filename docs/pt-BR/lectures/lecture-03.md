---
title: Aula 03 — O repositório como sistema de registro
---

# Aula 03 — O repositório como sistema de registro

> A verdade do trabalho agêntico mora no repositório, não na conversa.

## O problema: conversas são voláteis

Quando um agente trabalha com você, a conversa contém decisões, planos e "combinados". Mas a conversa:

- **some** quando a sessão termina;
- **não é auditável** — ninguém revisa o que foi dito;
- **não é compartilhável** — outro agente ou outra pessoa não vê o contexto;
- **não tem autoridade** — nada impede o agente de divergir do combinado.

Se o estado do trabalho vive só na conversa, o trabalho não tem estado.

## O princípio

> Todo conhecimento, decisão e estado de trabalho que importa deve viver no repositório, como arquivos versionados.

Isso vale para:

- **O que fazer** → `feature_list.json`, itens do framework de gestão
- **Como fazer** → AGENTS.md, policies, skills
- **O que já foi feito** → commits, relatórios, `progress.md`
- **Onde parou** → `session-handoff.md`
- **O que foi decidido** → comentários, ADRs, docs

Quando a verdade mora no repo, o agente (e qualquer agente futuro, de qualquer ferramenta) pode reconstruir o contexto completo com uma simples leitura — e o trabalho fica **revisável em PR**, como qualquer código.

## O sistema de registro no nosso ecossistema

O `webmotors-harness-factory` define a hierarquia de arquivos de estado:

| Arquivo | Papel | Quem lê |
|---|---|---|
| `feature_list.json` | Estado de cada feature (not_started, in_progress, blocked, passing) | O agente decide o que fazer |
| `progress.md` | Trabalho recente, atual, falhas, próxima ação | O agente retoma a sessão |
| `session-handoff.md` | O que está verificado, o que está quebrado, próximo passo | O próximo agente/pessoa |
| `AGENTS.md` | O roteiro permanente: o que ler, como verificar, como terminar | Todo agente que entra no repo |

Repare no requisito do factory:

> "Git é a verdade: verifique hand-offs com `git status`/`git diff` e re-executando testes você mesmo; nunca confie em narração."

Isso é o sistema de registro funcionando: **narração não é evidência**; o repo é.

## Na Webmotors — o caso A1

Na primeira story deste projeto (A1 — setup do curso), o agente scaffoldou o VitePress e tentou marcar a story como DONE. O gatekeeper **recusou**: não existe transição direta para DONE — só via `validate_progress` com evidência. O que desbloqueou não foi a palavra "pronto" na conversa, foi:

1. o build do site rodando e passando;
2. o test result registrado (`log-test PASSED`);
3. a evidência documentada no comentário da story.

Tudo isso virou **registro permanente** no histórico do repo e na trilha do workflow. A conversa teria sido esquecida; o registro não.

## Por que o repo e não o banco?

Um workflow engine pode guardar itens num banco, e isso serve para agregação — mas não muda onde mora a verdade: os arquivos de estado do harness continuam **no repo de cada projeto**, e o engine gerencia o fluxo em cima deles. Se apagar o engine fizer o projeto perder informação sobre si mesmo, o estado está no lugar errado. A regra prática:

- **Processo e fluxo** → framework de gestão (itens, gates, telemetria)
- **Contexto e conhecimento** → arquivos no repo (docs, skills, policies)
- **Evidência** → output de comandos, builds, testes, relatórios gerados

## Principais aprendizados

1. Conversa é volátil; repo é permanente, auditável e compartilhável.
2. Estado do trabalho (o quê, como, quanto, onde parou) mora em arquivos versionados.
3. Narração não é evidência: verifique no repo, não na conversa.
4. Um harness multi-ferramenta só funciona se a verdade estiver fora de cada ferramenta.

## Verifique seu aprendizado

```
"quiz me on a Aula 03"
```

**Próxima aula**: [04 — Por que um único arquivo de instruções falha](/pt-BR/lectures/lecture-04).