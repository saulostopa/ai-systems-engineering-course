"""Agentes especializados — raciocínio, nunca autoridade.

Contrato: run(NodeInput) -> NodeOutput.
  - Recebem visão IMUTÁVEL do estado (NodeInput.state).
  - Produzem PROPOSTAS (payload, artifacts, proposed_next, review, evidence).
  - NUNCA transicionam status: tentativa = chamada a API inexistente.

Em produção, um LLMProvider injetado responde; nos testes, stubs
determinísticos cumprem o contrato (ADK 2: função e agente são peers).
"""

from __future__ import annotations

from typing import Any, Callable, Protocol

from hard_harness.core.schemas import NodeInput, NodeOutput

LLMProvider = Callable[[str], str]


class LLMProviderProtocol(Protocol):
    def complete(self, prompt: str) -> str: ...


class _StubLLM:
    """LLM stub determinístico — só para testes/exemplos offline."""

    def complete(self, prompt: str) -> str:
        return "stub response"


class BaseAgent:
    """Base comum: recebe provider injetado; expõe run(NodeInput)."""

    name: str = "agent"

    def __init__(self, provider: LLMProviderProtocol | None = None) -> None:
        self.provider = provider or _StubLLM()

    def _prompt(self, ninput: NodeInput, instructions: str) -> str:
        scope = ninput.payload
        return f"{instructions}\n\nCONTEXTO:\n{scope}\n"

    def run(self, ninput: NodeInput) -> NodeOutput:
        raise NotImplementedError


class PlannerAgent(BaseAgent):
    """Planeja o trabalho: proposta de plano, sem efeitos no mundo."""

    name = "planner"

    def run(self, ninput: NodeInput) -> NodeOutput:
        raw = self.provider.complete(self._prompt(ninput, "Proponha um plano de execução em passos."))
        plan = {"plan_steps": raw.strip().splitlines()[:8], "source": self.name}
        # O próximo passo (ex.: coder) é proposta — o runner decide após gates.
        return NodeOutput(node_id=self.name, ok=True, payload=plan, proposed_next="validate_plan")


class CoderAgent(BaseAgent):
    """Gera ou altera código: produz um PATCH como artefato (proposta)."""

    name = "coder"

    def run(self, ninput: NodeInput) -> NodeOutput:
        raw = self.provider.complete(self._prompt(ninput, "Proponha o diff/patch da implementação."))
        patch_path = ninput.payload.get("patch_path", "/tmp/hard-harness-proposal.patch")
        try:
            with open(patch_path, "w", encoding="utf-8") as fh:
                fh.write(raw)
            artifacts = [{"path": patch_path, "kind": "patch"}]
        except OSError as exc:
            return NodeOutput(node_id=self.name, ok=False, error=f"não foi possível gravar patch: {exc}")
        return NodeOutput(node_id=self.name, ok=True, payload={"patch": raw[:2000]}, artifacts=artifacts, proposed_next="fanout")


class ReviewerAgent(BaseAgent):
    """Raciocínio de revisão: produz ReviewResult como PROPOSTA."""

    name = "reviewer"

    def run(self, ninput: NodeInput) -> NodeOutput:
        raw = self.provider.complete(self._prompt(ninput, "Revise o diff. Verdict: approved | changes_requested | rejected."))
        verdict = "approved" if "approved" in raw.lower() else "changes_requested"
        from hard_harness.core.schemas import ReviewResult

        review = ReviewResult(
            verdict=verdict,
            findings=[{"severity": "info", "location": "diff", "issue": raw.strip()[:200]}],
            summary=raw.strip()[:300],
        )
        return NodeOutput(node_id=self.name, ok=True, payload={"review": review.to_dict()}, review=review)


class EvidenceAgent(BaseAgent):
    """Síntese de evidências: consolida os resultados dos gates em relatório."""

    name = "evidence"

    def run(self, ninput: NodeInput) -> NodeOutput:
        joined = ninput.payload  # payload do join com build/testes/e2e/lint
        passed = all(item.get("error") is None for item in joined.values())
        summary = {
            "fanout": {k: ("ok" if v.get("error") is None else v["error"]) for k, v in joined.items()},
            "passed": passed,
        }
        return NodeOutput(node_id=self.name, ok=True, payload=summary)