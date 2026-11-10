---
title: Aula 06 — Inicialização como fase própria
---

# Aula 06 — Inicialização como fase própria

> Antes de trabalhar, o agente precisa entender onde está. Isso é uma fase — e merece um protocolo.

## O erro clássico

O agente abre o repo e começa a editar. A impressão de produtividade é enganosa: sem entender o terreno, ele:

- edita o arquivo errado (há 3 repos parecidos?);
- segue padrões que não existem no projeto;
- quebra contratos (hooks, lint, format);
- repete trabalho que outra sessão já fez.

**Boot não é tempo perdido — é a fase que evita o retrabalho.**

## A inicialização como protocolo

O `harness-factory` define o boot com `./init.sh`:

> "`init.sh` verifica o diretório de trabalho, valida as ferramentas, roda a validação de baseline e imprime os próximos comandos recomendados. **Nunca inicia processos longos por padrão.**"

A sequência de inicialização saudável:

1. **Onde estou?** — confirmar o repo correto (o factory checa o working directory).
2. **O que existe?** — ler AGENTS.md/roteador, feature_list, docs de arquitetura.
3. **O ambiente funciona?** — tooling presente (node, python, gh), hooks instalados (`git config core.hooksPath`), baseline validado.
4. **Onde paramos?** — session-handoff, progress, status do git.
5. **O que fazer agora?** — escolher UMA feature em `in_progress` (nunca duas).

## Por que "uma de cada vez" faz parte do boot

O factory é explícito:

> "Apenas uma feature pode estar `in_progress` por vez, a menos que uma exceção seja documentada. Escolha a feature `not_started` de maior prioridade."

Isso não é burocracia: é a proteção contra o agente que espalha trabalho por dez frentes e não termina nenhuma (o sintoma da Aula 07).

## A inicialização como fase do workflow

Quando um projeto roda sobre um [workflow engine](/pt-BR/harness-designs/enterprise-harness), o boot deixa de ser checklist e vira fase do fluxo: o engine lê o item, confirma o projeto, lê escopo e arquitetura, **decompõe tudo antes de qualquer trabalho** e só então libera a execução. Resolver o projeto é ler o `.harness/config.yaml` do diretório — o equivalente mecânico do "onde estou?".

E o gatekeeper estende o boot para o meio da sessão: a cada edição, ele verifica se o arquivo está dentro de um projeto gerenciado e se há item ativo. **O agente não consegue trabalhar "sem saber onde está"** — o harness lembra por ele.

## Na prática — o caso do nosso scoping

Quando escopamos o workflow engine para este curso, o "boot" foi literalmente refeito: removemos regras globais, instalamos as regras **no projeto** e verificamos que, dentro do `harness-plannig`, o projeto resolve e o workflow ativa — e fora dele, nada. A inicialização correta é o que garante que cada agente, em cada repo, comece com o harness certo.

## Checklist de boot (copie para seu projeto)

```sh
./init.sh            # ou o equivalente do seu harness
rtk git status       # árvore limpa? handoff pendente?
rtk git log --oneline -5  # o que foi feito recentemente?
# leia: AGENTS.md, session-handoff.md, feature_list.json
# escolha UMA feature in_progress (ou promova a de maior prioridade)
# declare o escopo ANTES de editar (policies/scope-control.md)
```

## Principais aprendizados

1. Boot é fase própria, não perda de tempo: evita retrabalho e quebra de contrato.
2. Onde estou → o que existe → ambiente OK → onde paramos → o que fazer.
3. Uma feature in_progress por vez é proteção contra dispersão.
4. O harness deve tornar o "não saber onde está" impossível (gatekeeper, project.json).

## Verifique seu aprendizado

```
"quiz me on a Aula 06"
```

**Próxima aula**: [07 — Excesso de autonomia e entrega incompleta](/pt-BR/lectures/lecture-07).