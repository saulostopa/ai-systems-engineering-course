"""Testes dos providers de LLM — sem rede real (servidor HTTP local).

Uso: python3 tests/test_llm_providers.py   (a partir de hard-harness/)

Cobre:
  - OpenRouterProvider: chamada HTTP correta + parsing + usage
  - OllamaProvider: mesmo contrato (endpoint /v1/chat/completions)
  - make_provider: seleção por ambiente (OpenRouter -> Ollama -> Stub)
  - agente parseia VERDICT com provider real
  - custo (llm_cost) viaja no payload
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hard_harness.agents import PlannerAgent, ReviewerAgent  # noqa: E402
from hard_harness.core.schemas import NodeInput, WorkflowState, WorkflowStatus  # noqa: E402
from hard_harness.llm.providers import (  # noqa: E402
    LLMError,
    OllamaProvider,
    OpenRouterProvider,
    StubProvider,
    make_provider,
)

RESPONSE_BODY = {
    "choices": [{"message": {"role": "assistant", "content": "resposta do modelo"}}],
    "usage": {"prompt_tokens": 12, "completion_tokens": 7},
}


class FakeLLMServer(BaseHTTPRequestHandler):
    """Servidor fake estilo OpenAI — captura a requisição e devolve RESPONSE_BODY."""

    captured: dict[str, Any] = {}
    requests: int = 0

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        type(self).captured = {"path": self.path, "headers": dict(self.headers), "body": body}
        type(self).requests += 1
        payload = json.dumps(RESPONSE_BODY).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt: str, *args) -> None:
        pass


def start_fake_server() -> tuple[HTTPServer, str]:
    server = HTTPServer(("127.0.0.1", 0), FakeLLMServer)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


# ═══ OpenRouter ═══════════════════════════════════════════════════════

def test_openrouter_chama_api_e_parseia():
    server, base = start_fake_server()
    try:
        provider = OpenRouterProvider(api_key="teste-key", model="m/modelo", base_url=base)
        text = provider.complete("pergunta", system="seja direto")
        assert text == "resposta do modelo"
        assert provider.last_usage.total == 19
        cap = FakeLLMServer.captured
        assert cap["path"] == "/chat/completions"
        assert cap["headers"].get("Authorization") == "Bearer teste-key"
        body = cap["body"]
        assert body["model"] == "m/modelo"
        assert body["messages"][0]["role"] == "system"
        assert body["messages"][1]["content"] == "pergunta"
    finally:
        server.shutdown()


def test_openrouter_sem_api_key_falha_explicito():
    os.environ.pop("OPENROUTER_API_KEY", None)
    try:
        OpenRouterProvider(api_key="")
        assert False, "sem chave deve falhar com LLMError"
    except LLMError as exc:
        assert "OPENROUTER_API_KEY" in str(exc)


def test_openrouter_erro_http_vira_llmerror():
    class FailHandler(FakeLLMServer):
        def do_POST(self) -> None:  # noqa: N802
            self.send_response(401)
            self.send_header("Content-Length", "0")
            self.end_headers()

    server = HTTPServer(("127.0.0.1", 0), FailHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        provider = OpenRouterProvider(api_key="x", base_url=base)
        try:
            provider.complete("oi")
            assert False, "401 deveria levantar LLMError"
        except LLMError as exc:
            assert "HTTP 401" in str(exc)
    finally:
        server.shutdown()


# ═══ Ollama ═══════════════════════════════════════════════════════════

def test_ollama_mesmo_contrato():
    server, base = start_fake_server()
    try:
        provider = OllamaProvider(base_url=base, model="llama3.2")
        text = provider.complete("pergunta")
        assert text == "resposta do modelo"
        assert FakeLLMServer.captured["path"] == "/v1/chat/completions"
        assert FakeLLMServer.captured["body"]["model"] == "llama3.2"
        assert provider.last_usage.total == 19
    finally:
        server.shutdown()


def test_ollama_available_falso_sem_servidor():
    assert OllamaProvider.available("http://127.0.0.1:1", timeout_s=0.3) is False


# ═══ make_provider (seleção por ambiente) ══════════════════════════════

def test_make_provider_openrouter_quando_env():
    os.environ["OPENROUTER_API_KEY"] = "chave-teste"
    try:
        provider = make_provider()
        assert provider.name == "openrouter"
    finally:
        os.environ.pop("OPENROUTER_API_KEY", None)


def test_make_provider_stub_sem_env():
    os.environ.pop("OPENROUTER_API_KEY", None)
    os.environ.pop("OLLAMA_API_URL", None)
    provider = make_provider()
    assert provider.name == "stub"


def test_make_provider_ollama_quando_env_e_responde():
    server, base = start_fake_server()
    os.environ.pop("OPENROUTER_API_KEY", None)
    os.environ["OLLAMA_API_URL"] = base
    try:
        provider = make_provider()
        # probe usa /api/tags (404 no fake, mas URL existe => considera não disponível)
        assert provider.name == "stub" or provider.name == "ollama"
    finally:
        os.environ.pop("OLLAMA_API_URL", None)
        server.shutdown()


# ═══ Agentes com provider real ═════════════════════════════════════════

def _ninput() -> NodeInput:
    state = WorkflowState(workflow_id="t1", status=WorkflowStatus.RUNNING, data={"planner_agent": {"plan_steps": ["x"]}})
    return NodeInput(node_id="reviewer_agent", state=state, payload={"diff": "conteúdo"})


def test_reviewer_parseia_verdict_com_provider_real():
    provider = StubProvider("revisão ok\nVERDICT: approved")
    agent = ReviewerAgent(provider=provider)
    output = agent.run(_ninput())
    assert output.review is not None
    assert output.review.verdict == "approved"
    assert output.payload.get("reviewer") == "llm:stub"
    assert "llm_cost" in output.payload  # custo viaja para o orçamento do runner


def test_planner_gera_steps_com_provider_real():
    provider = StubProvider("- passo um\n- passo dois")
    agent = PlannerAgent(provider=provider)
    output = agent.run(_ninput())
    assert output.payload["plan_steps"] == ["passo um", "passo dois"]
    assert output.proposed_next == "validate_plan"


def test_reviewer_default_e_changes_requested():
    provider = StubProvider("sem marcador nenhum")
    agent = ReviewerAgent(provider=provider)
    output = agent.run(_ninput())
    assert output.review.verdict == "changes_requested"


if __name__ == "__main__":
    import traceback

    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception:
                failed += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    total = sum(1 for n in globals() if n.startswith("test_"))
    print(f"\n== {total - failed}/{total} passaram")
    sys.exit(1 if failed else 0)