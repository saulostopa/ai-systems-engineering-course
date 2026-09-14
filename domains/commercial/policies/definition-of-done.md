# Definition of Done — domínio Comercial

Uma entrega comercial (deck/proposta/material) está pronta quando:

1. **Briefing atendido** — `scripts/proposal-check.sh <material> <briefing>` termina com `PROPOSTA APROVADA PARA ENVIO` (0 falhas): todos os `- [REQ]` do briefing respondidos.
2. **Números com fonte** — todo número citado com `FONTE:` (bloco); nenhum número solto.
3. **Revisão cruzada** — revisor diferente do gerador registrou veredito.
4. **Aprovação registrada** — aprovado/rejeitado na feature (estado/comentário), não só na conversa.
5. **Artefato versionado** — `materiais/YYYY-MM-DD-<slug>.md` no playbook; feature em `passing`.

## O que NÃO é "pronto" no domínio
- Deck com número sem fonte (o slide não existe sem a fonte).
- "O cliente gostou" sem registro de aprovação.
- Requisito do briefing sem resposta ("dá pra cortar isso").