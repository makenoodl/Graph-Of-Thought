> Historical planning note. Implementation truth: [architecture/components.md](../architecture/components.md).

# Phase 4 — Application Layer

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

Verified later: `StructureTextServiceLLM` and `ExecuteReasoningService` exist. `EnrichGraphService` and `QueryGraphService` do not. `OpenRouterClient` also lives in this package.

---

## Use Cases

Path: `got/application/use_cases/`

Primary:
- CreateGraphFromText

Secondary:
- EnrichExistingGraph
- ValidateGraph
- AnalyzeReasoning

Verified later: implemented use cases are `CreateGraphFromTextUseCase`, `AnalyzeReasoningUseCase`, `AnalyzeGraphUseCase`, and `ValidateAndPropagateGraphUseCase`. There is no `EnrichExistingGraph` or standalone `ValidateGraph` use case.

---

## DTOs

- Input/output boundaries
- API-safe representations
- Domain remains isolated

Implemented: `GraphSpecDTO`, `GraphDTO`, `AnalysisSummaryDTO`.

---

## Outcome

The system becomes **operable**, not just conceptual.
