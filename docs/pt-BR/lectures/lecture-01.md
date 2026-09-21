---
title: Aula 01 — Por que agentes capazes ainda falham
---

# Aula 01 — Por que agentes capazes ainda falham

> A primeira pergunta que este curso responde: se os modelos são tão bons, por que os agentes ainda erram tanto?

## O modelo não é o produto

O modelo de linguagem resolve o problema *cognitivo*: ele raciocina, escreve, lê e decide. Mas um agente que trabalha de verdade precisa de muito mais do que cognição. Ele precisa:

- **Saber o que existe** — quais arquivos, quais serviços, qual a regra de negócio.
- **Saber o que fazer** — qual feature, em que ordem, com que critério de pronto.
- **Saber quando parar** — como verificar que terminou sem declarar vitória cedo demais.
- **Lembrar onde estava** — o que já foi feito quando a sessão termina e outra começa.

Quando um desses quatro está ausente, o agente falha — mesmo sendo "capaz". E aqui está a virada de chave deste curso:

> **A falha quase nunca está no modelo. Está no ambiente em volta dele.**

## O experimento mental

Pegue a mesma pessoa (ou o mesmo modelo) e coloque-a em dois ambientes:

1. **Ambiente A**: uma mesa com uma pilha de papéis sem ordem, instruções orais vagas, nenhuma definição de "pronto", nenhuma forma de verificar o próprio trabalho, e interrupções a cada 10 minutos.
2. **Ambiente B**: uma mesa com o objetivo escrito, o escopo delimitado, os materiais organizados, uma checklist de aceite e um espelho onde conferir o resultado.

A mesma pessoa produz resultados dramaticamente diferentes. O modelo é o mesmo; o **harness** é o que muda.

## Na Webmotors

Nosso próprio repositório de curso é um exemplo vivo. No `harness-plannig`, o `.claude/CLAUDE.md`, o `AGENTS.md` e o `feature_list.json` são o "Ambiente B" para o agente que constrói o curso com a gente. Quando o gatekeeper bloqueou a story A1 de ir para DONE sem build e evidência, ele estava corrigindo exatamente o sintoma desta aula: **o agente se sentia pronto; o ambiente exigia prova**.

E no `webmotors-harness-factory`, o mesmo princípio aparece mecanizado: pre-commit hooks que bloqueiam, `scripts/validate-harness.sh` que verifica, `policies/definition-of-done.md` que define o aceite. Nenhum desses arquivos faz o modelo mais inteligente — eles fazem o trabalho mais confiável.

## O que um harness faz (resumo)

| Necessidade do agente | O que o harness oferece |
|---|---|
| Saber o que existe | AGENTS.md, docs, feature_list, skills |
| Saber o que fazer | Items/flows, escopo declarado, prioridade |
| Saber quando parar | Definition of Done, testes, gatekeeper |
| Lembrar onde estava | progress.md, session-handoff.md, estado no repo |

## Principais aprendizados

1. Agente = modelo + harness. Modelo raciocina; harness faz o trabalho acontecer.
2. Erros de agente são sintomas de ambiente, não de inteligência.
3. O harness não "melhora" o modelo — ele **constitui o sistema de trabalho** em que o modelo opera.
4. Tudo que você vai construir neste curso existe para responder: "como o agente sabe, age, verifica e lembra?"

## Verifique seu aprendizado

Peca a um agente para gerar o quiz desta aula com a skill `feature-quiz`:

```
"me testa com um quiz dos 4 níveis sobre a Aula 01"
```

Se ainda não tem a skill instalada, volte para a [Biblioteca](/pt-BR/resources/) e instale o pacote `harness-agent-skills`.

**Próxima aula**: [02 — O que é um harness, de fato](/pt-BR/lectures/lecture-02).