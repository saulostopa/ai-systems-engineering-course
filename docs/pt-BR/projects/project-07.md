---
title: Projeto 07 — Harness grande (multi-time)
---

# Projeto 06 — Harness grande (multi-time)

> Instale um orquestrador na sua máquina, adote dois repositórios com ele, e tenha uma visão única sobre os dois — sem um único byte de estado de projeto sair dos repositórios.

## Objetivo

Tudo até o Projeto 05 vive dentro de um repositório só. Este projeto é o passo
em que um **time de times** vira gerenciável: um fluxo compartilhado, um gate que
roda igual em todo lugar, e um relatório só que lê através dos projetos.

A armadilha a evitar é a solução óbvia. O reflexo é colocar itens, comentários e
evidências num banco central — e no momento em que você faz isso, o projeto
deixa de conseguir se explicar sozinho. Apague a ferramenta e o histórico foi
junto. O [blueprint do harness grande](/pt-BR/harness-designs/enterprise-harness)
existe para tornar a outra escolha concreta.

## As duas camadas

```
~/wm/                          ← a raiz que guarda seus projetos
├── wm-harness/                ← A · orquestrador, instalado 1× por máquina
│   ├── bin/wm-harness           o CLI
│   ├── flows/                   definições de fluxo compartilhadas pela organização
│   └── harness-basic/           payload vendorado das camadas 1-2
├── catalogo/                  ← B · repositório adotado
│   ├── .harness/config.yaml     13 linhas: qual fluxo, qual versão do engine
│   └── docs/exec-plans/{active,done}
└── fipe/                      ← B · outro
```

A regra que decide onde qualquer coisa vai:

> **O orquestrador é dono do *como*. O repositório é dono do *o quê* e do
> *o que aconteceu*.**

E o teste para os casos em que você fica na dúvida:

> **Se apagar o orquestrador fizer o projeto perder informação sobre si mesmo,
> a peça está na camada errada.**

## Passo a passo

### 1. Instale o orquestrador

Ele fica **acima** das pastas dos seus projetos, porque é esse o diretório que
ele varre:

```sh
cd enterprise-harness
./install.sh --prefix ~/wm/wm-harness --projects ~/wm
export PATH="$HOME/wm/wm-harness/bin:$PATH"
wm-harness doctor
```

O `doctor` imprime onde ele mora, qual diretório varre, e quantos repositórios
encontrou. Zero, por enquanto.

### 2. Adote dois repositórios

Use dois repos pequenos reais — ou dois descartáveis, o que já basta para ver o
mecanismo:

```sh
wm-harness adopt ~/wm/catalogo
wm-harness adopt ~/wm/fipe --flow hotfix
wm-harness list
```

Agora abra o `~/wm/catalogo` e olhe o que de fato chegou lá. O esqueleto, as
políticas, os hooks, `docs/exec-plans/{active,done}` — e o `.harness/config.yaml`,
que é toda a amarração com o orquestrador. **Nenhum engine, nenhum
`node_modules`, nenhum banco.**

### 3. Rode uma feature sob um fluxo

```sh
cd ~/wm/catalogo
wm-harness plan new feature/OEM-123 "Validação de e-mail"
cat docs/exec-plans/active/feature-OEM-123.md
```

O id segue a convenção de branch da Webmotors — `feature/OEM-123`,
`bugfix/AC-455`, `release/EST-3445` — então plano e branch carregam o mesmo
nome. No disco a barra é achatada para `feature-OEM-123.md`.

Leia os passos e os critérios de saída que apareceram: eles foram **copiados do
fluxo**. É isso que separa uma definição de fluxo de um documento que ninguém
abre — ela produziu o checklist que você está prestes a executar.

Faça a feature de verdade. Depois tente arquivar antes de preencher a evidência:

```sh
wm-harness plan done feature/OEM-123
```

Ele recusa. Preencha a tabela de Evidência com um comando real e a saída real
dele, e rode de novo — ele reescreve o status e move o arquivo para `done/`.

### 4. Olhe através dos dois projetos

```sh
wm-harness status
wm-harness check
wm-harness report
```

O `check` não carrega uma segunda cópia das regras: ele roda o
`scripts/validate-harness.sh` **dentro de cada repositório**. Os gates em que um
time já confia são os gates que a organização enxerga.

### 5. Prove a invariante

Este é o passo que faz o projeto valer a pena:

```sh
rm -rf ~/wm/wm-harness          # apaga o orquestrador inteiro
cd ~/wm/catalogo
cat docs/exec-plans/done/feature-OEM-123.md   # a evidência continua aqui
bash scripts/validate-harness.sh     # o repo continua se validando sozinho
```

Nada foi perdido. Reinstalar o orquestrador recupera os dois repositórios
varrendo o diretório — não há registro para restaurar, porque nunca houve um.

## Verificação

- `wm-harness doctor` termina com `ORCHESTRATOR OK`.
- Um repo adotado tem `.harness/config.yaml` e **nenhuma** engrenagem do orquestrador.
- Um plano criado pelo `plan new` carrega os passos do fluxo que o repo declarou.
- O `plan done` recusa um plano cujas linhas de evidência ainda estão `_pending_`.
- O `check` falha num repositório cujo fluxo declarado não existe mais.
- Depois de apagar o orquestrador, todo repo adotado continua passando no próprio gate.

## Entrega

Dois repositórios adotados, uma feature fechada com evidência em
`docs/exec-plans/done/`, e a saída do `wm-harness report` mostrando os dois —
mais a sua resposta escrita para: *qual peça disso você teria colocado num banco
central, e quanto isso teria custado?*

::: tip O pacote oficial
O `enterprise-harness/` deste repositório é a implementação de referência, com
`scripts/validate-enterprise-harness.sh` e 19 testes ponta a ponta — incluindo um
que apaga o orquestrador e verifica que os projetos sobrevivem. Leia os testes
antes do código: eles enunciam o contrato de forma mais direta que a prosa.
:::

::: warning Onde isso para
O orquestrador agrega com um relatório de CLI, calculado na hora. Ele não tem
UI, nem servidor, nem sincronização entre máquinas — dois desenvolvedores veem
os mesmos números porque leem os mesmos repositórios. Se a sua organização
precisa de Kanban e dashboards de telemetria, isso é um engine de camada 3-4 por
cima, e o blueprint lista as opções.
:::

**Projeto anterior**: [05 — Area Copilot com RAG](/pt-BR/projects/project-05) ·
**Blueprint**: [Harness grande](/pt-BR/harness-designs/enterprise-harness)

**Você terminou os projetos!** Revise as [Aulas](/pt-BR/lectures/) ou explore os [Designs de Harnesses](/pt-BR/harness-designs/) para ver onde cada peça se encaixa no plano completo.
