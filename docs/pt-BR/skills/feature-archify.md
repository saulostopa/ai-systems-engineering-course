---
title: feature-archify
---

# feature-archify — o diagrama que a entrega deve

> Uma feature que só deixa código obriga a próxima pessoa a ler o diff para
> entender. Esta skill faz a entrega se explicar sozinha — com um diagrama
> **validado antes de ser entregue**, não desenhado por opinião.

Ela embrulha o **Archify** ([tt-a1i/archify](https://github.com/tt-a1i/archify),
MIT) dentro do harness: quando uma feature fecha, o agente escreve uma descrição
tipada do que foi construído, e o harness renderiza e verifica.

## Veja primeiro

<a href="/demos/feature-branch-lifecycle.html" target="_blank" rel="noopener">
<strong>▶ feature/OEM-123 — do ticket à produção</strong></a> — o ciclo de vida do branch
que você vive de verdade: gate de commit, CI, review, deploy, e os três jeitos
de cada um te mandar de volta para o teclado.

<a href="/demos/harness-basic-pipeline.html" target="_blank" rel="noopener">
▶ O pipeline do harness básico</a> — a mesma skill aplicada ao próprio harness.

É um único HTML autocontido. Coisas para experimentar com ele aberto:

- **Troque as views** — `#view=happy-path` e `#view=gates` são duas leituras do
  mesmo grafo, não dois desenhos que podem divergir.
- **Siga a aresta de retorno do gatekeeper** — o laço "sem feature — declare uma"
  de volta ao `feature_list`. Esse caminho de falha é a razão de o diagrama ser um
  workflow e não um fluxograma.
- **Leia os cards** — um diz o que o leitor deve aprender, outro registra o
  achado do piloto G1.

## Por que "verificável" é o ponto inteiro

A maioria dos diagramas apodrece porque nada consegue dizer que estão errados. O
Archify passa o JSON tipado por **validadores atômicos** — schema, layout,
roteamento, clearance, legibilidade — e se recusa a entregar um artefato que
falhe em qualquer um.

Isso não é teórico. Preparando esta página, a demo parou de passar:

```
composition/desktop-readability
  text: "feature passing — report + quiz generated"
  projectedFontPx: 5.64   minimumProjectedFontPx: 6
```

Um rótulo tinha crescido o bastante para renderizar abaixo do piso de
legibilidade em 1440×900. Nenhuma revisão humana pegaria 5,64 contra 6. A
correção foi encurtar o rótulo para `feature passing`, e o artefato voltou ao
`showcase` — **0 erros, 9/9 checks**. Evidência antes do "pronto", aplicada ao
próprio diagrama (Aula 09).

## Como o harness chama a skill

A divisão importa: **o agente escreve, o harness verifica**. Nenhum script
infere um diagrama a partir de um diff — e ninguém deve ser encarregado de
lembrar de validar um.

```bash
# 1. o agente escreve a fonte: uma descrição tipada do que foi construído
#    docs/artifacts/feature-OEM-123.json

# 2. o harness renderiza e valida
./scripts/artifacts.sh feature/OEM-123
# [artifacts] OK — docs/artifacts/feature-OEM-123.html passed at showcase quality
```

E não é opcional onde importa. O fluxo `feature-default` declara:

```yaml
artifacts:
  - diagram
```

Então o `wm-harness plan done` recusa arquivar o plano sem ele:

```
[wm-harness] ERROR: feature/OEM-123 owes a delivery diagram
             (flow 'feature-default') — run: ./scripts/artifacts.sh feature/OEM-123
```

O fluxo `hotfix` declara `artifacts: []` de propósito — um incidente não deve
esperar por um diagrama, e o item de melhoria seguinte é onde a explicação é
feita.

## A paleta Webmotors

O Archify não tem campo de tema: `visual_preset` oferece quatro visuais fixos e
`brandMark` é um logo por nó. O que ele **expõe** são 38 custom properties CSS no
HTML entregue, então o `scripts/eleanor-theme.css` sobrescreve depois do
`archify deliver` — sem tocar na geometria, que é justamente o que o validador
aprovou.

Dois detalhes custaram uma rodada de depuração cada:

- O Archify escopa a paleta como `[data-preset="signal-flow"][data-theme="light"]`,
  que **tem especificidade maior que um `:root`** puro. A primeira tentativa
  parecia aplicada e não mudava nada.
- O Eleanor é um sistema de dois modos e o artefato tem um toggle light/dark
  funcionando, então entregar só a paleta escura transformaria o toggle num
  botão inútil.

Contraste não se herda de uma marca, se mede: o `scripts/check-contrast.py`
percorre os dois blocos e falha abaixo do piso — 4,5:1 para texto (WCAG 1.4.3),
3:1 para traços (1.4.11). Ele pegou três tokens que a primeira passada errou,
um deles em 2,7:1.

```sh
python3 scripts/check-contrast.py scripts/eleanor-theme.css
# 28 token(s) checked, 0 below floor
```

## Escolhendo o tipo

| Tipo | Use quando a pergunta é |
|---|---|
| `workflow` | como o processo roda, incluindo os caminhos de falha |
| `sequence` | quem chama quem, em que ordem |
| `dataflow` | de onde o dado vem e onde ele para |
| `architecture` | quais são as peças e como estão ligadas |
| `lifecycle` | por quais estados essa coisa passa |

O tipo errado produz um diagrama válido que responde uma pergunta que ninguém
fez. Escolha pela pergunta do leitor, não pelo formato do código.

## Instalação

```sh
npx skills add tt-a1i/archify --agent opencode --copy
```

::: warning Passe pelo gate antes
Uma skill é instrução que o agente executa com confiança implícita. O Archify
está no catálogo porque passou pelo [skill-guard](/pt-BR/skills/skill-guard) —
escaneado, triado achado a achado, com um patch local registrado no
`skills-lock.json`. Faça o mesmo com qualquer coisa que você adicionar.
:::

## O que vem neste repositório

| Peça | O que é |
|---|---|
| `skills-artifacts/feature-archify/SKILL.md` | O wrapper, no padrão do curso (Gather / Write / Output) |
| `.agents/skills/archify/` | O Archify em si (MIT), escaneado e fixado no `skills-lock.json` |
| `harness-basic/scripts/artifacts.sh` | O passo de renderizar-e-validar, instalado em todo repo adotado |
| `pilots/archify-demo/*.json` | A fonte da demo — reproduzível, um comando |

**Relacionados**: [feature-report](/pt-BR/skills/feature-report) · [feature-quiz](/pt-BR/skills/feature-quiz) ·
[skill-guard](/pt-BR/skills/skill-guard) · [Criar uma nova skill](/pt-BR/skills/how-to-create)
