---
title: qa-perf-triage
---

# qa-perf-triage — quando os gráficos estão planos e ainda assim está lento

> CPU tranquila. Memória tranquila. p99 triplicou. Esta skill é para o bug que
> só existe sob concorrência, e para o log de 120 mil linhas que guarda a
> resposta em algum lugar.

## Por que o grep não acha isso

Rode a demo — é determinística, não precisa de chave de API nem de rede:

```sh
python3 pilots/qa-perf-demo/triage_demo.py
```

Ela gera um log sintético de 162 mil linhas com uma regressão real enterrada, e
ranqueia de dois jeitos. **Por contagem**, que é o que o hábito de grep te dá:

```
 14.199  cache miss for key vehicles:brand:N
 14.009  connection returned to pool size=N
 13.809  retrying upstream call attempt N
```

Três formatos de ruído, dezenas de milhares de linhas, e nenhum deles é o bug.
**Por tempo total:**

```
  3685.4s  /api/dealers/{id}/stock      n=17980  p50=51ms   p95=630ms
   945.7s  /api/vehicles/search         n=54104  p50=17ms   p95= 26ms
   412.5s  /api/vehicles/{id}           n=35895  p50=12ms   p95= 17ms
```

O `/api/dealers/{id}/stock` atende **três vezes menos requisições** que a busca
e queima **quatro vezes mais tempo de parede**. O p95 dele é 24× o próprio p50
enquanto todo o resto fica plano — um endpoint degradando sozinho sob carga é
assinatura de contenção, não de query lenta.

Os dois movimentos que produziram isso: **normalizar antes de contar** (colapsar
todo número variável, para que 9 mil strings distintas virem os 3 formatos que
de fato são) e **ranquear por custo, não por frequência**.

## Por que o teste de carga sobe em rampa

Um teste plano em baixa concorrência não reproduz isso. O `locustfile` da skill
sobe 10 → 100 → 300 usuários de propósito:

```python
stages = [
    {"duration":  60, "users":  10, "spawn_rate":  1},
    {"duration": 180, "users": 100, "spawn_rate":  5},
    {"duration": 300, "users": 300, "spawn_rate": 10},
]
```

Bugs de contenção — esgotamento de pool, comboio de locks, N+1 sob leitura
paralela — aparecem a partir de um limiar. Um teste que nunca cruza esse limiar
reporta verde e não te ensina nada.

## O passo de IA, e o limite dele

Depois que a passada determinística estreita o campo, o `summarize_log.py`
fatia o que sobrou e pede clusters de anomalia a um modelo. Duas coisas a saber
antes de rodar:

- **Precisa de chave de API**, e é por isso que não faz parte da demo acima.
- **Ele redige antes de enviar** — tokens bearer, atribuições de
  `api_key`/`secret`/`password`, e-mails e números de cartão. Isso é
  *best-effort*, não garantia: um log com formato de segredo próprio da
  aplicação ainda precisa ser limpo na origem. Leia os padrões antes de apontar
  para um log de produção.

## Esta não entra no fluxo de entrega

Toda outra skill do catálogo é [cobrada por um fluxo](/pt-BR/harness-designs/enterprise-harness)
quando uma feature fecha. Esta não é, deliberadamente: é um **diagnóstico**,
buscado quando algo já está errado. Fazer toda entrega dever um teste de carga
adicionaria minutos a cada merge para pegar um problema que a maioria das
features não tem — e um gate que as pessoas detestam é um gate que as pessoas
contornam.

O que o harness faz no lugar é guardar a evidência: o `log-event.sh` registra a
fricção, para que na segunda vez que isso acontecer você não comece do zero.

## Instalação

```sh
npx skills add <a skill qa-perf-triage> --agent opencode --copy
```

**Relacionados**: [qa-playwright-e2e](/pt-BR/skills/qa-playwright-e2e) ·
[Aula 11 — Observabilidade dentro do harness](/pt-BR/lectures/lecture-11)
