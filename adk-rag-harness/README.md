# ADK + RAG + Jev harness

The first slice keeps the decision contract and retrieval boundary independent
of Google ADK and the Jev provider. It can run offline with a fake decision
provider, which makes policy behavior testable before adding network clients.

The intended runtime flow is:

```text
request → decision provider → policy code → RAG adapter → evidence gate
```

The dependency-free Jev adapter now targets TypeSafe's `/v1/systemone` contract
and accepts an injected transport for offline tests. Provider errors fail closed
in the workflow. The `RagHarnessAdapter` loads the existing `rag-harness`
controller by an allowlisted collection and returns typed evidence without
controlling transitions. Google ADK will own the production workflow graph and
session runtime in a following slice.

## Test

```bash
python3 -m unittest discover -s tests -v  # 7 tests
```
