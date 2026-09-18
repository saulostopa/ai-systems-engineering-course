---
title: Projeto 02 — Harness básico instalável
---

# Projeto 02 — Harness básico instalável

> Empacote o harness mínimo do Projeto 01 em algo que qualquer projeto pequeno baixa e roda em 5 minutos.

## Objetivo

Construir o **pacote de harness básico**: um conjunto de arquivos que você copia para qualquer repo pequeno e que entrega AGENTS.md (roteador), feature list, progress/handoff, políticas essenciais e um `init.sh` de inicialização.

Isto é literalmente a Story **B1** do nosso plano — e este projeto te ensina a construí-lo antes de o curso entregar o oficial.

## Estrutura do pacote

```
harness-basico/
├── init.sh                    # valida ambiente, imprime próximos passos
├── AGENTS.md                  # roteador curto (Aula 04)
├── feature_list.json          # fonte de verdade de escopo (Aula 08)
├── claude-progress.md         # diário de sessão (Aula 05)
├── session-handoff.md         # bilhete para a próxima sessão (Aula 05)
├── policies/
│   ├── scope-control.md       # escopo antes de editar (Aula 07)
│   ├── definition-of-done.md  # "pronto" verificável (Aula 09)
│   └── evidence-required.md   # evidência antes de "done" (Aula 09)
└── skills/                    # (opcional) pacote do harness-agent-skills
```

## Passo a passo

### 1. Escreva o `init.sh`

O `init.sh` do `webmotors-harness-factory` é o modelo:

```bash
#!/bin/bash
# init.sh — inicializa o harness básico num projeto
set -e
echo "Verificando diretório..."
[ -f "AGENTS.md" ] || echo "⚠️  AGENTS.md ausente — copie o pacote para a raiz"
node --version && npm --version
echo "Próximos passos:"
echo "  1. Leia AGENTS.md"
echo "  2. Escolha UMA feature em feature_list.json"
echo "  3. Rode os testes do projeto"
```

### 2. Escreva as políticas (2-5 linhas cada)

`definition-of-done.md`:

```markdown
# Definition of Done
Uma feature está pronta quando:
1. O build passa (saída anexada).
2. Os testes passam, sem redução na suíte.
3. O diff contém só o escopo declarado.
4. A evidência está registrada (comando + resultado).
```

### 3. Adicione os arquivos de estado

Use os modelos da [Biblioteca](/pt-BR/resources/templates): `feature_list.json` com 3-5 features de exemplo, `claude-progress.md` e `session-handoff.md` com os cabeçalhos obrigatórios (Aula 05).

### 4. Instale num repo real

Copie o pacote para um projeto pequeno seu, rode `./init.sh`, execute uma feature de ponta a ponta e registre a evidência.

## Verificação

- `./init.sh` roda sem erro e imprime os próximos passos.
- Um agente novo, sem contexto, consegue: ler o AGENTS.md → escolher a feature → implementar → provar (build+teste) → atualizar os estados.
- O handoff escrito por uma sessão permite a outra retomar sem perguntar nada.

## Entregável

Seu pacote versionado num repo (ou numa pasta `templates/` do seu harness) + a evidência da primeira feature executada com ele.

::: tip Status
O pacote oficial, com scripts de hooks e validação completos, é a Story **B1** do curso (EPIC B). Este projeto te dá a base para revisar o oficial com olhar crítico.
:::

**Próximo projeto**: [03 — Harness de App com QA](/pt-BR/projects/project-03).