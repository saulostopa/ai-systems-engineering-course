import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from adk_rag_harness.contracts import DecisionAnswer, DecisionProviderError, DecisionQuestion, DecisionResult, EvidenceChunk, RetrievalResponse
from adk_rag_harness.jev import JevDecisionProvider
from adk_rag_harness.workflow import AdkRagWorkflow, WorkflowStatus


class FakeDecisions:
    def __init__(self, answers):
        self.answers = answers
        self.calls = []

    def decide(self, state, questions):
        self.calls.append((state, [q.name for q in questions]))
        return DecisionResult({name: DecisionAnswer(value, confidence) for name, (value, confidence) in self.answers[len(self.calls) - 1].items()}, provider="fake")


class FakeRag:
    def __init__(self, answerable=True):
        self.answerable = answerable
        self.requests = []

    def retrieve(self, request):
        self.requests.append(request)
        chunks = (EvidenceChunk("docs/guide.md", "authoritative evidence", 0.91),) if self.answerable else ()
        return RetrievalResponse(request, chunks, self.answerable)


class WorkflowTests(unittest.TestCase):
    def test_direct_route_skips_rag(self):
        decisions = FakeDecisions([{"needs_retrieval": (False, 0.98)}])
        rag = FakeRag()
        result = AdkRagWorkflow(decisions, rag).run("write a greeting")
        self.assertEqual(result.status, WorkflowStatus.DIRECT)
        self.assertEqual(rag.requests, [])

    def test_low_confidence_falls_back_to_clarification(self):
        decisions = FakeDecisions([{"needs_retrieval": (True, 0.42)}])
        result = AdkRagWorkflow(decisions, FakeRag()).run("maybe search this")
        self.assertEqual(result.status, WorkflowStatus.CLARIFY)

    def test_retrieval_uses_typed_choices_and_evidence(self):
        decisions = FakeDecisions([
            {"needs_retrieval": (True, 0.96)},
            {"collection": ("docs", 0.94), "strategy": ("hybrid", 0.93)},
        ])
        rag = FakeRag()
        result = AdkRagWorkflow(decisions, rag).run("find the deployment policy")
        self.assertEqual(result.status, WorkflowStatus.RETRIEVED)
        self.assertEqual(rag.requests[0].collection, "docs")
        self.assertEqual(rag.requests[0].strategy, "hybrid")
        self.assertEqual(result.chunks[0].source, "docs/guide.md")

    def test_insufficient_evidence_blocks_answer(self):
        decisions = FakeDecisions([
            {"needs_retrieval": (True, 0.96)},
            {"collection": ("code", 0.94), "strategy": ("keyword", 0.93)},
        ])
        result = AdkRagWorkflow(decisions, FakeRag(answerable=False)).run("find a missing rule")
        self.assertEqual(result.status, WorkflowStatus.BLOCKED)

    def test_provider_failure_fails_closed(self):
        class BrokenProvider:
            def decide(self, state, questions):
                raise DecisionProviderError("offline")

        result = AdkRagWorkflow(BrokenProvider(), FakeRag()).run("search this")
        self.assertEqual(result.status, WorkflowStatus.BLOCKED)
        self.assertEqual(result.confidence, 0.0)


class JevAdapterTests(unittest.TestCase):
    def test_serializes_questions_and_normalizes_typed_answers(self):
        captured = {}

        def transport(payload):
            captured.update(payload)
            return {
                "model": "jev-1.13.0",
                "answers": {
                    "needs_retrieval": {"type": "noul", "noul": 0.92},
                    "collection": {"type": "choice", "choice": "docs", "confidence": 0.88, "probabilities": {"docs": 0.88, "code": 0.12}},
                    "urgency": {"type": "score", "score": 1.5, "confidence": 0.77, "legend": {"0": "low", "1": "medium", "2": "high"}, "probabilities": {"0": 0.1, "1": 0.3, "2": 0.6}},
                },
                "usage": {"input_tokens": 12, "output_tokens": 0},
            }

        provider = JevDecisionProvider(transport=transport)
        result = provider.decide(
            {"request": "find policy"},
            [
                DecisionQuestion("needs_retrieval", "Does it need evidence?", "noul"),
                DecisionQuestion("collection", "Which collection?", "choice", ("docs", "code")),
                DecisionQuestion("urgency", "How urgent?", "score", ("low", "medium", "high")),
            ],
        )
        self.assertEqual(captured["model"], "jev-latest")
        self.assertEqual(captured["questions"]["collection"]["criteria"], {"docs": "Select docs.", "code": "Select code."})
        self.assertEqual(result.answer("needs_retrieval").value, True)
        self.assertEqual(result.answer("collection").value, "docs")
        self.assertEqual(result.answer("urgency").value, 1.5)
        self.assertEqual(result.metadata["usage"]["input_tokens"], 12)

    def test_missing_choice_options_fails_before_transport(self):
        provider = JevDecisionProvider(transport=lambda payload: {})
        with self.assertRaises(DecisionProviderError):
            provider.decide({}, [DecisionQuestion("collection", "Which?", "choice")])


if __name__ == "__main__":
    unittest.main()
