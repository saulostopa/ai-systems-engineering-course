# AGENTS.md — Roteador de harness básico

> Roteador curto (Aula 04). Aponte, não empilhe. Substitua os exemplos pelos
> caminhos reais do seu projeto.

## 1. O que este repositório é

[Uma linha: o produto e o contexto — substitua]

## 2. O que ler primeiro

1. `README.md` — visão geral do projeto.
2. `feature_list.json` — fonte de verdade do que fazer.
3. `claude-progress.md` — progresso da sessão atual.
4. `session-handoff.md` — estado deixado pela sessão anterior.

## 3. Como determinar o estado atual

- `feature_list.json` — status por feature (`not_started` / `in_progress` / `blocked` / `passing`).
- `claude-progress.md` — trabalho recente, atual, falhas, próxima ação.
- `session-handoff.md` — o que está verificado, o que está quebrado, próximo passo.
- `git status` / `git diff` — árvore de trabalho.

## 4. Como escolher uma tarefa

- Apenas uma feature `in_progress` por vez (exceção exige registro em `claude-progress.md`).
- Escolha a `not_started` de maior prioridade.
- Declare o escopo antes de editar (`policies/scope-control.md`):
  - O que vou mudar? Por quê?
  - Quais arquivos são esperados? O que está FORA do escopo?
  - Como o sucesso será verificado?

## 5. Como verificar o trabalho

- Siga `policies/definition-of-done.md` e `policies/evidence-required.md`.
- Rode o build e os testes do projeto (comandos abaixo).
- Nada é "pronto" sem evidência registrada (comando + resultado).
- **Git é a verdade**: re-execute testes e confira `git diff`; nunca confie em narração.

## 6. Como terminar a sessão

1. Atualize `feature_list.json` (estados reais).
2. Atualize `claude-progress.md` (o que foi feito, o que falhou, próxima ação).
3. Atualize `session-handoff.md` (seções obrigatórias no cabeçalho).
4. Rode os testes — devem passar.
5. Commit coerente (`policies/git.md` se existir).

## 7. Comandos do projeto

<!-- Substitua pelos comandos reais -->

```bash
npm run build    # build
npm test         # testes
npm run dev      # desenvolvimento
```

## 8. Onde a documentação vive

| Preciso de | Vou em |
|---|---|
| Regras de processo | `policies/*.md` |
| Arquitetura | `docs/architecture/` |
| Skills | `.claude/skills/` (ou `.agents/skills/`) |
| Estado | `feature_list.json`, `claude-progress.md`, `session-handoff.md` |