---
name: skill-guard
description: Escaneia uma skill em busca de prompt injection, exfiltração de dados, escalonamento de privilégio e risco de supply chain ANTES de instalá-la, usando o SkillSpector (NVIDIA). Use sempre que o usuário pedir para instalar, adicionar, baixar, avaliar ou confiar numa skill, plugin, agente ou servidor MCP vindo de fora do repositório.
---

# Skill Guard — nenhuma skill entra sem scan

Uma skill é instrução que o agente executa com **confiança implícita**: ela
entra no contexto e passa a dirigir o comportamento do modelo, sem revisão de
código, sem sandbox, sem CI. É a superfície de supply chain mais barata de
atacar e a mais cara de auditar depois que já rodou.

O levantamento da NVIDIA sobre 31.132 skills encontrou **26,1% com
vulnerabilidades** e **5,2% com sinal de intenção maliciosa**. Esta skill
responde a uma pergunta só, antes da instalação: **dá para instalar isto?**

Motor: [SkillSpector](https://github.com/NVIDIA/SkillSpector) (Apache-2.0),
**fixado na tag `v2.11.2`** e rodado em Docker — sem depender do Python local.

## Gather

- A **origem** da skill: repo git, URL, zip ou diretório já baixado.
- Quem pediu e **para quê** — o escopo declarado é o que o scan vai contradizer
  ou confirmar (uma skill de diagramas que lê `~/.ssh` não é um falso positivo).
- O `skills-lock.json` do repositório: se a skill já tem `scanVerdict`, confira
  se o `computedHash` ainda bate antes de confiar no veredito antigo.

## Run — o gate

```sh
harness-basic/scripts/gate-skill-scan.sh <alvo>      # dir, SKILL.md, .zip ou URL de repo
harness-basic/scripts/gate-skill-scan.sh --all       # todas as skills do repo
```

O gate constrói a imagem na primeira execução (1-2 min), confere o **pin de
supply chain** (a tag ainda aponta para o commit fixado?) e roda o scan em
modo **estático** (`--no-llm`) — determinístico, sem chave de API, válido em CI
e offline.

**Escaneie a origem antes de baixar.** `gate-skill-scan.sh https://github.com/x/y`
faz o scanner buscar o repo dentro do container. Clonar primeiro para escanear
depois já colocou o código na máquina.

## Ler o veredito

| Score | Severidade | O que fazer |
|---|---|---|
| 0-20 | LOW | Instalar — registre o veredito no `skills-lock.json`. |
| 21-50 | MEDIUM | **Ler os achados um a um** e decidir com o usuário. O gate avisa, não bloqueia. |
| 51-100 | HIGH / CRITICAL | Não instalar. O gate bloqueia (exit 1). |

Saídas: `0` aprovado · `1` bloqueado · `2` erro de execução. Relatórios JSON
completos ficam em `.harness/skill-scans/<caminho-da-skill>.json`.

Os achados vêm identificados por padrão — `SC2` (curl \| bash), `PE3`
(acesso a credenciais), `E1`/`E4` (transmissão externa e vazamento de
contexto), `P1`/`P2` (instruction override, instruções ocultas), `AR1`
(supressão de recusa), `TM2` (tool misuse). Cite o **ID e a linha** ao relatar,
nunca "o scanner não gostou".

## Depois do scan — registre

Toda skill aprovada entra no `skills-lock.json` com o veredito que a aprovou:

```json
"archify": {
  "source": "tt-a1i/archify",
  "computedHash": "111f1c0b…",
  "scanVerdict": {
    "scanner": "skillspector@v2.11.2",
    "scannerCommit": "69dcdfb74487d361ba4c811d088cfdea2ff3a9dc",
    "mode": "static",
    "scannedAt": "2026-09-17",
    "score": 22, "severity": "MEDIUM", "issues": 2, "suppressed": 57,
    "rawScore": 100, "rawIssues": 59,
    "decision": "ACEITO_COM_RESSALVA",
    "baseline": ".agents/skills/archify/.skillspector-baseline.yaml",
    "notes": "SC4 fast-uri==3.1.5 (4 CVEs, via ajv) e SC1 sem pin — reais, não suprimidos."
  }
}
```

**Guarde o score bruto junto com o triado.** Quem abrir o arquivo depois
precisa ver as duas coisas, não só a confortável. Sem esse registro o veredito
morre no terminal de quem rodou, e a próxima pessoa reinstala às cegas.

## Falsos positivos — o baseline

Achado que você abriu, leu e confirmou ser falso positivo entra num
`.skillspector-baseline.yaml` **dentro do diretório da skill** — com `reason`
escrito por extenso. Nunca na raiz do repositório: um baseline global desarma a
regra para todas as outras skills. O gate aplica sozinho quando encontra o
arquivo.

**Nunca suprima um achado que você não abriu**, e nunca suprima um achado
verdadeiro para deixar o gate verde — um achado real fica visível até ser
corrigido.

## Regras

- **Escaneie antes de baixar, não depois.** A ordem é o controle.
- **Um scan estático limpo não é uma skill auditada.** O modo estático julga
  *forma*, não intenção: ele pega `curl | bash` e leitura de `~/.ssh` com
  confiabilidade, e é fraco em instrução maliciosa escrita em prosa. Score 0
  significa "nenhum padrão conhecido", nunca "é seguro".
- **`cobertura: partial` não é aprovação plena** — parte do conteúdo não foi
  inspecionada. Reporte junto com o score; não o omita porque o score foi 0.
- **Nunca suba o limiar para fazer uma skill passar.** Se o usuário quer
  instalar algo que o gate bloqueou, essa é uma decisão dele, tomada com os
  achados na frente e registrada — não um ajuste silencioso de `SKILL_GUARD_MAX_SCORE`.
- **Skill de terceiro é reavaliada quando muda.** Veredito antigo com origem
  nova não vale; rode de novo.
- Escaneie também **servidores MCP** — o scanner tem padrões de MCP least
  privilege e tool poisoning, e um MCP compromete tanto quanto uma skill.
