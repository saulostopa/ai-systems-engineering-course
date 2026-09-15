"""Hard Harness — orquestração executável framework-agnóstica.

Módulos:
  core/     grafo, runner, schemas, gates, events (o núcleo)
  stores/   persistência (FileStateStore; AgEnFKStore adapter)
  adapters/ adk2 (inspiração opcional), rag (provedor de contexto)
  agents/   especialistas: planner, coder, reviewer, evidence
"""