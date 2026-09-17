---
name: agentic-navigation
description: Navega no app como um usuário e valida a UI com visão — sobe o build, abre o app, percorre fluxos reais, tira screenshots e emite veredito por critério. Use quando o usuário pedir para validar/aceitar uma tela ou fluxo do app, verificar visualmente o resultado de uma feature, ou "abrir o app e testar". Requer um agente com capacidade de visão.
---

# Navegação agêntica com visão

Feche o loop de aceitação do app: o agente não pergunta "funciona?" — ele
sobe o app, navega, **vê** e emite veredito por critério, com screenshots
como evidência (Aula 09: prova, não opinião).

## Gather — antes de navegar

- A feature em questão: leia o diff e os testes E2E existentes (o que o QA já cobre).
- O app: como subir (`package.json` scripts — `dev`, `build`, `preview`), porta, credenciais de ambiente de teste (ou como criar dados de teste via interceptação).
- Os critérios de aceite da feature (do item/report — nunca invente).

## Navegar — o protocolo de 5 passos

1. **Sobe o app** — build (ou dev server) com o comando real; confirme a porta respondendo.
2. **Cria estado determinístico** — intercepte a API (`page.route` / mock) quando precisar de dados específicos; nunca dependa de dados aleatórios.
3. **Percorre o fluxo real** — do ponto de entrada até o fim, como um usuário: clique, preencha, submeta, volte. Navegue também os **estados de borda**: vazio, erro, loading, dados duplicados.
4. **Valida com visão** — em cada passo: layout (sobreposição, corte, overflow), contraste legível, loading infinito, mensagens de erro corretas, empty states aceitáveis. Tire **screenshots como evidência** de cada passo importante.
5. **Emite veredito por critério** — para cada critério de aceite: `ACEITO` ou `REJEITADO`, com o screenshot e a observação que justifica.

## Verdict — formato obrigatório

```markdown
## Veredito da navegação — <feature/screen>

| Critério | Veredito | Evidência |
|---|---|---|
| Fluxo completo funciona | ACEITO | <screenshot> |
| Sem quebra visual | REJEITADO — sobreposição no header | <screenshot> |
| Estado vazio aceitável | ACEITO | <screenshot> |
| Loading não infinito | ACEITO | <screenshot> |

### Achados
- **[REJEITADO] Sobreposição no header** — ao rolar com o teclado, o header
  cobre o conteúdo (screenshot). Causa provável: z-index do sticky header.
- Recomendação: vira teste E2E (camada QA) para imortalizar a regressão.
```

## Output

- Veredito por critério + screenshots salvos em `reports/navigation/YYYY-MM-DD-<slug>/` (com o nome do passo no arquivo).
- Cada **achado** vira recomendação de teste E2E novo — o loop fecha (o exploratório encontra, o determinístico imortaliza).
- Nenhum "parece que funciona": todo ACEITO tem screenshot; todo REJEITADO tem causa provável.

## Regras

- Nunca navegue com dados aleatórios: intercepte para determinismo.
- Não "corrija" o que achou — registre o achado (correção é outra feature).
- Se não conseguiu subir o app, pare e reporte o bloqueio — não invente veredito.