import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from adk_rag_harness.contracts import DecisionAnswer, DecisionResult, EvidenceChunk, RetrievalResponse
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


if __name__ == "__main__":
    unittest.main()
