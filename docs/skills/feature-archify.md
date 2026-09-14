---
title: feature-archify
---

# feature-archify — diagramas pós-conclusão

Skill wrapper que integra o **Archify** ([tt-a1i/archify](https://github.com/tt-a1i/archify), MIT, 62k stars) ao fluxo de artefatos do curso: quando um trabalho é concluído, além do `feature-report` e do `feature-quiz`, o harness gera o **diagrama verificável** que ensina como o que foi construído funciona.

## Entregue

| Peça | O que é |
|---|---|
| `skills-artifacts/feature-archify/SKILL.md` | Skill wrapper no padrão do curso (Gather/Write/Output) — escolha do tipo, contrato de qualidade e ciclo validate→deliver |
| `.agents/skills/archify/` | A skill Archify completa (v2.17, MIT) — pacote funcional: schemas, renderers, binário Node |
| `pilots/archify-demo/harness-basic-pipeline.json` | Fonte reproduzível do diagrama demo |
| `pilots/archify-demo/harness-basic-pipeline.html` | **Diagrama entregue**: 9/9 artifact checks, composition showcase **PASS** — o pipeline do harness básico com gates |

## O diagrama demo (abrir no navegador)

`pilots/archify-demo/harness-basic-pipeline.html` — workflow do harness básico:
pessoa/agente → init → feature_list → implementação → **gatekeeper** (com o
retorno "sem feature — declare") → build/testes → validate-harness →
commit+push. Com 2 views (`#view=happy-path` e `#view=gates`) e 3 cards,
incluindo o que o leitor deve aprender e o achado do piloto G1.

## Por que é "verificável"

O Archify não renderiza por opinião: o JSON tipado passa por **validators
atômicos** (schema, layout, rotas, clearance) e só um artefato que passa
`composition: showcase` é entregue — cada falha vem com diagnóstico e a
correção suportada. Nesta integração, o validator pegou erros reais de
topologia e roteamento em 8 iterações até o pass — exatamente a disciplina
que o curso ensina (evidência antes de "done", aplicada ao próprio diagrama).

## Instalar em outro projeto

```sh
npx skills add tt-a1i/archify -g          # ou --agent opencode --copy
```

## Uso

```
"gera o diagrama do fluxo dessa feature que acabamos de entregar"
```

**Relacionado**: [feature-report](/skills/feature-report) · [feature-quiz](/skills/feature-quiz) · [Criar uma skill nova](/skills/how-to-create)