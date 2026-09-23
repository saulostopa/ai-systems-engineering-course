---
title: Aula 13 — De prompts manuais a loops autônomos
---

# Aula 13 — De prompts manuais a loops autônomos

> O salto de qualidade não vem de prompts melhores; vem de loops que se auto-corrigem.

## Do prompt ao loop

**Prompting** é uma conversa: você fala, o modelo responde, você fala de novo. O agente não age — ele emite texto.

**Loop engineering** é um ciclo: o agente **age** (edita, roda, testa), **observa** o resultado (exit codes, outputs, diffs) e **decide** o próximo passo — repetindo até o critério de saída.

```
PROMPT:   humano → modelo → texto → humano → modelo → ...
LOOP:     humano → agente → ação → observação → decisão → ação → ... → critério de saída
```

O prompt pede; o loop **trabalha**. O harness é o que torna o loop seguro: sem gates e verificação, um loop autônomo é uma avalanche.

## Os quatro componentes de um loop seguro

1. **Ação** — o agente executa ferramentas (editar, build, testar, git). O harness controla quais.
2. **Observação** — o agente lê o resultado real (exit code, output, diff, teste). O harness garante que ele não pule essa etapa.
3. **Decisão** — o agente decide o próximo passo com base no observado (corrigir, continuar, parar).
4. **Critério de saída** — a condição verificável que encerra o loop. O harness a impõe (Definition of Done, gates).

Sem o componente 4, o loop não termina ou termina cedo demais — o que une as aulas 07 e 09.

## Loop vs. fluxo de múltiplos loops

Um agente pode rodar um loop único: fazer → verificar → repetir. Mas um harness real orquestra **vários loops em sequência**, cada um com seu critério:

```
loop de escopo    → entender o que fazer (boot, leitura, decomposição)
loop de código    → implementar até o build+testes passarem
loop de review    → revisar o diff até os gates passarem
loop de evidência → gerar artefatos até o report/quiz fecharem
```

Cada loop tem ferramentas próprias, gates próprios e saída verificável. O harness define **quando um loop termina e o próximo começa** — isso é o que a Aula 14 formaliza como grafos.

## No nosso ecossistema

- **Um workflow engine**: cada fase do fluxo (plan → code → test → review → close) é um loop com critério de saída — avançar o item exige evidência, não apenas "continuar".
- **Factory**: `init.sh` é o loop de escopo; os pre-commit hooks fecham o loop de código; o `pr-hook.sh` fecha o loop de entrega.
- **Skills de artefato**: `feature-report` roda o loop de evidência — ler o diff/testes, sintetizar, gerar o HTML.

E o curso inteiro é um loop: cada aula termina com o quiz (observação), e o leitor decide o próximo passo (decisão).

## Loop autônomo em domínios

- **Finanças**: o harness de madrugada roda o loop relatório: ler planilhas → validar → processar → publicar → registrar. Sem humano até o café.
- **Games**: o loop de playteste simulado: gerar variações → simular → medir engajamento → iterar.
- **Comercial**: o loop de proposta: ler briefing + CRM → rascunhar → validar contra requisitos → finalizar.

O mesmo esqueleto de loop — o que muda são as ações e os critérios de saída.

## Principais aprendizados

1. Prompt pede; loop trabalha. O salto é de conversa para ciclo de ação.
2. Ação, observação, decisão e critério de saída são os quatro componentes.
3. O harness torna o loop seguro: sem gates, autonomia é avalanche.
4. Um fluxo completo é uma sequência de loops, cada um com sua saída verificável.

## Verifique seu aprendizado

```
"quiz me on a Aula 13"
```

**Próxima aula**: [14 — De loops únicos a engenharia de grafos](/pt-BR/lectures/lecture-14).