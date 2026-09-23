---
title: Lesson 18 — Running the ADK harness with Ollama
---

# Lesson 18 — Running the ADK harness with Ollama

> A practical lab for `adk-rag-harness`: run the ADK Dev UI against a local
> Ollama model, use natural-language requests, and inspect the evidence that
> proves the workflow ran.

## What this lab teaches

The Dev UI is a client for the harness. It is useful for sending requests,
starting sessions and inspecting events. It does not replace the deterministic
workflow. The model proposes when to call a tool; `run_workflow` still applies
the typed decision, retrieval policy and fallback rules in code.

The local default has two routing paths exercised by the course prompts:

- direct requests, which answer without retrieval;
- retrieved requests, which return local demo evidence and a source reference.

The conversation model defaults to `llama3.1:8b`. Typed routing decisions use
`qwen2.5:14b` through `ollama-system-one`, because it was more consistent than
`llama3.1:8b` on the routing evals. `demo` remains available as an explicit
deterministic provider.

The real Jev provider is enabled separately with `HARNESS_OFFLINE=0` and a
`TYPESAFE_API_KEY`. That separation makes local UI experiments safe and
repeatable.

## Prerequisites

- Python 3.10 or newer;
- [`uv`](https://docs.astral.sh/uv/);
- [Ollama](https://ollama.com/) running locally;
- the `adk-rag-harness/` directory checked out.

Check that the model is installed:

```sh
ollama list
```

If it is missing, install it once:

```sh
ollama pull llama3.1:8b
```

Ollama Desktop may already be serving the API. If it is not, start the local
server in another terminal:

```sh
ollama serve
```

The default API is `http://localhost:11434`. A quick health check is:

```sh
curl -fsS http://127.0.0.1:11434/api/tags
```

## Install and start the harness

Use `uv` for both installation and execution. This keeps the `adk` command in
the project environment, so a global `pip` or `adk` installation is not needed.

```sh
cd adk-rag-harness
uv sync --extra adk --extra ollama --extra jev-sdk
OLLAMA_MODEL=llama3.1:8b uv run adk web
```

Open [http://127.0.0.1:8000/dev-ui/?app=adk_app](http://127.0.0.1:8000/dev-ui/?app=adk_app)
and select `adk_app`. Keep the terminal running while using the UI. Restart
`adk web` after changing Python code or environment variables.

The ADK integration uses LiteLLM's `ollama_chat` provider. The model must be
able to call tools; `llama3.1:8b` is the course default because it completed the
tool-call path in this lab. A model answering text without calling
`run_workflow` has not exercised the harness.

## Natural-language prompts for the demonstration

Paste one prompt at a time into the message box. No special command syntax is
required.

| Prompt | What it demonstrates | Expected route |
|---|---|---|
| `Write a short greeting for a course participant.` | A request that does not need repository evidence | Direct |
| `Find the deployment policy in the course documentation and summarize the evidence.` | A request that needs retrieval and a source reference | Retrieved |
| `Search the repository for the rule that controls whether a request needs external evidence.` | Retrieval-oriented language rather than a function name | Retrieved |
| `I need an answer about the project architecture. Which collection should be searched and why?` | Asking for a retrieval policy in natural language | Retrieved |
| `Answer only when the repository evidence is sufficient; otherwise explain what is missing.` | The desired contract for a guarded answer | Guarded answer |

The first two prompts are the reliable smoke test for the current demo. The
The last prompt describes the low-confidence contract; its complete behavior is
covered by the decision-policy tests and becomes meaningful when the real Jev
and RAG providers are enabled.

The same prompts are stored in `adk-rag-harness/evals/golden_prompts.json`.
Run the offline contract evals with:

```sh
python3 -m unittest discover -s tests -v
```

The evals compare route, RAG call count, collection, strategy, evidence source
and blocked/clarification behavior. They do not compare generated prose, so a
small wording change does not create a false failure.

### Switching the decision provider

The chat model and the typed routing provider are separate. The app reads
`HARNESS_DECISION_PROVIDER` from `adk_app/agent.py`:

```sh
# Default: local Ollama typed decisions
uv run adk web

# Deterministic demo provider
HARNESS_DECISION_PROVIDER=demo uv run adk web

# Local typed decisions with Ollama
HARNESS_DECISION_PROVIDER=ollama-system-one \
OLLAMA_DECISION_MODEL=qwen2.5:14b uv run adk web

# OpenRouter for hosted decisions
HARNESS_DECISION_PROVIDER=openrouter-system-one \
OPENROUTER_DECISION_MODEL=deepseek/deepseek-v4-flash-0731 \
uv run adk web
```

The two OpenAI-compatible modes preserve the typed contract but are not the
Jev model. Evaluate their confidence values before using them as a production
policy boundary. The installed `codex`, `claude` and `agy` CLIs can be wrapped
later with read-only subprocess adapters and strict JSON Schema output; their
interactive tools and session state should not run inside this decision path.

If `OPENROUTER_API_KEY` is not set, the app can read the local
`openrouter.key` from `~/.local/share/opencode/auth.json` without copying the
credential into the project.

### Switching from demo evidence to the real RAG index

The retrieval provider is independent from the decision provider. Build the
course-document index once:

```sh
ollama pull nomic-embed-text
RAG_EMBEDDER=ollama OLLAMA_EMBED_MODEL=nomic-embed-text \
PYTHONPATH=rag-harness python3 -m rag_harness index docs --verbose
```

Then start the app with:

```sh
HARNESS_RAG_PROVIDER=rag-harness uv run adk web
```

The index is local and ignored by Git. A missing index or retrieval failure
produces `blocked`, so the assistant cannot present invented evidence.
The `nomic-embed-text` model supplies semantic embeddings through the local
Ollama API. For a fully offline architecture check, use
`RAG_EMBEDDER=ngram`; recreate the index when changing embedding providers.

Combine it with OpenRouter decisions when testing the complete path:

```sh
HARNESS_DECISION_PROVIDER=openrouter-system-one \
HARNESS_RAG_PROVIDER=rag-harness \
uv run adk web
```

After the offline contract passes, exercise the real model path with Ollama:

```sh
HARNESS_OFFLINE=1 OLLAMA_MODEL=llama3.1:8b uv run python evals/run_ollama_evals.py
```

This opt-in check fails if the model does not call `run_workflow`, returns the
wrong route, or produces a retrieval result without evidence.

The next integration boundary is Jev. Set the key only in your shell and run:

```sh
TYPESAFE_API_KEY=your-key uv run python evals/run_jev_evals.py
```

This check evaluates Jev's typed routing decisions separately from Ollama and
prints only the provider model, route, confidence and evidence count.

## How to read the Dev UI

### Events

The Events view shows the user message, the model's tool call, the
`run_workflow` result and the final response. A successful retrieval example
looks like:

```text
user request
  → run_workflow("find the deployment policy")
  → evidence, route and confidence
  → final answer with the source reference
```

![ADK Dev UI events showing the retrieval workflow](/images/adk-rag-ollama-events.png)

### Traces

The Traces view proves which provider was used and where time was spent. For
this setup, look for `generate_content ollama...`, `run_workflow`, latency and
token counts. The expected shape is:

```text
adk_rag_router
├── call_llm → generate_content ollama...
├── run_workflow
└── call_llm → generate_content ollama...
```

![ADK Dev UI traces showing Ollama calls and workflow execution](/images/adk-rag-ollama-traces.png)

![ADK Dev UI first successful local run](/images/adk-rag-ollama-first-run.png)

### State, Artifacts and Evals

- **State** shows the session state passed between steps.
- **Artifacts** is where a future implementation can expose generated files
  or evidence bundles.
- **Evals** is the place to add golden requests and compare routing, evidence
  and answer quality. A green chat response alone is not an evaluation.

## Troubleshooting

| Symptom | Check |
|---|---|
| `command not found: adk` | Run `uv run adk web` from `adk-rag-harness`. |
| The model is not called | Confirm Ollama is reachable and use a tool-capable model. |
| `ollama ps` is empty after the answer | The model may have been unloaded; inspect it during an active request or run `ollama list`. |
| The UI opens but the app is missing | Start the server from the repository root with the app directory available, then refresh. |
| The route is always a demo route | Check that `HARNESS_DECISION_PROVIDER` is not set to `demo`. |
| The trace does not show Ollama | Confirm `OLLAMA_MODEL` and `OLLAMA_API_BASE`, then restart `adk web`. |

## Evidence checklist

Before considering the lab complete, capture:

1. the model present in `ollama list`;
2. an Events view with a tool call and final answer;
3. a Traces view containing `generate_content ollama` and `run_workflow`;
4. the exact natural-language prompt used;
5. the route, confidence and source reference returned by the workflow.

## Check your learning

```text
"quiz me on Lesson 18"
```

**Back to theory**: [16 — ADK 2](/lectures/lecture-16) · [17 — Building a Hard Harness](/lectures/lecture-17)

**Project lab**: [Project 06 — ADK + RAG + Jev harness](/projects/project-06)

**Official references**: [ADK Ollama integration](https://adk.dev/agents/models/ollama/) · [ADK web interface](https://adk.dev/runtime/web-interface/)
