---
title: Aula 07 — Excesso de autonomia e entrega incompleta
---

# Aula 07 — Excesso de autonomia e entrega incompleta

> O agente faz demais, entrega de menos e não percebe nenhum dos dois.

## O paradoxo do agente

Dê autonomia total a um agente e observe o padrão que se repete:

- **Overreach**: ele melhora o que não foi pedido, refatora o que não precisava, "aproveita para" corrigir dez coisas.
- **Under-finish**: ele considera pronto o que está pela metade — faltou o teste, faltou o doc, faltou rodar o build, faltou o e2e.

Os dois lados são o mesmo erro: **a autonomia sem limites não é poder, é descontrole**. O agente decide o escopo e decide o "pronto" — e ele é péssimo nos dois julgamentos.

## O antídoto: escopo declarado e verificação mecânica

### 1. Declare o escopo antes de editar

O `webmotors-harness-factory` exige (via `policies/scope-control.md`):

> "Registre seu escopo antes de implementar: **O que estou mudando? Por quê? Quais arquivos são esperados? O que está explicitamente fora do escopo? Como o sucesso será verificado?**"

Declarar o escopo antes não é formalidade: é o **contrato** entre o agente e o gate. Com o escopo escrito, o "pronto" deixa de ser opinião e vira comparação: entregou o que declarou?

### 2. Imponha gates mecânicos, não intenções

O factory mecaniza:

| Gate | Mecanismo | Quando bloqueia |
|---|---|---|
| Check de gate | `scripts/gatekeeper.sh` (pre-commit hook) | Qualquer edição fora do fluxo permitido |
| QA de frontend | `scripts/frontend-qa-gate.sh` (pre-commit) | Mudança de frontend sem cobertura E2E |
| PR | `scripts/pr-hook.sh` (pre-push) | Push sem relatório de PR |

A regra é: **se o processo depende da boa vontade do agente, ele não vai acontecer**. O que existe como script e hook acontece sempre.

### 3. Defina "pronto" como critério verificável

`policies/definition-of-done.md` + `policies/evidence-required.md`:

> "A conclusão exige evidência registrada (comandos executados, esperado vs. real). Nunca afirme 'done' sem prova."

## O gatekeeper do AgEnFK como exemplo vivo

O AgEnFK leva isso ao nível de workflow:

- **Item ativo obrigatório**: edições fora de um item em andamento são bloqueadas pelo gatekeeper.
- **DONE inalcançável por atalho**: não existe transição direta para DONE — só via `validate_progress` no passo final do fluxo, com evidência.
- **Teste como etapa**: o item passa por um estado de teste (`log-test PASSED/FAILED`) antes de concluir.

Vimos isso na prática na story A1: o agente tentou marcar DONE e o workflow **violou a regra** — a resposta foi mover para o fluxo correto, rodar o build, registrar o teste e só então concluir. O overreach ("eu terminei") foi interceptado pelo harness, não pelo bom senso.

## Escopo de tempo também conta

Autonomia excessiva também é **quando** o agente age. Por isso o harness define:

- em que estágio ele pode agir (flow steps);
- o que pode fazer sem pedir (ferramentas permitidas, arquivos esperados);
- o que exige aprovação humana (deploys, merges, mudanças de escopo);
- o que é proibido (fora do escopo declarado, editar arquivos alheios à feature).

## Na Webmotors — o espírito, não a letra

O objetivo do harness não é engessar — é dar **liberdade dentro de limites conhecidos**. O time de QA ganha gates de E2E que protegem o app; o time de finanças ganha validação de planilha antes do relatório subir; o time de games ganha validação de publish antes de subir o build para a plataforma. Cada área declara o que é "demais" e o que é "pela metade" — e o harness impede os dois.

## Principais aprendizados

1. Overreach e under-finish são o mesmo defeito: escopo e "pronto" sem contrato.
2. Escopo declarado antes de editar = contrato verificável de entrega.
3. Gate mecânico > intenção: se não é script/hook, não acontece.
4. "Done" é um estado do fluxo, não uma palavra na conversa.

## Verifique seu aprendizado

```
"quiz me on a Aula 07"
```

**Próxima aula**: [08 — Feature lists como primitivas de harness](/lectures/lecture-08).