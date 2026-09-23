# ADK + RAG + Jev harness

The harness keeps the decision contract and retrieval boundary independent of
Google ADK and the Jev provider. It can run offline with fake providers, which
makes policy behavior testable before adding network clients.

The intended runtime flow is:

```text
request → decision provider → policy code → RAG adapter → evidence gate
```

The dependency-free Jev adapter targets TypeSafe's `/v1/systemone` contract and
accepts an injected transport for offline tests. `TypeSafeSdkDecisionProvider`
can use the official `typesafe-sdk` package when the optional
`[jev-sdk]` extra is installed. Provider errors fail closed in the workflow.
The `RagHarnessAdapter` loads the existing `rag-harness` controller by an
allowlisted collection and returns typed evidence without controlling
transitions. `AdkRuntimeAdapter` exposes this bounded workflow as a structured
Google ADK `LlmAgent` tool and `App` when the optional `[adk]` extra is installed.

The official TypeSafe SDK is published at
https://github.com/typesafe-ai/typesafe-sdk-python. This project depends on its
package rather than copying its source. Jev is an API service; no model weights
are downloaded.

## Run the ADK app

The `adk_app/agent.py` entrypoint runs in offline demo mode by default:

```bash
uv sync --extra adk --extra ollama --extra jev-sdk
uv run adk web
```

Open `http://localhost:8000`, select `adk_app`, and try a request such as
`find the deployment policy`. The app uses Ollama by default through
`http://localhost:11434` and the
`gemma3:latest` model. Set `OLLAMA_MODEL` to another locally installed model
when needed. `HARNESS_OFFLINE=0` and `TYPESAFE_API_KEY` enable Jev for routing.

```bash
OLLAMA_MODEL=mistral-small3.1 HARNESS_OFFLINE=0 uv run adk web
```

The Ollama server must be running and the selected model must support tool
calling. The ADK integration uses the `ollama_chat` LiteLLM provider.

## Test

```bash
python3 -m unittest discover -s tests -v  # 12 tests
```

Optional runtime dependencies:

```bash
uv sync --extra adk --extra ollama --extra jev-sdk
```
