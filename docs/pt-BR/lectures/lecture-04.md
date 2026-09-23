---
title: Aula 04 — Por que um único arquivo de instruções falha
---

# Aula 04 — Por que um único arquivo de instruções falha

> O instinto natural é empilhar tudo num AGENTS.md gigante. É o pior instinto que existe.

## A tentação do arquivo único

É sedutor: um único arquivo que diz **tudo** — contexto, regras, comandos, políticas, exemplos, lembretes. Um "manual completo". O problema é que esse arquivo falha em cinco frentes ao mesmo tempo:

1. **Custo de contexto**: cada token do arquivo é pago em todo carregamento. Um arquivo de 5 mil linhas rouba contexto do trabalho real.
2. **Contradição**: instruções longas se contradizem, e o agente segue a última ou a mais específica — imprevisível.
3. **Obsolescência**: ninguém revisa um arquivo gigante; ele apodrece em silêncio.
4. **Irrelevância**: 90% das instruções não se aplicam à tarefa atual, mas o agente não sabe filtrar.
5. **Diluição**: o que é crítico (gate, verificação) se perde entre o que é decorativo.

## O padrão que funciona: roteamento

Em vez de um manual único, um **roteador** curto aponta para documentos específicos, carregados sob demanda:

```
AGENTS.md (roteador — curto, estável)
├── O que este repo é
├── O que ler primeiro (links)
├── Como escolher uma tarefa (feature_list.json)
├── Como verificar (policies/definition-of-done.md)
└── Onde a documentação vive (tabela de rotas)
```

O agente carrega o roteador, e então **busca** a página certa quando precisa — exatamente como uma pessoa usa um README, não como quem decora uma bíblia.

## Evidência do nosso ecossistema

O `webmotors-harness-factory/AGENTS.md` é um roteador exemplar: 9 seções curtas, com uma tabela "Where deeper documentation lives" apontando para `docs/architecture/`, `docs/operations/`, `skills/<nome>/SKILL.md`, `policies/*.md`. Nada de conteúdo copiado — só rotas.

O `harness-agent-skills` segue o mesmo padrão no nível de skills: cada skill é um `SKILL.md` curto com frontmatter (`name` + `description`), e o corpo em `Gather → Write → Output`. A descrição é o gatilho de carregamento: a skill só é lida **quando a tarefa combina** — sob demanda, não no boot.

Harnesses maduros distribuem regras por plataforma — um diretório por formato de agente (Claude, Codex, Cursor, Gemini, OpenCode) em vez de um único arquivo universal — para que cada ferramenta receba o formato que de fato lê.

## Regra prática: o arquivo de 10%

Um arquivo de instruções bem formado deveria ser cortável em ~10% sem perder nenhuma regra crítica. Se você precisa ler 300 linhas para saber como verificar o trabalho, o roteiro está errado.

| Sintoma | Diagnóstico |
|---|---|
| AGENTS.md com mais de ~150 linhas | Provável roteador inchado; extrair para docs/ |
| Instruções duplicadas em 2+ lugares | Contração e divergência chegando |
| "Lembrar de..." no final do arquivo | Instrução que será esquecida; virar policy ou skill |
| Tabela de conteúdo manual | Sina de que o arquivo já é um livro; quebrar |

## Na Webmotors — o curso como exemplo

Este curso é um harness de conhecimento, e segue o mesmo princípio: a home e as páginas de seção são **roteadores** (links para aulas, projetos, biblioteca); cada aula é um documento pequeno com escopo único; cada skill é um pacote carregado sob demanda. Quando a biblioteca de templates (A4) for entregue, os templates prontos seguirão o mesmo formato — roteador curto + docs rotadas.

## Principais aprendizados

1. Arquivo único gigante = custo, contradição, obsolescência, irrelevância, diluição.
2. Roteador curto + documentos sob demanda é o padrão que escala.
3. Skills com `description` de gatilho são o mecanismo de carregamento sob demanda.
4. Se você não consegue cortar 90% do arquivo sem perder regra crítica, o roteamento está errado.

## Verifique seu aprendizado

```
"quiz me on a Aula 04"
```

**Próxima aula**: [05 — Continuidade em tarefas longas](/pt-BR/lectures/lecture-05).