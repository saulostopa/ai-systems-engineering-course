---
name: roblox-publish
description: Prepara e valida a publicação de uma feature de jogo no Roblox — build Luau/Rojo, configuração de monetização e checklist de plataforma. Use quando o usuário pedir para publicar, subir build ou validar publicação no Roblox.
---

# Publicação Roblox validada

Publicar não é "subir e torcer": é passar pela validação de plataforma com
checklist verificável (Aula 10: E2E muda o resultado — aqui o "E2E" é o
publish pipeline).

## Gather

- A feature e seu estado em `feature_list.json`.
- O design doc (skills/game-design) — se não existir, não publique: a feature não tem especificação.
- Configs: `default.project.json` (Rojo), monetização (Developer Product / Game Pass IDs), permissões.

## Write / Validate — o checklist mecânico

1. **Build Luau** — o projeto compila sem erros (Rojo build / `rojo build`); exit 0 obrigatório.
2. **Assets** — todas as meshes/texturas referenciadas existem; nenhum asset quebrado (IDs válidos).
3. **Monetização** — cada Developer Product/Game Pass referenciado existe na página da experiência; preços preenchidos; nada apontando para produto inexistente.
4. **Segurança** — nada de dados sensíveis no código; scripts com permissões mínimas.
5. **Playteste simulado** — scripts/playtest-simulate.sh passou (a feature não sobe sem playteste).

## Output

- `relatorios/YYYY-MM-DD-<slug>-publish.md`: checklist com STATUS por item (PASS/FAIL + evidência — saída do comando).
- Qualquer FAIL bloqueia a publicação — registrar no log do harness (log-event.sh) e na feature.
- Só então: publicar e registrar a versão publicada na feature (`passing`).