# Graph-of-Thought Reasoning Engine

A deterministic structural core for LLM-centric cognitive systems.

LLM chain-of-thought is untestable: you cannot assert on hidden tokens, catch a contradiction before it spreads, or replay a reasoning step. Graph-of-Thought (GoT) represents thinking as an explicit graph you can inspect, validate, and debug like any other data structure.

Language models are used only to turn natural language into a structured graph. Validation, confidence propagation, and analysis are deterministic Python.

> Reasoning should be represented as a persistent, typed, and manipulable graph — not a transient stream of tokens.

**Persistence across processes is not implemented.** A `Graph` lives in memory for a library call or HTTP request. See [docs/architecture/overview.md](docs/architecture/overview.md).

## Documentation

| Doc | Purpose |
|-----|---------|
| [AGENTS.md](AGENTS.md) | Contract for AI coding agents |
| [docs/README.md](docs/README.md) | Documentation index |
| [docs/development/getting-started.md](docs/development/getting-started.md) | Install, run, test |
| [docs/roadmap.md](docs/roadmap.md) | Proposed evolution (RFC 0002; not code) |
| [got/domain/reasoning/README.md](got/domain/reasoning/README.md) | Structural reasoning engine |

## Overview

Nodes are units of thought (`fact`, `hypothesis`, `goal`, `constraint`, …). Edges are typed relations (support, contradiction, causality, structure, time). `Confidence` on nodes is epistemic belief in `[0.0, 1.0]`, not a statistical probability.

The engine then:

- validates structure and epistemic conflicts
- propagates confidence along epistemic (and optionally causal) edges
- detects contradiction clusters and connected components

```
LLMs → semantic interpretation (GraphSpecDTO)
Graph engine → deterministic reasoning
```

## Installation

This project uses [uv](https://docs.astral.sh/uv/). Python 3.11+ (`pyproject.toml`). CI uses 3.11.

```bash
uv venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync --dev
```

With pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run

HTTP API (requires `OPENROUTER_API_KEY`; the FastAPI app loads `.env`):

```bash
export OPENROUTER_API_KEY=your_key_here
uv run uvicorn got.api.app:app --reload
```

```bash
curl -X POST http://localhost:8000/analyze-text \
  -H "Content-Type: application/json" \
  -d '{"text": "We want to increase B2B revenue. SMB pricing is already at its ceiling."}'
```

The JSON body includes `graph` (`nodes`, `edges`, `metadata`) and `analysis` (`blocked_paths`, `viable_paths`, `recommendation`, `contradiction_count`). **`blocked_paths` and `viable_paths` are always `0` today**; `recommendation` is derived from those counts, so it does not yet reflect real path analysis.

In-process, without an LLM:

```bash
uv run python examples/simple_sandbox.py
```

Hub demo (static snapshots of the same engine, no LLM): [`spaces/hf-demo/`](spaces/hf-demo/). Gradio live hosting on the Hub requires a [PRO](https://huggingface.co/pro) plan; the free Space is HTML.

```bash
hf auth login
uv run --with huggingface_hub python spaces/hf-demo/publish.py
```

```bash
uv run pytest
uv run ruff check got examples
```

## Status

Implemented: domain graph, ops, validators, propagators, analyzers, FastAPI `POST /analyze-text`, OpenRouter structurer.

Not implemented: graph persistence, auth, agent runtime, `EnrichGraphService`, ports/infrastructure adapters (empty files). Cursor rules named `*-agent.mdc` are editor personas, not Python modules.

Proposed evolution (not current code): [docs/roadmap.md](docs/roadmap.md) — journal and replay first, then a deterministic Adaptive GoT loop, budget, rule-based transition reward, scoped `GraphRepo`, learned policy last. Details: [RFC 0002](docs/rfcs/0002-sequenced-runtime-roadmap.md).

## Contributing

Contributions are welcome: new validators/propagators/analyzers, synthetic-graph tests, examples.

The structural engine must stay deterministic, testable, explicit, and independent of LLM calls. Read [AGENTS.md](AGENTS.md) and [docs/development/conventions.md](docs/development/conventions.md) before large changes.
