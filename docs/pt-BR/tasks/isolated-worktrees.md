---
title: Feature — fluxo com worktrees isoladas
---

# Feature — fluxo com worktrees isoladas

Status: **in_progress** · Priority: **P0** · Escopo: curso, `harness-basic` e `adk-rag-postgres-harness`

## Decisão

Usar worktrees Git isoladas como limite padrão para trabalho paralelo de agentes.
O checkout principal fica reservado para integração. Cada feature recebe sua
própria worktree e branch, e a integração acontece em uma worktree desanexada
criada a partir da referência atual de integração.

O curso documenta o contrato independente de provider. O `harness-basic` instala
o contrato por meio do `AGENTS.md` e das políticas geradas. O harness RAG com
PostgreSQL adiciona a regra de que o repositório indexado e o serviço de banco
devem estar presos a uma revisão conhecida e separados do checkout que recebe
atualizações.

## Contrato

### Worktree da feature

```bash
git fetch origin
git worktree add ../wt-<feature-id> -b feature/<id> origin/develop
cd ../wt-<feature-id>
```

Cada worktree possui sua própria instalação de dependências, caches e builds.
Arquivos `.env*` reais nunca devem ser copiados para uma worktree.

### Worktree de integração

```bash
git fetch origin
git worktree add --detach ../wt-integrate origin/develop
git -C ../wt-integrate merge --no-ff feature/<id>
cd ../wt-integrate
<comandos de build e testes>
git push origin HEAD:refs/heads/develop
```

Se a branch ou o remoto divergirem, o agente para e pergunta ao dono do
repositório.

### Worktree de serviço fixo

```bash
git worktree add --detach ../wt-service <known-sha>
cd ../wt-service
<inicie o serviço com configuração explícita e banco sintético>
```

O serviço deve ler esse checkout fixado e não acompanhar outra worktree que
esteja recebendo atualizações.

### Limpeza e comandos proibidos

```bash
git worktree list
git worktree remove ../wt-<feature-id>
git worktree prune
```

Remova worktrees órfãs sem `--force`; reserve `--force` para worktrees
temporárias do CI local. A mesma branch não pode estar em duas worktrees.

Agentes não devem executar `reset --hard`, pushes forçados, `checkout -B`,
`switch -C`, `branch -f/-D`, `worktree add -B`, `clean -f`, `stash drop/clear`,
rebase ou amend de commit publicado. Divergência exige parar e perguntar.

## Fatias de implementação

1. Adicionar este contrato em inglês e português ao backlog do curso.
2. Adicionar a política e a seção do router geradas pelo Basic.
3. Adicionar a seção de worktree e serviço fixo ao RAG com PostgreSQL.
4. Adicionar o guard provider-neutral `git-safe` e o guard de fast-forward do
   pre-push ao Basic e ao RAG com PostgreSQL.
5. Verificar que os checkouts atuais não foram modificados e que os novos
   arquivos não contêm secrets nem valores de ambiente.
6. Executar os testes estruturais relevantes em cada worktree isolada.

## Critérios de aceite

- Um novo Basic instala as instruções de worktree por seus templates.
- As instruções do Basic cobrem feature, integração e serviço.
- O README do RAG PostgreSQL explica o isolamento da pasta indexada e do banco.
- Os dois harnesses documentam limpeza, unicidade de branch e proibição de
  comandos Git destrutivos.
- O Basic e o RAG PostgreSQL recusam mecanicamente comandos destrutivos por
  `git-safe`, e seus hooks pre-push recusam exclusões e updates non-fast-forward.
- O curso referencia o contrato nos dois harnesses de projeto.
- Nenhum valor de `.env*` é lido, copiado ou commitado.
- A implementação fica limitada a documentação e políticas do harness.

## Fora de escopo

- Criar worktrees automaticamente para cada invocação de agente.
- Uma deny list específica de um único agente de programação.
- Alterar código da aplicação, schema do banco ou comportamento de runtime.

## Verificação atual

- `harness-basic`: `npm run validate` passou; o gate E2E passou `7/7`; os testes
  estruturais do Skill Guard passaram, com dois casos opcionais do fixture do
  curso pulados.
- `adk-rag-postgres-harness`: `uv run --with pytest --with
  'psycopg[binary]' --with tree-sitter --with tree-sitter-javascript --with
  tree-sitter-typescript pytest -q` passou com `2 passed`.
- Os testes da política Git cobrem a lista de comandos destrutivos, exclusão de
  refs e o comportamento fast-forward/non-fast-forward do pre-push (`17/17`).
- As duas worktrees de implementação passaram em `git diff --check`.
- Os checkouts originais do curso e dos harnesses permaneceram limpos.

## Locais da implementação

- Contrato do curso: esta tarefa e sua versão em inglês.
- Distribuição Basic: `harness-basic/templates/AGENTS.md` e
  `harness-basic/templates/policies/git-worktrees.md` no
  [repositório de harnesses](https://github.com/saulostopa/harnesses).
- Distribuição RAG PostgreSQL: `adk-rag-postgres-harness/README.md` no
  [repositório de harnesses](https://github.com/saulostopa/harnesses).
