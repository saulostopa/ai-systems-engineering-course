---
title: Aula 12 — Sessões terminam com estado limpo
---

# Aula 12 — Sessões terminam com estado limpo

> O fim de uma sessão é o início da próxima. Terminar sujo é sabotar a continuidade.

## O que é "estado limpo"

Uma sessão termina limpa quando a próxima sessão (agente ou humano) consegue retomar sem precisar **desfazer** nada do que você fez. Estado sujo é o oposto: arquivos meio editados, features `in_progress` que ninguém avançou, handoff desatualizado, testes quebrados deixados para trás.

O sintoma clássico: o próximo agente abre o repo, roda os testes, e eles falham — e ele gasta a sessão inteira descobrindo que a falha não era dele, era da sessão anterior.

## O protocolo de encerramento do factory

O `webmotors-harness-factory` define o fim de sessão com precisão (`AGENTS.md` §8):

1. Atualizar `feature_list.json` — estados reais das features.
2. Atualizar `claude-progress.md` — o que foi feito, o que falhou, próxima ação.
3. Atualizar `session-handoff.md` — seções obrigatórias do cabeçalho.
4. Rodar `scripts/cleanup-scanner.sh` — detectar drift e artefatos esquecidos.
5. Rodar `scripts/validate-harness.sh` — **deve passar**.
6. Seguir `policies/git.md` — commits coerentes, sem lixo.

Repare na simetria com a Aula 06 (boot): **o boot começa lendo o handoff; o encerramento escreve o handoff**. Se todo mundo escreve, todo mundo lê algo confiável.

## O que fica limpo de verdade

| Artefato | Estado limpo | Estado sujo |
|---|---|---|
| Árvore git | Sem mudanças não commitadas sem propósito | Arquivos órfãos, merges pela metade |
| Testes | Suíte verde e estável | Falhas preexistentes "deixadas" |
| Features | Uma `in_progress` coerente, resto `not_started`/`passing` | Dez `in_progress`, nenhuma avançada |
| Handoff | Diz exatamente onde parou e o que vem | Diz o que aconteceu há 3 sessões |
| Artefatos | Reports/quizzes gerados e referenciados | HTMLs soltos sem dono |

## O encerramento como contrato

O AgEnFK trata o encerramento como parte do fluxo: o item só conclui depois do teste registrado e da evidência — e a transição entre fases preserva o estado. Quando uma sessão é pausada, o `agenfk-pause` salva o contexto completo; quando retoma, o `agenfk-resume` restaura — o "estado limpo" vira mecânico, não hábito.

E na prática deste projeto: a sessão que fez o scoping terminou com tudo commitado (working tree clean), pushed e com a story A2 em `IN_PROGRESS` coerente — a sessão seguinte (esta, escrevendo as aulas) começou lendo o estado e continuou sem retrabalho.

## "Clean state" para áreas de domínio

- **Finanças**: o harness de madrugada termina publicando o relatório e marcando as planilhas como processadas — se a manhã começa com o relatório pronto e o estado consistente, o harness dormiu "limpo".
- **Games**: a sessão de criação de narrativa termina com o doc de design commitado e o item avançado — nunca com ideias só na conversa.
- **Comercial**: a proposta fica salva e versionada, com o próximo passo registrado.

## Principais aprendizados

1. Estado limpo é o que permite retomada sem retrabalho — o contrário de "tarefa concluída".
2. O encerramento espelha o boot: quem escreve o handoff garante a leitura confiável da próxima sessão.
3. Suíte verde estável, árvore coerente e features consistentes são o mínimo.
4. Clean state mecânico (pause/resume, gates) > clean state como boa intenção.

## Verifique seu aprendizado

```
"quiz me on a Aula 12"
```

**Próxima aula**: [13 — De prompts manuais a loops autônomos](/pt-BR/lectures/lecture-13).