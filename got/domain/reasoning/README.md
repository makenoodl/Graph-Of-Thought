## Structural Reasoning Engine

Deterministic, non-LLM reasoning over a `Graph`. Same input graph → same diagnostics and confidence updates (timestamps excluded). This package must not call language models or the network.

Planning-era notes: [docs/planning/reasoning.md](../../../docs/planning/reasoning.md). Implementation map: [docs/architecture/components.md](../../../docs/architecture/components.md).

### Modules

1. **Validation** — `got/domain/reasoning/validation/`
2. **Propagation** — `got/domain/reasoning/propagation/`
3. **Analysis** — `got/domain/reasoning/analysis/`

### Validation

Question: is this graph structurally and epistemically coherent?

Orchestrator: `Validator.validate(graph) -> ValidationResult` (`validator.py`).

`ValidationResult` holds string `violations` and `warnings`, `is_valid` (no violations), and events (`CycleDetected`, `ContradictionDetected`). `ValidationReport` in `violations.py` is unused.

| Class | Layer | Implemented checks |
|-------|-------|-------------------|
| `CausalValidator` | causal | Causal cycles (**warnings**); `FOLLOWS` on a pair that also has a causal edge (**warnings**) |
| `EpistemicValidator` | epistemic | Direct `CONTRADICTS` (**violations**); opposing pairs; evidence-for+against; confidence vs support/weaken counts |
| `StructuralValidator` | structural | Hierarchical cycles (**violations**); anti-symmetry; 2-step transitivity gaps; missing inverses; circular INSTANCE_OF/TYPE_OF; SIMILAR_TO asymmetry |

There is no separate temporal or logical validator. Empty file: `consistency_checker.py`.

An optional `event_handler` may be passed to `Validator`; the HTTP path does not use it.

### Propagation

Question: how does confidence move from starting nodes?

Orchestrator: `PropagationService`.

- `propagate_epistemic(graph, starting_node_ids)` — BFS on `is_epistemic()` outgoing edges
- `propagate_causal(graph, starting_node_ids)` — BFS on `is_causal()` outgoing edges
- `propagate_all` — epistemic then causal

Both update **target node** confidence by a fixed factor (default `0.1`). They do not add edges or infer new causal links. Visit-once BFS. `IMPLIES` / `BLOCKS` are listed in epistemic lookup sets but are not traversed (`is_epistemic()` is false).

Contract: `BasePropagator` protocol in `base_propagator.py`.

### Analysis

Question: where are the contradictions, components, and support chains?

| Class | Implemented output |
|-------|-------------------|
| `ContradictionDetector` | `ContradictionCluster` list |
| `ConnectivityAnalyzer` | Undirected components, isolated nodes (not articulation points) |
| `CriticalPathAnalyzer` | Reverse BFS along supporting relations to a target |

`AnalysisService.analyze()` fills contradiction clusters and connectivity. It sets `critical_paths` to `{}`. Call `analyze_critical_paths` for paths.

### Contribution rules

**Do:** add composable validators, propagators, or analyzers; write focused tests on synthetic graphs; document new invariants in [docs/domain/invariants.md](../../../docs/domain/invariants.md).

**Do not:** introduce LLM calls, hidden heuristics, or prompt/token logic in this package.
