---
name: game-design
description: Projeta features de jogo — persona, storytelling, mecânicas e economia — e gera o design doc. Use quando o usuário pedir para criar/desenhar um personagem, narrativa, mecânica, missão ou feature de jogo.
---

# Game design com harness

Projete a feature de jogo como uma feature de produto: escopo, verificação e
artefato — só que o "teste" é um playteste simulado.

## Gather

- A feature list do jogo (`feature_list.json` do playbook): qual feature, em que estado.
- O universo do jogo (docs de lore, personagens existentes, tom da narrativa).
- Restrições de plataforma (Roblox: engine Luau, limitações de meshes/partes).

## Write

O design doc em 5 seções, sempre nesta ordem:

1. **Persona** — quem joga esta feature: idade, motivação, dor. (Persona primeiro — mecânica depois.)
2. **Storytelling** — a narrativa: gancho, conflito, recompensa. Em uma frase: "o jogador faz X porque Y".
3. **Mecânica** — o loop jogável: input → regra → feedback. Descreva UMA mecânica central por doc.
4. **Economia** (se aplicável) — custos, recompensas e progressão em tabela; sem números inventados — cada valor com justificativa.
5. **Verificação** — os critérios do playteste simulado (scripts/playtest-simulate.sh): o que deve acontecer para a feature ser ACEITA.

## Output

- `design-docs/YYYY-MM-DD-<slug>.md` (ou HTML via feature-report se o time usa a base visual).
- Atualize a feature para `in_progress` (uma por vez) e registre a decisão de design no doc — nunca só na conversa.