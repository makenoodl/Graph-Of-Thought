# Conventions

Conventions below are taken from existing modules. There is no Ruff config in `pyproject.toml`. Lint locally with `uv run ruff check got examples` (Ruff defaults). CI still calls `uv run ruff got examples`, which Ruff 0.14.x does not accept.

## Layers

| Package | Allowed dependencies | Typical types |
|---------|----------------------|---------------|
| `got/domain` | stdlib + domain only | `@dataclass`, `Enum` |
| `got/application` | domain + pydantic + stdlib | use-case classes, Pydantic DTOs |
| `got/api` | application + FastAPI | routers, request/response models |

Do not import `got.application` or `got.api` from `got.domain`. Do not add LLM or HTTP clients under `got/domain/reasoning`.

Prefer extending live packages over filling empty `got/infrastructure` or `got/domain/ports` unless the change explicitly introduces a wired port.

## Mutations

- Structural changes: `got.domain.ops` (`AddNode`, `AddEdge`, `RemoveNode`, `RemoveEdge`, `UpdateNodeConfidence`).
- Integrity checks that must hold even if ops are bypassed: `Graph.add_node` / `Graph.add_edge` / `Edge.__post_init__`.
- **Deviation:** `StructureTextServiceLLM` builds nodes and edges with `Graph.add_*` directly. New construction paths should use ops unless there is a reason to skip events.

Do not mutate `graph.edges` except inside `Graph` or `RemoveEdge` (which already does).

## Reasoning engine

- Validators: read-only, return `ValidationResult`, emit `CycleDetected` / `ContradictionDetected` when applicable.
- Propagators: in-place confidence updates, BFS, no topology changes, deterministic given edge list order.
- New validators/propagators: separate class, register in `Validator` or `PropagationService`, add a synthetic-graph test.

## DTOs vs domain

- LLM input contract: `GraphSpecDTO`.
- API output graph: `GraphDTO.from_domain`.
- Do not expose `ValidationResult` internals on HTTP unless you intentionally expand the response model.

## Style observed in-tree

- Python 3.11 typing (`list[str]`, `X | None`) mixed with older `List`/`Optional` and some files using `from __future__ import annotations`.
- Domain comments in English; a few validator messages in French (`CausalValidator` cycle/temporal strings).
- Ops are classes with `execute(...)`, not free functions.

## Configuration

No settings object. New tunables should not be hardcoded in several places; today the OpenRouter model and timeout live on `OpenRouterClient` fields, and propagator `factor` defaults to `0.1`.
