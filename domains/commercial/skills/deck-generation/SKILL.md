---
name: deck-generation
description: Gera decks de apresentação e propostas a partir de briefing + contexto (CRM, dados de área) — com cada número citando a fonte. Use quando o usuário pedir uma apresentação, deck, proposta ou material comercial.
---

# Geração de deck com contexto

O deck nasce do briefing e do contexto — nunca do zero. Número sem fonte é
proibido (regra multi-domínio).

## Gather

1. **Briefing** — leia o briefing da demanda: público, objetivo, prazo, tom.
2. **Contexto** — consulte o Area Copilot (`area_harness query <area_root>`) e/ou o CRM: números de vendas, metas, histórico do cliente.
3. **Fonte** — cada número coletado guarda `FONTE: <arquivo> (linhas X-Y)`.

## Write

Estrutura do deck (slide deck em Markdown/HTML autocontido):

1. **Abertura** — o problema do público em 1 frase (do briefing).
2. **Prova** — 3-5 números com FONTE citada embaixo de cada um.
3. **Solução** — o que está sendo oferecido; sem promessa que o briefing não sustenta.
4. **Próximos passos** — prazo e responsável (do briefing).

Regras:
- Cada slide com número tem a fonte visível no rodapé.
- Sem número = sem fonte = sem slide.
- Nada inventado: se o contexto não tem o número, diga que falta (não estime).

## Output

- `materiais/YYYY-MM-DD-<slug>.md` (ou HTML) + lista de fontes citadas.
- Atualize a feature em `feature_list.json` (uma `in_progress` por vez).