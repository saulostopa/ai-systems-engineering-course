# Design de Harnesses

Blueprints dos harnesses que este projeto entrega. Cada blueprint descreve a
arquitetura, os componentes e o que o torna funcional na prática.

- [Harness básico (download)](/pt-BR/harness-designs/basic-harness) — para projetos pequenos; baixa e roda.
- [Harness grande (multi-time)](/pt-BR/harness-designs/enterprise-harness) — gatekeepers, políticas e observabilidade para muitas equipes.
- [App Harness](/pt-BR/harness-designs/app-harness) — QA (E2E) + navegação agêntica com visão: build → abrir → validar.
- [RAG Harness & Area Copilots](/pt-BR/harness-designs/rag-harness) — contexto de código e de negócio (planilhas, imagens, docs).
- [Harness ADK + RAG + Jev](/pt-BR/harness-designs/adk-rag-jev-harness) — decisões tipadas, evidências e caminhos blocked no workflow.
- [Harness ADK RAG com PostgreSQL](/pt-BR/harness-designs/adk-rag-postgres-harness) — recuperação compartilhada com PostgreSQL + pgvector para times maiores.
- [Harnesses de domínio](/pt-BR/harness-designs/domain-harnesses) — o mesmo esqueleto, skill packs por área: games, finanças, comercial.
- [Hard Harness (orquestração executável)](/pt-BR/harness-designs/hard-harness) — grafo executável, contratos tipados, gates determinísticos e agentes especializados (ADK 2 como referência).

::: tip Status
Os blueprints cobrem as variantes local, compartilhada e de orquestração executável dos harnesses do curso.
:::

::: tip Baixe apenas os projetos executáveis
O catálogo standalone completo está em [github.com/saulostopa/harnesses](https://github.com/saulostopa/harnesses). Ele contém os diretórios executáveis dos harnesses e as instruções de instalação sem exigir o clone deste repositório do curso.
:::
