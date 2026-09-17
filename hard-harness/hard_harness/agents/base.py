"""Agentes especializados — raciocínio, nunca autoridade.

Contrato: run(NodeInput) -> NodeOutput.
  - Recebem visão do estado (NodeInput.state) — nunca a mutam.
  - Produzem PROPOSTAS (payload, artifacts, proposed_next, review, evidence).
  - NUNCA transicionam status.

Provider de LLM injetável (llm/providers.py): OpenRouter por padrão (env
OPENROUTER_API_KEY), Ollama opcional (OLLAMA_API_URL), Stub offline.
O custo (usage do provider) viaja no payload como `llm_cost` — o runner
aplica o orçamento (Limits.llm_budget).
"""

from __future__ import annotations

from typing import Any

from hard_harness.core.schemas import NodeInput, NodeOutput
from hard_harness.llm.providers import LLMProvider, StubProvider, make_provider


class BaseAgent:
    """Base comum: recebe provider injetado; expõe run(NodeInput)."""

    name = "agent"

    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider if provider is not None else make_provider()
        self.system = "Você é um especialista de harness engineering da Webmotors. Responda em português, direto e verificável."

    def _prompt(self, ninput: NodeInput, instructions: str) -> str:
        return f"{instructions}\n\nCONTEXTO:\n{ninput.payload}\n"

    def _cost_payload(self) -> dict[str, Any]:
        """Anexa o custo do provider (usage) ao payload — o runner decide o orçamento."""
        usage = getattr(self.provider, "last_usage", None)
        tokens = usage.total if usage else 0
        return {"llm_cost": float(tokens) / 1000.0 if tokens else 1.0, "llm_tokens": tokens}

    def run(self, ninput: NodeInput) -> NodeOutput:
        raise NotImplementedError


class PlannerAgent(BaseAgent):
    """Planeja o trabalho: proposta de plano, sem efeitos no mundo."""

    name = "planner"

    def run(self, ninput: NodeInput) -> NodeOutput:
        raw = self.provider.complete(
            self._prompt(ninput, "Proponha um plano de execução em passos curtos. Comece cada passo com '- '."),
            system=self.system,
        )
        steps = [line.lstrip("- ").strip() for line in raw.splitlines() if line.strip().startswith("-")]
        plan = {"plan_steps": steps[:8], "source": f"llm:{self.provider.name}"}
        plan.update(self._cost_payload())
        return NodeOutput(node_id=self.name, ok=True, payload=plan, proposed_next="validate_plan")


class CoderAgent(BaseAgent):
    """Gera ou altera código: produz um PATCH como artefato (proposta)."""

    name = "coder"

    def run(self, ninput: NodeInput) -> NodeOutput:
        raw = self.provider.complete(
            self._prompt(ninput, "Proponha o diff/patch da implementação em um bloco ```diff ... ```."),
            system=self.system,
        )
        patch_path = ninput.payload.get("patch_path", "/tmp/hard-harness-proposal.patch")
        try:
            with open(patch_path, "w", encoding="utf-8") as fh:
                fh.write(raw)
            artifacts = [{"path": patch_path, "kind": "patch"}]
        except OSError as exc:
            return NodeOutput(node_id=self.name, ok=False, error=f"não foi possível gravar patch: {exc}")
        payload = {"patch": raw[:2000], "patch_path": patch_path}
        payload.update(self._cost_payload())
        return NodeOutput(node_id=self.name, ok=True, payload=payload, artifacts=artifacts, proposed_next="fanout")


class ReviewerAgent(BaseAgent):
    """Raciocínio de revisão: produz ReviewResult como PROPOSTA."""

    name = "reviewer"

    def run(self, ninput: NodeInput) -> NodeOutput:
        raw = self.provider.complete(
            self._prompt(
                ninput,
                "Revise o trabalho. Responda na última linha com VERDICT: approved | changes_requested | rejected",
            ),
            system=self.system,
        )
        verdict = "changes_requested"
        lowered = raw.lower()
        for token in ("approved", "changes_requested", "rejected"):
            if f"verdict: {token}" in lowered:
                verdict = token
                break
        from hard_harness.core.schemas import ReviewResult

        review = ReviewResult(
            verdict=verdict,
            findings=[{"severity": "info", "location": "diff", "issue": raw.strip()[:200]}],
            summary=raw.strip()[:300],
        )
        payload = {"review": review.to_dict(), "reviewer": f"llm:{self.provider.name}"}
        payload.update(self._cost_payload())
        return NodeOutput(node_id=self.name, ok=True, payload=payload, review=review)


class EvidenceAgent(BaseAgent):
    """Síntese de evidências: consolida os resultados dos gates em relatório."""

    name = "evidence"

    def run(self, ninput: NodeInput) -> NodeOutput:
        joined = ninput.state.data.get("fanout_coder_agent", ninput.payload)
        passed = all(item.get("error") is None for item in joined.values())
        summary = {
            "fanout": {k: ("ok" if v.get("error") is None else v["error"]) for k, v in joined.items()},
            "passed": passed,
        }
        raw = self.provider.complete(
            self._prompt(ninput, "Escreva 3 linhas: o que foi entregue, o que foi verificado e o que ficou em aberto."),
            system=self.system,
        )
        summary["synthesis"] = raw.strip()[:600]
        summary.update(self._cost_payload())
        return NodeOutput(node_id=self.name, ok=True, payload=summary)