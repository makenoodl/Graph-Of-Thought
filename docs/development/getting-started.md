# Getting started

Python **3.11+** (`requires-python` in `pyproject.toml`). Local `.python-version` is `3.13`. CI uses **3.11**.

Package manager: [uv](https://docs.astral.sh/uv/) (lockfile `uv.lock`). `pip install -e .` is documented as a fallback.

## Install

```bash
uv venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv sync --dev
```

`--dev` matches CI (`uv sync --dev`) and installs pytest and Ruff. Plain `uv sync` is enough to import the library and run uvicorn.

## Environment

The HTTP text pipeline needs an OpenRouter key. The FastAPI app loads `.env` from the process working directory.

```bash
export OPENROUTER_API_KEY=your_key_here
```

Do not commit `.env`. See [../operations/configuration.md](../operations/configuration.md).

In-process graph construction (`examples/simple_sandbox.py`, unit tests) does **not** need the key.

## Run the API

```bash
uv run uvicorn got.api.app:app --reload
```

Entry object: `app` from `got.api.app`. Then:

```bash
curl -X POST http://localhost:8000/analyze-text \
  -H "Content-Type: application/json" \
  -d '{"text": "We want to increase B2B revenue. SMB pricing is already at its ceiling."}'
```

Response shape: `{ "graph": { "nodes", "edges", "metadata" }, "analysis": { "blocked_paths", "viable_paths", "recommendation", "contradiction_count" } }`. Path counts are currently always `0`. Interactive docs: `http://localhost:8000/docs`.

## Run the sandbox (no LLM)

```bash
uv run python examples/simple_sandbox.py
```

## Tests and lint

```bash
uv run pytest
uv run ruff check got examples
```

CI is intended to run the same checks; the workflow file still uses `uv run ruff got examples`, which current Ruff rejects. Details: [testing.md](testing.md).

## Where to read next

- [../architecture/overview.md](../architecture/overview.md)
- [conventions.md](conventions.md)
- [../../AGENTS.md](../../AGENTS.md) if you are an AI agent
