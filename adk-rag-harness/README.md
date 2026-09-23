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
`llama3.1:8b` model. Set `OLLAMA_MODEL` to another locally installed model
when needed. `HARNESS_OFFLINE=0` and `TYPESAFE_API_KEY` enable Jev for routing.

```bash
OLLAMA_MODEL=mistral-small3.1 HARNESS_OFFLINE=0 uv run adk web
```

The Ollama server must be running and the selected model must support tool
calling. The ADK integration uses the `ollama_chat` LiteLLM provider.

## Golden prompt evaluations

The natural-language examples from the course are also stored as executable
contract fixtures in `evals/golden_prompts.json`. They test the workflow's
observable result instead of comparing model prose: route, RAG call count,
collection, strategy, evidence source and blocked/clarification behavior.

These evals use scripted decision and RAG providers, so they do not require
Ollama, Jev, Google ADK or network access. Provider-backed evals belong in a
separate integration job after the offline contract is stable.

To exercise the actual ADK, LiteLLM and Ollama path, run the opt-in integration
check while Ollama is serving `llama3.1:8b`:

```bash
HARNESS_OFFLINE=1 OLLAMA_MODEL=llama3.1:8b uv run python evals/run_ollama_evals.py
```

It fails if Ollama does not call `run_workflow`, if the tool result has the
wrong route, or if a retrieved result has no evidence. It is intentionally
separate from the default suite because it needs a running local model and can
take several seconds per prompt.

To test the live Jev decision provider independently from the conversational
model, export `TYPESAFE_API_KEY` in the shell and run:

```bash
TYPESAFE_API_KEY=your-key uv run python evals/run_jev_evals.py
```

The runner sends only the typed routing questions to Jev, keeps retrieval in the
workflow, and prints provider model, route, confidence and evidence count. It
never prints the API key or raw provider payloads.

## Test

```bash
python3 -m unittest discover -s tests -v  # 13 tests
```

Optional runtime dependencies:

```bash
uv sync --extra adk --extra ollama --extra jev-sdk
```
