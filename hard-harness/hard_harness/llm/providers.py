"""Providers de LLM — OpenRouter (padrão), Ollama (opcional), Stub (offline).

Os agentes do hard-harness recebem um provider injetável
(`complete(prompt) -> str`). Aqui moram as implementações reais:

  - OpenRouterProvider: API compatível com OpenAI (urllib da stdlib).
  - OllamaProvider:    endpoint local /v1/chat/completions.
  - StubProvider:      determinístico, para testes/exemplos offline.
  - make_provider():   seleção por ambiente, SEM surpresa de rede:
        1. OPENROUTER_API_KEY definida  -> OpenRouter
        2. OLLAMA_API_URL definida      -> Ollama (probe curto)
        3. senão                        -> Stub (com aviso claro)

Custo: providers expõem `last_usage` (tokens); os agentes anexam
`llm_cost` ao payload; o runner aplica `llm_budget`.
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass, field
from typing import Any

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "deepseek/deepseek-v4-flash-0731"
OLLAMA_BASE = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"


@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class LLMError(RuntimeError):
    pass


class LLMProvider:
    """Contrato mínimo: complete(prompt) -> str."""

    name = "base"

    def complete(self, prompt: str, system: str | None = None) -> str:
        raise NotImplementedError

    @property
    def last_usage(self) -> Usage:
        return Usage()


def _http_post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout_s: float) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={**headers, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", errors="replace")[:400]
        except Exception:
            pass
        raise LLMError(f"HTTP {exc.code} do provider: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise LLMError(f"sem conexão com o provider: {exc}") from exc


class OpenRouterProvider(LLMProvider):
    """Provider via OpenRouter — mesmo estilo usado pelo opencode desta sessão."""

    name = "openrouter"

    def __init__(self, api_key: str | None = None, model: str = OPENROUTER_MODEL, base_url: str = OPENROUTER_BASE,
                 max_tokens: int = 2048, temperature: float = 0.2, timeout_s: float = 120.0) -> None:
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise LLMError("OPENROUTER_API_KEY não definida (env ou argumento)")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout_s = timeout_s
        self._usage = Usage()

    @property
    def last_usage(self) -> Usage:
        return self._usage

    def complete(self, prompt: str, system: str | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        data = _http_post_json(
            f"{self.base_url}/chat/completions",
            {"model": self.model, "messages": messages, "max_tokens": self.max_tokens, "temperature": self.temperature},
            {"Authorization": f"Bearer {self.api_key}"},
            self.timeout_s,
        )
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"resposta inesperada do OpenRouter: {str(data)[:300]}") from exc
        usage = data.get("usage") or {}
        self._usage = Usage(int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0)))
        return text or ""


class OllamaProvider(LLMProvider):
    """Provider local via Ollama (endpoint compatível com OpenAI)."""

    name = "ollama"

    def __init__(self, base_url: str = OLLAMA_BASE, model: str = OLLAMA_MODEL,
                 max_tokens: int = 2048, timeout_s: float = 300.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_tokens = max_tokens
        self.timeout_s = timeout_s
        self._usage = Usage()

    @property
    def last_usage(self) -> Usage:
        return self._usage

    def complete(self, prompt: str, system: str | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        data = _http_post_json(
            f"{self.base_url}/v1/chat/completions",
            {"model": self.model, "messages": messages, "max_tokens": self.max_tokens, "stream": False},
            {},
            self.timeout_s,
        )
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"resposta inesperada do Ollama: {str(data)[:300]}") from exc
        usage = data.get("usage") or {}
        self._usage = Usage(int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0)))
        return text or ""

    @classmethod
    def available(cls, base_url: str = OLLAMA_BASE, timeout_s: float = 1.5) -> bool:
        try:
            with urllib.request.urlopen(f"{base_url.rstrip('/')}/api/tags", timeout=timeout_s) as res:
                return res.status == 200
        except Exception:
            return False


class StubProvider(LLMProvider):
    """Determinístico — para testes/exemplos sem rede. Avisa que é stub."""

    name = "stub"

    def __init__(self, response: str = "stub response") -> None:
        self.response = response
        self.calls: list[str] = []

    def complete(self, prompt: str, system: str | None = None) -> str:
        self.calls.append(prompt[:200])
        return self.response


def make_provider(prefer_ollama: bool = False) -> LLMProvider:
    """Seleção por ambiente — sem surpresa de rede (Aula do curso: decidir por evidência).

    1. OPENROUTER_API_KEY definida -> OpenRouter (padrão desta sessão).
    2. OLLAMA_API_URL definida (ou prefer_ollama) e Ollama responde -> Ollama.
    3. senão -> Stub com aviso claro.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    ollama_url = os.environ.get("OLLAMA_API_URL", "")
    if api_key:
        try:
            return OpenRouterProvider(api_key=api_key)
        except LLMError as exc:
            print(f"[llm] aviso: OpenRouter configurado mas falhou ao instanciar: {exc}")
    if ollama_url or prefer_ollama:
        base = ollama_url or OLLAMA_BASE
        if OllamaProvider.available(base):
            return OllamaProvider(base_url=base)
        print(f"[llm] aviso: Ollama ({base}) não respondeu — usando stub")
    if not api_key and not ollama_url and not prefer_ollama:
        print("[llm] aviso: nenhum provider configurado (OPENROUTER_API_KEY ou OLLAMA_API_URL) — usando stub determinístico")
    return StubProvider()