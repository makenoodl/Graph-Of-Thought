> Historical planning note. Implementation truth: [architecture/components.md](../architecture/components.md).

# Phase 2 — Structural Reasoning Engine

## Objective

Provide **deterministic reasoning over graphs**, independent of LLMs.

This layer answers:
- Is this reasoning coherent?
- Are there contradictions?
- What propagates from what?

---

## Modules

### Validation

Path: `got/domain/reasoning/validation/`

Validators:
- CausalValidator
  - Detect causal cycles
  - Validate temporal coherence
- EpistemicValidator
  - Detect belief conflicts
- StructuralValidator
  - Hierarchy consistency
  - Transitivity checks

Validator orchestrator:
- validator.py

---

### Propagation

Path: `got/domain/reasoning/propagation/`

- EpistemicPropagator
  - Propagates confidence across relations
- CausalPropagator
  - Transitive causal inference
- propagation.py (orchestrator)

Verified later: both propagators BFS from starting nodes and update target `Confidence` in place. They do not create new edges.

---

### Analysis

Path: `got/domain/reasoning/analysis/`

- ContradictionDetector
- Connectivity analysis
- Critical reasoning paths

Verified later: `AnalysisService.analyze()` leaves `critical_paths` empty. Call `analyze_critical_paths()` separately.

---

## Design Constraints

- No probabilistic hallucination
- No LLM calls
- Deterministic and testable

---

## Outcome

This layer turns the graph into an **active reasoning object**.
