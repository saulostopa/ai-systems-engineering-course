"""Providers de LLM — OpenRouter (padrão), Ollama (opcional), Stub (offline).

Uso nos agentes:
    provider = make_provider()          # env: OPENROUTER_API_KEY | OLLAMA_API_URL
    text = provider.complete(prompt, system="...")
"""

from .providers import (
    LLMError,
    LLMProvider,
    OllamaProvider,
    OpenRouterProvider,
    StubProvider,
    Usage,
    make_provider,
)

__all__ = ["LLMError", "LLMProvider", "OllamaProvider", "OpenRouterProvider", "StubProvider", "Usage", "make_provider"]