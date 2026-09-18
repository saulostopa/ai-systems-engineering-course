"""Hard Harness — framework-agnostic executable orchestration.

Modules:
  core/     graph, runner, schemas, gates, events (the core)
  stores/   persistence (FileStateStore; AgEnFKStore adapter)
  adapters/ adk2 (optional inspiration), rag (context provider)
  agents/   specialists: planner, coder, reviewer, evidence
  llm/      providers: OpenRouter (default), Ollama (optional), Stub (offline)
"""