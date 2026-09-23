---
title: Backlog — modos de execução e revisão independente
---

# Backlog — modos de execução e revisão independente

Statuso: **backlog** · Prioridade: **P1** · Escopo: capacidade transversal dos harnesses

## Decisão

Adicionar ao curso um **Contrato de Execução e Revisão Independente**. A
capacidade vem do harness do Iris Target e impede que uma feature seja marcada
como `passing` apenas porque o comando de implementação terminou com sucesso.

O modo padrão continua sendo `checkpointed`. Uma feature pode optar por
`end_to_end_independent_review` quando o usuário quiser executar em sequência
os cortes técnicos já autorizados e revisar o resultado somente ao final.

O modo não amplia autoridade. Ele continua parando para ações externas,
mudanças destrutivas, credenciais ou dados ausentes, mudanças materiais de
escopo e decisões jurídicas ou comerciais.

## Contrato

```json
{
  "execution": { "mode": "checkpointed" },
  "completion": {
    "independent_review": {
      "required": true,
      "fresh_context": true,
      "reviewer_must_differ_from_implementer": true,
      "brief_path": "docs/reviews/<feature-id>/brief.md",
      "report_path": "docs/reviews/<feature-id>/report.json"
    }
  }
}
```

`execution.mode` controla o ritmo da entrega. `completion.independent_review`
controla as evidências exigidas antes de `passing`. Os dois campos devem ficar
separados para que uma feature possa ser executada por checkpoints e ainda
exigir revisão independente ao final.

## Matriz de adoção

| Harness | Política |
|---|---|
| Básico | Suportar os dois modos; checkpointed como padrão |
| App | Exigir revisão para mudanças de UI, autenticação, API ou E2E |
| RAG / Area Copilot | Exigir para retrieval, citações, permissões ou fronteiras de dados |
| Domínio | Exigir para compliance, finanças, monetização ou regras críticas |
| Hard | Tornar o gate padrão antes de `passing` |
| Enterprise | Exigir para mudanças entre repositórios e flows |
| ADK + RAG + Jev | Exigir para roteamento, limiares, fallback, evidências e runtime |

Pequenas mudanças apenas documentais podem continuar em `checkpointed` sem
revisão independente, salvo quando a feature optar explicitamente pelo modo.

## Protocolo de revisão

1. Registrar o modo e os caminhos reservados antes da implementação.
2. Definir escopo, critérios de aceite, invariantes e verificações proporcionais.
3. Fazer a primeira revisão em contexto novo e com identidade revisora diferente.
4. Registrar caminhos, comandos, resultados, achados e resoluções.
5. Fazer a revisão final em contexto novo e com uma nova instância revisora.
6. Permitir `passing` somente com `PASS` final e nenhum achado pendente.

O relatório deve vincular o estado revisado a um commit ou revisão. Declarar
`fresh_context` sozinho não é evidência suficiente; o harness deve registrar o
identificador da tarefa ou sessão revisora quando a capacidade for implementada.

## Integração com o Archify

O Archify mantém seu contrato determinístico atual:

- `validate` verifica schema, geometria e composição;
- `deliver` cria o artefato confiável e registra hashes da especificação e do artefato;
- `visual-check` registra evidência automatizada do navegador;
- revisão visual perceptual continua sendo uma afirmação separada.

Adicionar um contrato de revisão opcional ao Archify, sem exigir revisão de
agente para todo diagrama. O receipt de revisão deve validar:

- `specification_sha256` e `artifact_sha256` correspondentes;
- revisão analisada e identidade da pessoa ou agente revisor;
- views, temas e viewports inspecionados;
- achados com severidade, status e resolução;
- `PASS` final para entregas que exigirem revisão.

A forma prevista é um passo separado de validação ou uma flag explícita
`--require-review` na entrega final. A evidência automatizada do navegador nunca
deve ser apresentada como revisão perceptual.

## Sequência de implementação

1. Adicionar schema e validador independente de provedor ao `harness-basic`.
2. Adicionar evidência de revisão aos gates de conclusão do Hard e Enterprise.
3. Integrar o contrato ao ADK + RAG + Jev para mudanças de roteamento e evidências.
4. Adicionar ao Archify o receipt opcional vinculado por hashes.
5. Criar testes adversariais para reutilização do mesmo revisor, revisão obsoleta,
   evidência ausente, achados não corrigidos e caminhos inválidos.

## Critérios de aceite

- Features existentes continuam válidas sem um objeto `execution`.
- `passing` não pode ignorar uma revisão independente explicitamente exigida.
- Revisores, contextos, revisões, caminhos e comandos ficam registrados.
- Todos os caminhos revisados permanecem dentro do repositório.
- Reports antigos não validam artefato ou commit mais novo.
- O receipt do Archify mantém separadas validação determinística, evidência do
  navegador e revisão perceptual.

## Origem da decisão

A feature se baseia nos modos de execução e no validador de revisão independente
implementados no harness do Iris Target: [PR #1](https://github.com/saulostopa/iristarget/pull/1).
