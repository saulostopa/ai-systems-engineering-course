#!/bin/bash
# init.sh — inicializa o harness básico num projeto (modelo do webmotors-harness-factory)
# Uso: copie o pacote templates/ para a raiz do projeto e rode: ./init.sh
set -e

echo "=== Harness básico — inicialização ==="

# 1. Diretório de trabalho
echo "[1/4] Verificando diretório de trabalho..."
[ -f "AGENTS.md" ] || { echo "  ERRO: AGENTS.md ausente. Copie o pacote para a raiz do projeto."; exit 1; }
echo "  OK: AGENTS.md presente"

# 2. Ferramentas
echo "[2/4] Verificando ferramentas..."
command -v node >/dev/null 2>&1 && echo "  OK: node $(node --version)" || echo "  AVISO: node não encontrado (ajuste conforme o projeto)"
command -v npm  >/dev/null 2>&1 && echo "  OK: npm $(npm --version)" || echo "  AVISO: npm não encontrado"

# 3. Hooks (opcional — copie de .githooks/ do factory se tiver)
echo "[3/4] Verificando hooks..."
if git rev-parse --git-dir >/dev/null 2>&1; then
  HOOKS=$(git config core.hooksPath || echo "não configurado")
  echo "  hooksPath: $HOOKS"
else
  echo "  AVISO: não é um repositório git"
fi

# 4. Baseline
echo "[4/4] Baseline do projeto..."
if [ -f "package.json" ]; then
  npm run build >/dev/null 2>&1 && echo "  OK: build passou" || echo "  AVISO: build falhou — execute 'npm run build' e investigue antes de trabalhar"
else
  echo "  AVISO: sem package.json (projeto de outra natureza — ajuste esta seção)"
fi

echo
echo "=== Próximos passos ==="
echo "  1. Leia AGENTS.md"
echo "  2. Escolha UMA feature em feature_list.json (status: in_progress)"
echo "  3. Declare o escopo em policies/scope-control.md"
echo "  4. Implemente e verifique (build + testes + evidência)"