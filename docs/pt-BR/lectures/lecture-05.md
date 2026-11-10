---
title: Aula 05 — Continuidade em tarefas longas
---

# Aula 05 — Continuidade em tarefas longas

> Tarefas de engenharia duram dias. Sessões de agente duram minutos. O harness é a ponte.

## O problema fundamental

Um agente tem uma janela de contexto limitada e uma sessão finita. Uma feature de verdade — do escopo ao deploy — atravessa:

- várias sessões do mesmo agente;
- vários agentes (planejamento, código, review, teste);
- vários dias corridos (com a mente do agente "desligada" entre eles).

Sem estado persistente, cada sessão recomeça do zero: o agente relê tudo, re-decide o que já foi decidido, e o trabalho oscila.

## Estado entre sessões: o trio do harness

O `harness-factory` resolve com três arquivos complementares:

```
feature_list.json      → o QUE existe e em que estado (fonte de verdade de escopo)
progress.md            → o que aconteceu NESTA sessão (trabalho recente, falhas, próxima ação)
session-handoff.md     → o que fica PARA a próxima sessão (verificado, quebrado, próximo passo)
```

A divisão de papéis é o que importa:

- **feature_list** é o *mapa* — muda pouco, é a verdade do escopo.
- **progress** é o *diário* — muda a cada sessão, documenta o caminho.
- **handoff** é o *bilhete* — o resumo que permite à próxima sessão (agente ou humano) retomar sem reler tudo.

## A retomada como protocolo

Uma boa retomada segue um protocolo fixo — e o harness o transforma em hábito:

1. **Leia o handoff** antes de tocar em qualquer arquivo.
2. **Re-verifique** o que o handoff afirma (git status, testes) — nunca confie na narração.
3. **Atualize o progress** com o trabalho real da sessão atual.
4. **Atualize o handoff** antes de encerrar: o que ficou verificado, o que quebrou, qual a próxima ação.
5. **Atualize o feature_list** com o estado real das features.

## Na prática — a continuidade na prática

Um workflow engine formaliza esse protocolo em cima do repo: cada story carrega status, comentários com evidência e trilha de teste. Quando o agente retoma a story A2, ele não pergunta "onde paramos?" — ele lê a story, os comentários e o estado, e continua. A tríade de arquivos acima faz o mesmo trabalho sem engine nenhum; o que importa é que o registro esteja no repositório.

Na prática desta semana: a story A1 foi concluída numa sessão; a evidência (build OK, test PASSED) ficou registrada; quando retomamos, o estado estava íntegro sem nenhuma conversa anterior na memória. **A continuidade não veio da memória do agente — veio do harness.**

## O que NÃO funciona

| Estratégia | Por que falha |
|---|---|
| "Manter a conversa aberta" | Janela de contexto esgota; sessão cai; memória morre |
| Re-descrever o contexto em cada prompt | Custo, erro humano, divergência |
| Confiar que o agente "se lembra" | Não há memória entre sessões — só o que está no repo |
| Handoff na cabeça (não escrito) | Esquecimento e ruído garantidos |

## Principais aprendizados

1. Tarefa longa ≠ sessão longa: o trabalho dura mais que qualquer janela de contexto.
2. Mapa (feature_list) + diário (progress) + bilhete (handoff) cobrem o ciclo de vida.
3. Retomar é um protocolo, não um palpite: ler, re-verificar, atualizar.
4. Continuidade é propriedade do harness, não do modelo.

## Verifique seu aprendizado

```
"quiz me on a Aula 05"
```

**Próxima aula**: [06 — Inicialização como fase própria](/pt-BR/lectures/lecture-06).