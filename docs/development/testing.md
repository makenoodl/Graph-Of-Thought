# Testing

## Tooling

- Runner: pytest (`got/tests/`, `pytest>=8` via uv dev extras).
- Lint: Ruff (`ruff` 0.14.11 in `uv.lock`). No `ruff.toml`.
- CI: `.github/workflows/ci.yml` — lint job, then test job with `OPENROUTER_API_KEY=dummy`.

There is no coverage gate, no pytest.ini, and no HTTP or LLM integration test.

## Layout

| Path | Role |
|------|------|
| `got/tests/test_validation_propagation_flow.py` | Builds a two-node graph, validates, epistemic-propagates, asserts confidence increased |
| `got/tests/__init__.py` | Duplicate of an older version of the same test module (also defines `test_validate_then_propagate_epistemic`) |

Prefer adding modules under `got/tests/test_*.py` rather than growing `__init__.py`.

## Commands

```bash
uv sync --dev
uv run pytest
uv run ruff check got examples
```

`.github/workflows/ci.yml` still runs `uv run ruff got examples`. With Ruff 0.14.x that invocation fails (`unrecognized subcommand 'got'`). Use `ruff check`.

`uv run pytest` collects one test from `test_validation_propagation_flow.py` (passed when this docs set was written). The similarly named function in `got/tests/__init__.py` is not collected.

`uv run ruff check got examples` reported unused imports/variables in several modules (documented as existing lint debt, not fixed in the documentation change).

## What to test

The structural engine is the priority: small synthetic graphs, deterministic expected `ValidationResult`, confidence deltas, and analysis clusters.

Do **not** call OpenRouter from unit tests. Inject a fake `OpenRouterClient` if you test `StructureTextServiceLLM`.

Suggested gaps (not currently covered): duplicate nodes, self-loops, `CONTRADICTS` violations, structural cycles, causal vs epistemic propagation, `GraphSpecDTO` reference checks, FastAPI handler with a stubbed use case.

## Determinism

Avoid `datetime.now()` assertions. Prefer confidence values, violation strings, cluster membership, and component counts.
