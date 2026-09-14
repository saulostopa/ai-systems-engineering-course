# Design system v2 — Eleanor (Webmotors)

A evolução do design das skills de artefato: os princípios v1 (Carbon,
Lightning, Fluent, Material, GOV.UK, Atlassian — ver a v1 no
`harness-agent-skills`) agora sobre os **tokens do design system Eleanor**
da Webmotors, com acessibilidade como pilar de primeira classe.

## O que mudou da v1 para a v2

| Dimensão | v1 | v2 (Eleanor) |
|---|---|---|
| Fonte | Manrope + Source Sans 3 + IBM Plex Mono | **Figtree** (display + corpo) + IBM Plex Mono (dado bruto) |
| Accent | genérico | **brand red `#d81f41`** (escuro: `#e53858`) |
| Paleta | inventada | **tokens Eleanor**: gray dark 50-950, indigo, semânticos |
| Acessibilidade | princípio citado | **checklist executável**: contraste AA validado, `:focus-visible`, `prefers-reduced-motion`, `aria-live` no resultado |
| Idioma | só pt-BR | **toggle EN/PT** (`data-i18n` + pares `data-i18n-pt/en`) |
| Quiz | 4 níveis fixos | **modo de revisão adaptativo**: erradas entram na revisão automaticamente |

## Tokens (resumo)

- **Papel > valor**: `--color-accent-text` em vez de `--color-red` (lição Atlassian).
- **3 variantes por status/tier**: sólido, `-soft`, `-text`; texto sempre no `-text` sobre o `-soft`.
- **Números**: `tabular-nums` sempre; delta com direção e base.
- **Elevação no escuro**: passo de superfície + hairline, nunca só sombra.
- **Um accent só**: semânticos (success/warning/danger/info) só em veredito real.

## Regras mecânicas (não reescrever)

- `system.css` vai inteiro no `<style>`; `skeleton.html` (scripts) copiado por inteiro.
- Os scripts têm literais `${...}` — nunca passar por template engine.
- O quiz: 4 `.quiz-level` × 3 opções × 1 `data-correct` + 1 `.quiz-why` rastreável.
- Adaptatividade e aria-live já estão nos scripts do skeleton — o gerador não os reimplementa.

## Validação da v2 (feita neste entregável)

- `scripts/build-demo.py` monta report + quiz mecanicamente (mesmo caminho da skill).
- Estrutura validada: 4 níveis, 12 opções, 4 corretas, 4 explicações, CSS injetado, i18n presente.