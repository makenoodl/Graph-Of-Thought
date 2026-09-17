# Domain invariants

Only constraints that appear in code are listed. Each entry names the enforcer and a verification approach. Items marked **inferred** follow from code shape but are not asserted by tests today.

The structural engine is **non-destructive for topology** (no node/edge add/remove during validate/propagate/analyze) and **destructive for confidence** during propagation.

## Graph integrity

### Unique node id

1. **Invariant:** `Graph.nodes` keys are unique; adding a node with an existing id raises `ValueError`.
2. **Why:** Nodes are addressed by id in edges and ops.
3. **Enforced by:** `Graph.add_node`.
4. **Verify:** unit test duplicate `add_node`; current suite does not cover this.

### Edges reference existing nodes

1. **Invariant:** `source_id` and `target_id` must exist in `Graph.nodes`.
2. **Why:** Prevent dangling relations.
3. **Enforced by:** `Graph.add_edge`. `GraphSpecDTO.validate_references` enforces the same on LLM specs before construction.
4. **Verify:** `GraphSpecDTO` validator; `Graph.add_edge` error path (untested).

### No self-loops

1. **Invariant:** `source_id != target_id` and both non-empty.
2. **Why:** Relation identity and cycle reconstruction assume two endpoints.
3. **Enforced by:** `Edge.__post_init__`.
4. **Verify:** constructing `Edge(a, a, …)` raises (untested).

### Unique edge identity

1. **Invariant:** at most one edge per `(source_id, target_id, relation_type)`.
2. **Why:** `Edge.__eq__` / `__hash__` and `Graph.add_edge` treat that triple as identity. Different relation types between the same pair are allowed.
3. **Enforced by:** `Graph.add_edge` (`if edge in self.edges`).
4. **Verify:** second identical `AddEdge` raises (untested).

### Removing a node removes incident edges

1. **Invariant:** after `remove_node`, no remaining edge mentions that id.
2. **Why:** keep referential integrity.
3. **Enforced by:** `Graph.remove_node`.
4. **Verify:** remove a connected node and assert edge list (untested).

### Non-empty concept

1. **Invariant:** `Node.concept` is non-empty after strip.
2. **Why:** a node is a named thought.
3. **Enforced by:** `Node.__post_init__`.
4. **Verify:** `Node(concept=" ")` raises (untested).

## Confidence

### Bounded belief

1. **Invariant:** `Confidence.value ∈ [0.0, 1.0]`.
2. **Why:** epistemic strength is a closed scale. Code comments reject treating it as a statistical probability.
3. **Enforced by:** `Confidence.__post_init__`; `weaken`/`strengthen` clamp; Pydantic `Field(ge=0.0, le=1.0)` on DTOs.
4. **Verify:** `Confidence(1.1)` raises; DTO validation; propagation test asserts a strengthened value stays meaningful (`test_validate_then_propagate_epistemic`).

### Confidence is replaced, not mutated in place

1. **Invariant:** `Confidence` is frozen; updates assign a new instance on `Node` / `Edge`.
2. **Why:** value-object semantics.
3. **Enforced by:** `@dataclass(frozen=True)` on `Confidence`.
4. **Verify:** attempting field assignment on `Confidence` raises (untested).

## Validation vs mutation

### Validation does not modify topology or confidence

1. **Invariant:** `Validator.validate` only reads the graph and fills `ValidationResult`.
2. **Why:** validation is an audit of a snapshot.
3. **Enforced by:** validators have no `add_node`/`update_confidence` calls (code inspection).
4. **Verify:** compare graph before/after `validate` (untested except that the flow test validates then propagates separately).

### Propagation does not add or remove nodes or edges

1. **Invariant:** documented on `BasePropagator`; implementations only call `Node.update_confidence`.
2. **Why:** keep topology stable while beliefs update.
3. **Enforced by:** `EpistemicPropagator`, `CausalPropagator`.
4. **Verify:** node/edge counts unchanged after `propagate_epistemic` (partially: the flow test checks confidence, not counts).

### Invalid graphs still receive propagation

1. **Invariant:** `ValidateAndPropagateGraphUseCase` always propagates after `validate`.
2. **Why:** unknown as a historical decision. Observable consequence: contradictions do not block belief updates.
3. **Enforced by:** `validate_and_propagate_graph.py` with no `is_valid` guard.
4. **Verify:** graph with `CONTRADICTS` still changes confidence (untested).

### Severity split (causal vs structural vs epistemic)

1. **Invariant:** causal cycles are **warnings**; hierarchical structural cycles and direct `CONTRADICTS` are **violations** (`is_valid` becomes false).
2. **Why:** comments in `CausalValidator` say causal cycles “can be valid”; epistemic direct contradiction is treated as a hard conflict; structural hierarchy is expected to be a DAG.
3. **Enforced by:** `add_warning` vs `add_violation` in each validator.
4. **Verify:** construct a causal cycle vs `PART_OF` cycle vs `CONTRADICTS` edge (untested).

## Layer classification

### Epistemic edges include SUPPORTS and CONTRADICTS

1. **Invariant:** `get_layer()` returns `"epistemic"` for `SUPPORTS` and `CONTRADICTS` because `is_epistemic()` is checked before the logical fallback.
2. **Why:** those relations participate in belief validation and epistemic BFS.
3. **Enforced by:** `RelationType.get_layer` / `is_epistemic`.
4. **Verify:** `RelationType.SUPPORTS.get_layer() == "epistemic"`.

### Visit-once BFS

1. **Invariant:** each reachable node is dequeued at most once; a node’s confidence is updated when an incoming traversed edge is processed, not once per graph.
2. **Why:** termination and a deterministic visit order (queue order + `graph.edges` list order).
3. **Enforced by:** `visited` sets in both propagators.
4. **Verify:** diamond-shaped graphs (untested). **Inferred:** determinism holds for a given `edges` list order; `datetime.now()` on the graph timestamp still changes.

## LLM spec

### Spec references must resolve

1. **Invariant:** every `starting_node_ids` entry and every edge endpoint exists in `GraphSpecDTO.nodes`.
2. **Why:** prevent incomplete LLM JSON from building an inconsistent graph.
3. **Enforced by:** `GraphSpecDTO.validate_references`.
4. **Verify:** Pydantic validation on a spec with a dangling edge (untested in-repo).

### Unknown enum tokens are coerced before validation

1. **Invariant:** after sanitize, `node_type` is one of the eight allowed strings; `relation_type` is one of the 22 relation values. Unknown node types become `concept`; unknown relations become `supports`.
2. **Why:** LLM enum drift (`fix(llm): coerce unknown GraphSpec enums from model output`).
3. **Enforced by:** `StructureTextServiceLLM._sanitize_llm_spec`.
4. **Verify:** feed a spec dict with `"node_type": "opportunity"` (untested).

## Concurrency and transactions

1. **Invariant (inferred):** a `Graph` is not thread-safe. Lists/dicts are mutated in place with no locks.
2. **Why:** single-threaded request and library usage.
3. **Enforced by:** nothing.
4. **Verify:** not applicable until shared graphs exist.

There are no database transactions. Idempotency is not implemented for HTTP: repeating `POST /analyze-text` calls the LLM again and mints new ids.

## Security

1. **Invariant:** no authentication or authorization on the API.
2. **Why:** unknown; the app is a local development server.
3. **Enforced by:** absence of middleware.
4. **Verify:** route list in `got/api`.

`OPENROUTER_API_KEY` is read from the environment. Prompts include caller `text` verbatim; do not send secrets in `text`.

## Public API compatibility

No versioning policy is implemented beyond FastAPI `version="0.1.0"`. `GraphDTO` / `AnalyzeTextResponse` fields are the HTTP contract. `blocked_paths` / `viable_paths` are part of that JSON but are not computed.
