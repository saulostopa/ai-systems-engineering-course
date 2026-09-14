---
name: proposal-workflow
description: Valida uma proposta/deck contra o briefing antes do envio — checklist de requisitos, revisão cruzada e registro de aprovação. Use quando o usuário pedir para revisar, validar, aprovar ou enviar uma proposta/apresentação.
---

# Validação de proposta antes do envio

Enviar antes de validar é o "commit sem gate" do comercial (Aula 07/10).
A proposta só sai com o checklist passando.

## Gather

- A proposta (materiais/) e o briefing de origem.
- O script de verificação: `scripts/proposal-check.sh <proposta> <briefing>`.

## Write / Validate — checklist

1. **Requisitos do briefing** — cada requisito do briefing tem resposta na proposta (scripts/proposal-check.sh compara item a item).
2. **Números com fonte** — todo número do deck tem `FONTE:` citada; nenhum número solto.
3. **Revisão cruzada** — a proposta foi lida por um revisor diferente de quem gerou (outro agente/pessoa); o revisor registra o veredito.
4. **Registro de aprovação** — aprovado/rejeitado fica registrado na feature (comentário/estado), nunca só na conversa.

## Output

- `relatorios/YYYY-MM-DD-<slug>-aprovacao.md`: checklist com STATUS por item + veredito do revisor.
- Qualquer FAIL bloqueia o envio (log-event.sh registra a fricção).