> Historical planning note. Implementation truth: [domain/model.md](../domain/model.md). `MergeNodes` is empty; `GraphUpdated` is not emitted by ops.

# Phase 1 — Domain Foundations (Completed)

## Objective

Build a **pure domain core** representing reasoning as a graph,
independent of infrastructure, LLMs, or frameworks.

---

## Core Concepts

### Graph
- Aggregate root
- Owns nodes, edges, versioning, invariants

### Node
Represents:
- Concept
- Hypothesis
- Fact
- Constraint
- State

### Edge
Represents a typed relation:
- Causal
- Epistemic
- Support
- Contradiction
- Dependency
- Refinement

---

## Value Objects

- NodeType
- RelationType (22 types)
- Confidence (probabilistic / ordinal)

Note: `Confidence` is documented in code as epistemic belief, not a statistical probability.

---

## Domain Events

- NodeCreated
- EdgeAdded
- NodeRemoved
- GraphUpdated
- ContradictionDetected

Purpose:
- Traceability
- Cognitive history
- Auditing

Verified later: ops return events; there is no event store.

---

## Operations (Ops)

Atomic domain actions:
- AddNode
- AddEdge
- RemoveNode
- MergeNodes

Guarantees:
- Invariant preservation
- Traceable mutations
- Deterministic behavior

Verified later: `RemoveEdge` and `UpdateNodeConfidence` also exist. `got/domain/ops/merge_nodes.py` is empty.

---

## Outcome

The domain package is free of LLM imports. Test coverage of the domain is limited to a single flow test.
