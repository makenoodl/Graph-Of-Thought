# ADR 0005: Validation does not block propagation

**Status:** Accepted (implemented)  
**Date:** unknown  
**Code:** `got/application/use_cases/validate_and_propagate_graph.py`

## Context

Validation can mark a graph invalid (for example a `CONTRADICTS` edge). The engine also updates confidences along edges.

## Decision

`ValidateAndPropagateGraphUseCase.execute` always calls `Validator.validate`, then always runs epistemic (and optionally causal) propagation. `is_valid` is returned but not used as a guard.

## Consequences

- Belief updates occur on structurally invalid graphs.
- HTTP analysis can report contradictions while confidences have already been strengthened or weakened.
- Callers that need “propagate only if valid” must branch themselves.

## Rationale

**Unknown.** The use case docstring only states the sequence.

## Alternatives

None implemented.
