# AGENTS.md

Engineering contract for AI coding agents working in this repository.

Graph-of-Thought is a Python engine that stores reasoning as a typed in-memory graph and runs **deterministic** validation, confidence propagation, and analysis. A language model is used only to turn text into `GraphSpecDTO`. Cursor `*-agent.mdc` files describe **intended editor personas**, not implemented Python services.

## Navigate

| Goal | Location |
|------|----------|
| HTTP entry | `got/api/app.py`, `got/api/routes/analyze_text.py` |
| Text → graph | `got/application/services/structure_text_service_llm.py` |
| Reasoning pipeline | `got/application/services/execute_reasoning.py` |
| Graph aggregate | `got/domain/model/` |
| Mutations | `got/domain/ops/` |
| Structural engine | `got/domain/reasoning/` |
| Tests | `got/tests/` |
| Example (no LLM) | `examples/simple_sandbox.py` |

Empty and unwired: `got/domain/ports/`, `got/infrastructure/`, `got/interface/`, `main.py` (hello stub), `got/domain/ops/merge_nodes.py`.

Documentation index: [docs/README.md](docs/README.md).

## Read before modifying

| Change type | Read |
|-------------|------|
| Any nontrivial change | [docs/architecture/overview.md](docs/architecture/overview.md), [docs/domain/invariants.md](docs/domain/invariants.md) |
| Domain model / ops | [docs/domain/model.md](docs/domain/model.md) |
| Validators, propagators, analysis | [got/domain/reasoning/README.md](got/domain/reasoning/README.md), [docs/architecture/components.md](docs/architecture/components.md) |
| API or DTOs | [docs/architecture/execution-flow.md](docs/architecture/execution-flow.md), [docs/architecture/data-flow.md](docs/architecture/data-flow.md) |
| Config / secrets | [docs/operations/configuration.md](docs/operations/configuration.md) |
| Tests | [docs/development/testing.md](docs/development/testing.md) |

Do not treat [docs/planning/](docs/planning/README.md) as implementation truth.

## Workflow

**Understand → Scope → Plan → Implement → Verify → Report**

1. **Understand** — Read the modules you will touch. Confirm whether the feature is implemented, partial, empty scaffolding, or only a Cursor persona. Do not invent ports, persistence, or agents because planning docs mention them.
2. **Scope** — Name affected packages, public DTOs/routes, and invariants from [docs/domain/invariants.md](docs/domain/invariants.md).
3. **Plan** — For nontrivial work, state the layer (`domain` / `application` / `api`), whether LLM I/O is involved, and how you will test. Structural engine work must stay deterministic and LLM-free.
4. **Implement** — Small, layer-respecting changes. Reuse `Validator`, `PropagationService`, `AnalysisService`, and domain ops. Do not copy reasoning rules into the API layer.
5. **Verify** — Run `uv run pytest` and, for Python edits, `uv run ruff check got examples`. Add or extend synthetic graph tests for engine changes. Do not call OpenRouter in unit tests. Do not use `uv run ruff got examples` (obsolete CLI; still present in CI).
6. **Report** — What changed, what you ran, what you could not verify (no key, no coverage of a branch, empty module still unused).

## Architectural boundaries

Preserve these unless the task is explicitly to change them:

- `got.domain` must not import `got.application` or `got.api`.
- `got/domain/reasoning` must not call LLMs, HTTP, or the filesystem.
- Validation remains non-destructive to graph topology. Propagation may update `Confidence` only.
- `POST /analyze-text` stays a thin map over use cases.
- Do not wire empty `got/infrastructure` by accident; either implement and connect a port properly or extend the live application services.

Choose the module by layer, not by persona name:

- Graph integrity → `got/domain/model` or `got/domain/ops`
- Coherence rules → `got/domain/reasoning/validation`
- Belief updates → `got/domain/reasoning/propagation`
- Insights → `got/domain/reasoning/analysis`
- Orchestration of those → `got/application/use_cases` or `services`
- HTTP → `got/api`

## Conventions and dependencies

Follow [docs/development/conventions.md](docs/development/conventions.md).

- New runtime dependencies belong in `pyproject.toml` only when the code imports them. `networkx`, `openai`, and `transformers` are currently unused.
- New env vars: document in [docs/operations/configuration.md](docs/operations/configuration.md). Never commit secrets or `.env`.
- Prefer ops for mutations. Document any intentional bypass (the LLM structurer currently bypasses ops).

## Incomplete validation

If you cannot run pytest, Ruff, or a live OpenRouter call, say so. Do not claim a command passed. If behavior is untested, label it. If a planning doc disagrees with code, trust the code and note the drift.
