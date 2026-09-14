# Definition of Done — domínio Games

Uma feature de jogo está pronta quando:

1. **Design doc existe** — `design-docs/YYYY-MM-DD-<slug>.md` com persona, storytelling, mecânica, economia (se houver) e critérios de verificação.
2. **Playteste simulado passou** — `scripts/playtest-simulate.sh <doc>` termina com `PLAYTESTE ACEITO` (0 falhas).
3. **Build valida** — Rojo/Luau compila (exit 0), assets íntegros.
4. **Publicação validada** (quando aplicável) — checklist da skill `roblox-publish` 100% PASS com evidência.
5. **Evidência registrada** — comandos + saídas anexadas; feature em `passing`.

## O que NÃO é "pronto" no domínio
- Design doc sem persona ou sem critérios de aceite.
- Feature publicada sem playteste simulado.
- "Achei que a plataforma aceita" — sem o checklist executado.