---
title: feature-animation
---

# feature-animation — uma viagem real, um passo por vez

> Um diagrama mostra o formato de um sistema. Uma animação te leva por **uma
> jornada concreta** — um commit, uma requisição, um registro — com o valor real
> que ele carrega em cada passo. É o artefato para "mas o que acontece de fato?"

## Veja primeiro

<a href="/demos/demo-animation.html" target="_blank" rel="noopener">
<strong>▶ Um commit atravessando os gates</strong></a> — aperte **Avançar** e veja uma
mudança em `price-tag.tsx` encontrar cada gate pela frente.

<a href="/demos/demo-consent-journey.html" target="_blank" rel="noopener">
<strong>▶ Do consentimento à identidade</strong></a> — um visitante responde ao banner do
Fuse CMP e vira um `acid` do AdFixus que chega ao GAM como PPID. Cinco estágios,
tirados do `ignition-adfixus-tag-docs`.

A segunda vale abrir mais pelo card embaixo dela do que pela animação: ele
registra que, para um visitante brasileiro, a jornada **nunca sai do estágio 1**,
porque o CMP reporta `gdprApplies: false` e os eventos `tcloaded` /
`useractioncomplete` em que a ponte filtra nunca chegam. Uma animação que
mostrasse só o caminho feliz teria sido uma mentira agradável.

Quatro estágios, e todo valor neles é real:

| Estágio | O que carrega |
|---|---|
| `git commit` | `src/components/price-tag.tsx` — preparado, nada verificado ainda |
| `gatekeeper.sh` | `1 in_progress ✓` — o escopo foi declarado antes da edição |
| `e2e-gate.sh` | `e2e/test_price.py ✓` — o teste veio no mesmo commit |
| `commit` | `a1b2c3d feature/OEM-123` |

A legenda é `aria-live`, então um leitor de tela é informado de qual estágio
está ativo em vez de ter que notar uma borda mudando de cor. E o autoplay é
opt-out por preferência: `prefers-reduced-motion` o impede antes de começar.

## O que estava errado, e não era a skill

A página que você está lendo era um stub de nove linhas, então era justo
suspeitar que a skill tivesse se perdido. Não tinha — o
`harness-agent-skills/animations/` guardava um artefato funcional de
2026-08-21, com playback de verdade. O que aconteceu é mais específico, e vale
saber se você escreve skills:

O `feature-animation` manda splicar o `system.css` e o `skeleton.html` do
`feature-report`. Quando esses assets foram reescritos para o Eleanor, **o
report e o quiz foram levados junto e os estilos de animação não**. O CSS v1
tinha oito regras `.flow-*`; o v2 tinha zero. A skill continuou apontando para
um design system que já não sabia estilizar o que ela produzia.

Por isso o artefato antigo ainda parecia certo — foi gerado antes da migração —
enquanto qualquer coisa gerada depois sairia sem estilo. **Uma skill que depende
de assets compartilhados quebra em silêncio quando esses assets seguem em
frente.**

Dois defeitos vieram junto, ambos corrigidos:

- **O accent era o azul `#2554c7`.** Todo o resto do catálogo já tinha migrado
  para o vermelho Eleanor. Portado: a demo acima mede `rgb(216, 31, 65)`.
- **A track rolava horizontalmente.** A 1440px a linha tinha 1355px dentro de
  uma caixa de 1040px, então o último estágio ficava fora da tela no
  carregamento — um estágio que o leitor nunca soube que existia. Agora os
  estágios dividem a linha em vez de exigir largura dela, e no celular a track
  vira coluna.

## Escolhendo os estágios

De três a seis. Menos não justifica uma animação; mais não cabe na linha, e a
correção para "mais" é agrupar estágios vizinhos que tratam do mesmo assunto —
não encolher as caixas.

A regra que decide se um estágio é real: **você consegue nomear a função,
endpoint ou script que ele representa, e o valor de exemplo é algo que poderia
mesmo aparecer ali.** `Estágio 2` com `dado de exemplo` é um placeholder
fantasiado de diagrama.

## Onde ela fica entre as outras

| Artefato | Responde |
|---|---|
| [feature-report](/pt-BR/skills/feature-report) | o que foi entregue, e o que prova |
| [feature-archify](/pt-BR/skills/feature-archify) | como o sistema construído está ligado |
| **feature-animation** | como é uma viagem real por dentro dele |
| [feature-quiz](/pt-BR/skills/feature-quiz) | se o leitor entendeu alguma coisa |

Ela **não** é cobrada pelo fluxo padrão. O diagrama já carrega a explicação da
entrega, e exigir os dois taxaria todo merge para cobrir um caso que a maioria
das features não tem. Adicione `animation` à lista `artifacts:` de um fluxo
quando a feature for uma que as pessoas vão precisar que alguém caminhe junto.

```sh
cd skills-artifacts && python3 scripts/build-demo.py
```

**Relacionados**: [feature-archify](/pt-BR/skills/feature-archify) · [feature-report](/pt-BR/skills/feature-report) ·
[Criar uma nova skill](/pt-BR/skills/how-to-create)
