---
title: Harness básico (download)
---

# Harness básico (download)

> O pacote que qualquer projeto pequeno baixa e roda em minutos. Versionado em
> `harness-basic/` na raiz deste repositório.

## Para quem é

Projetos pequenos e médios, times de 1-5 pessoas, sem infraestrutura própria de
processo. O harness básico entrega **o mínimo que muda o comportamento do
agente**: roteador, estado, políticas e dois gates mecânicos.

## O que o pacote contém

```
harness-basic/
├── package.json              # metadados (npm privado)
├── install.sh                # instalador: copia tudo + ativa hooks
├── templates/                # os arquivos do harness (mesma base da A4)
│   ├── AGENTS.md             # roteador (Aula 04)
│   ├── feature_list.json     # escopo com estado (Aula 08)
│   ├── claude-progress.md    # diário de sessão (Aula 05)
│   ├── session-handoff.md    # bilhete entre sessões (Aula 05)
│   ├── policies/             # scope-control, definition-of-done, evidence
│   └── init.sh               # boot (Aula 06)
├── scripts/
│   ├── gatekeeper.sh         # pre-commit: exige UMA feature in_progress
│   ├── validate-harness.sh   # health check completo do harness (Aula 11)
│   └── log-event.sh          # registro de fricção (Aula 11)
└── .githooks/
    ├── pre-commit            # roda gatekeeper.sh
    └── pre-push              # roda validate-harness.sh
```

## Instalação

```sh
git clone <este repo>              # ou copie a pasta harness-basic/
cd <seu-projeto>                   # repo git existente
./harness-basic/install.sh <seu-projeto>
./init.sh                          # valida o ambiente e imprime próximos passos
```

O instalador:
1. copia templates, scripts e hooks;
2. ativa `git config core.hooksPath .githooks`;
3. recusa sobrescrever arquivos existentes (use `--force` conscientemente).

## O que os gates fazem (testado)

| Gate | Quando | Comportamento |
|---|---|---|
| `pre-commit` (gatekeeper.sh) | todo commit | **Bloqueia** se 0 features `in_progress` (Aula 08) ou >1 (Aula 06/07); bypass consciente de 5 min via `.harness/skip-gatekeeper` |
| `pre-push` (validate-harness.sh) | todo push | Bloqueia se arquivos obrigatórios faltarem, JSON inválido, estados errados ou >1 `in_progress` |

O `validate-harness.sh` é o "health check" da Aula 11: 0 falhas = harness saudável;
qualquer falha = o harness quebrou e o push é bloqueado **antes** de publicar.

## Evolução natural

| Quando | Evolua para |
|---|---|
| Time cresceu, várias equipes no mesmo repo | [Harness grande (multi-time)](/pt-BR/harness-designs/enterprise-harness) — B2 |
| App com QA | [App Harness](/pt-BR/harness-designs/app-harness) — C |
| Contexto de negócio da área | [RAG Harness & Area Copilots](/pt-BR/harness-designs/rag-harness) — D |
| Domínio específico (games/finanças/comercial) | [Harnesses de domínio](/pt-BR/harness-designs/domain-harnesses) — E |

## Garantia

Nenhum arquivo é decorativo: cada um responde a uma pergunta do agente (o quê,
como, quando parar, onde estava) ou a um gate do processo (escopo, pronto,
evidência). Pasta de harness inchada é dívida, não rigor.