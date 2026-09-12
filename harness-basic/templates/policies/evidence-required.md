# Evidência exigida

> Aula 09 e 11. Evidência é o que transforma "declarar vitória" em "provar a
> vitória". Nunca afirme "done" sem prova.

## O que conta como evidência

| Afirmação | Evidência mínima |
|---|---|
| "Está construído" | `build` executado, exit 0, saída anexada |
| "Está testado" | Nomes dos testes + contagem + saída verde |
| "Está no escopo" | `git diff` mostrando só o declarado |
| "Está integrado" | E2E/gates/hooks executados e passando |
| "Está publicado" | URL/artefato gerado e verificado |

## Formato da evidência

```
COMANDO: <comando executado>
ESPERADO: <o que deveria acontecer>
REAL: <o que aconteceu>
STATUS: PASSED | FAILED
```

## Regra de ouro
- Git é a verdade: re-execute e confira — nunca confie em narração.
- Uma suíte verde com menos testes que o início é regressão, não passe.