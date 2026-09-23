# ADK + RAG + Jev harness

The first slice keeps the decision contract and retrieval boundary independent
of Google ADK and the Jev provider. It can run offline with a fake decision
provider, which makes policy behavior testable before adding network clients.

The intended runtime flow is:

```text
request → decision provider → policy code → RAG adapter → evidence gate
```

Google ADK will own the production workflow graph and session runtime in a
following slice. The existing `rag-harness` remains an independent subsystem.

## Test

```bash
python3 -m unittest discover -s tests -v
```
