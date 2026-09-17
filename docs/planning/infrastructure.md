> Historical planning note. This file was a duplicate of the Phase 4 application plan. `got/infrastructure/` contains empty FastAPI/LLM/persistence/structuring stubs and is not on the live path. See [architecture/overview.md](../architecture/overview.md).

# Phase 4 — Application Layer (filename: infrastructure.md)

## Objective

Orchestrate domain logic into **usable use cases**.

No business logic here — only coordination.

---

## Services

Path: `got/application/services/`

- StructureTextService
- EnrichGraphService
- ExecuteReasoningService
- QueryGraphService

---

## Use Cases

Path: `got/application/use_cases/`

Primary:
- CreateGraphFromText

Secondary:
- EnrichExistingGraph
- ValidateGraph
- AnalyzeReasoning

---

## DTOs

- Input/output boundaries
- API-safe representations
- Domain remains isolated

---

## Outcome

The system becomes **operable**, not just conceptual.
