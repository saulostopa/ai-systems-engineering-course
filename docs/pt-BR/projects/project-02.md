---
title: Projeto 02 — Harness básico instalável
---

# Projeto 02 — Harness básico instalável

> Empacote o harness mínimo do Projeto 01 em algo que qualquer projeto pequeno baixa e roda em 5 minutos.

## Objetivo

Construir o **pacote de harness básico**: um instalador que entrega AGENTS.md
(roteador), estado de features, progress/handoff, políticas essenciais, planos
de execução e validação mecânica a qualquer repositório pequeno. O perfil
padrão do curso também inclui sete skills reutilizáveis em `.agents/skills/`.

Isto é literalmente a Story **B1** do nosso plano — e este projeto te ensina a construí-lo antes de o curso entregar o oficial.

## Estrutura do pacote

```
harness-basico/
├── init.sh                    # valida ambiente, imprime próximos passos
├── AGENTS.md                  # roteador curto (Aula 04)
├── feature_list.json          # fonte de verdade de escopo (Aula 08)
├── progress.md                # diário de sessão (Aula 05)
├── session-handoff.md         # bilhete para a próxima sessão (Aula 05)
├── policies/
│   ├── scope-control.md       # escopo antes de editar (Aula 07)
│   ├── definition-of-done.md  # "pronto" verificável (Aula 09)
│   └── evidence-required.md   # evidência antes de "done" (Aula 09)
├── scripts/                   # validação, gates, artefatos e scan de skills
├── .githooks/                 # enforcement pre-commit e pre-push
└── .agents/skills/            # perfil padrão (sete skills do curso)
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

Use os modelos da [Biblioteca](/pt-BR/resources/templates): `feature_list.json` com 3-5 features de exemplo, `progress.md` e `session-handoff.md` com os cabeçalhos obrigatórios (Aula 05).

### 4. Instale num repo real

Use um destino explícito em vez de copiar arquivos manualmente:

```bash
./install.sh /caminho/absoluto/do/projeto
cd /caminho/absoluto/do/projeto
./init.sh
./scripts/validate-harness.sh
```

O instalador deve proteger arquivos existentes e exigir `--force` para uma
substituição consciente. Quando o destino é um repositório Git, ele configura
`core.hooksPath=.githooks`.

### 5. Suporte um modo explícito de auto-instalação em pacotes derivados

Se a própria pasta do pacote será gerenciada pelo harness, torne a intenção
explícita:

```bash
git init
./install.sh --self
```

Nunca deixe `./install.sh .` sobrescrever silenciosamente o estado do pacote.
`--self` é o contrato separado de uma distribuição derivada; o núcleo
standalone pode continuar exigindo outro destino.

### 6. Inclua o perfil padrão de skills

Instale em `.agents/skills/`: `feature-report`, `feature-quiz`,
`feature-archify`, `skill-guard`, `qa-playwright-e2e`, `qa-perf-triage` e
`agentic-navigation`. Mantenha os assets Eleanor compartilhados em
`.agents/skills/assets/` e valide que toda skill tem um `SKILL.md` com
frontmatter correspondente.

## Verificação

- `./init.sh` roda sem erro e imprime os próximos passos.
- `./scripts/validate-harness.sh` valida o núcleo e as sete skills padrão.
- Instalação limpa, recusa de sobrescrita e reinstalação com `--force` têm testes.
- O modo `--self` de um pacote derivado é testado separadamente da instalação normal.
- Um agente novo, sem contexto, consegue: ler o AGENTS.md → escolher a feature → implementar → provar (build+teste) → atualizar os estados.
- O handoff escrito por uma sessão permite a outra retomar sem perguntar nada.

## Entregável

Seu pacote versionado num repositório, testes do instalador, o perfil padrão de
skills (quando escolhido) e a evidência da primeira feature executada com ele.

::: tip Status
O pacote oficial, com scripts de hooks e validação completos, é a Story **B1** do curso (EPIC B). Este projeto te dá a base para revisar o oficial com olhar crítico.
:::

**Próximo projeto**: [03 — Harness de App com QA](/pt-BR/projects/project-03).
