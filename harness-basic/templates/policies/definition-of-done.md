# Definition of Done

> Aula 09. "Pronto" é um estado verificável, não uma palavra.

Uma feature está pronta quando:

1. **Build passa** — comando executado e saída anexada (exit 0).
2. **Testes passam, sem redução** — a suíte completa roda verde; nenhum teste
   foi deletado, renomeado, pulado ou enfraquecido em relação ao início.
3. **Diff no escopo** — `git diff` contém apenas o declarado em
   `policies/scope-control.md`.
4. **Evidência registrada** — comando + resultado esperado vs. real, anexados
   ao item/report da feature.
5. **Estado atualizado** — `feature_list.json` reflete o estado real (`passing`).

## O que NÃO é "pronto"
- "Parece que funciona" (sem build/testes executados).
- "Testei" (sem comandos e resultados).
- Suíte verde com menos testes que o início — isso é regressão, não passe.