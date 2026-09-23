"""Executable Google ADK app for local development.

Offline mode is the default so ``adk web`` never calls external providers by
accident. Set ``HARNESS_OFFLINE=0`` and ``TYPESAFE_API_KEY`` to use Jev.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from adk_rag_harness.adk_runtime import AdkRuntimeAdapter, AdkRuntimeConfig
from adk_rag_harness.contracts import DecisionAnswer, DecisionQuestion, DecisionResult, EvidenceChunk, RetrievalResponse
from adk_rag_harness.jev_sdk import TypeSafeSdkDecisionProvider
from adk_rag_harness.workflow import AdkRagWorkflow


class DemoDecisions:
    """Deterministic local provider used by the default offline app."""

    def decide(self, state, questions):
        request = str(state.get("request", "")).lower()
        if questions[0].name == "needs_retrieval":
            needs_retrieval = any(word in request for word in ("find", "search", "policy", "evidence", "document"))
            return DecisionResult({"needs_retrieval": DecisionAnswer(needs_retrieval, 0.98)}, provider="demo")
        return DecisionResult(
            {
                "collection": DecisionAnswer("docs", 0.98),
                "strategy": DecisionAnswer("hybrid", 0.98),
            },
            provider="demo",
        )


class DemoRag:
    """Small evidence source for exercising the ADK UI without a repository."""

    def retrieve(self, request):
        chunk = EvidenceChunk(
            source="demo/policy.md",
            text=f"Demo evidence for: {request.query}",
            score=1.0,
        )
        return RetrievalResponse(request, (chunk,), True, "demo evidence")


def _build_workflow() -> AdkRagWorkflow:
    offline = os.getenv("HARNESS_OFFLINE", "1") != "0"
    decisions = DemoDecisions() if offline else TypeSafeSdkDecisionProvider()
    return AdkRagWorkflow(decisions, DemoRag())


root_agent = AdkRuntimeAdapter(
    _build_workflow(),
    AdkRuntimeConfig(
        app_name="adk_rag_harness",
        agent_name="adk_rag_router",
        model=os.getenv("ADK_MODEL", "gemini-flash-latest"),
    ),
).build_agent()
