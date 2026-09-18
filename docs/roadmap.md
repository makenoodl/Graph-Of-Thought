# Roadmap

**Status:** Proposed — not implemented. Source of truth: [RFC 0002](rfcs/0002-sequenced-runtime-roadmap.md). Discussion: https://github.com/makenoodl/Graph-Of-Thought/issues/2

This is not [planning/](planning/README.md) (historical notes) and not current code. Architecture truth remains [architecture/overview.md](architecture/overview.md).

## Order (gates)

1. **Journal + versions + replay + diff** — required for debug and any process reward. Aligns [ADR 0004](decisions/0004-in-memory-graph.md).
2. **Deterministic Adaptive GoT loop** — `EXPAND|VERIFY|PRUNE|STOP`; LLM only in `EXPAND`. AGoT-class, not RGoT.
3. **Budget + scheduler** — measure tokens vs quality (TTC L2).
4. **Transition reward** — rules first (violations, support, cost); GraphPRM is an analogy, not a dataset.
5. **Scoped `GraphRepo`** — log persistence; `REPLACES` / `INVALIDATES`; tests for **Zombie** and **TMA-NM** from day 1 of this wave.
6. **Learned policy** — only when (2)+(3)+(4) produce trajectories.

Do not implement a later number because a planning note or Cursor persona mentions it.
