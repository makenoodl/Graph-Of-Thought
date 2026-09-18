# RFC 0002: Sequenced runtime roadmap (journal → adaptive loop → budget → reward → scoped persistence → learned policy)

**Status:** Proposed  
**Date:** 2026-09-18  
**Author:** maintainer direction (chat 2026-09-18)  
**Issue:** https://github.com/makenoodl/Graph-Of-Thought/issues/2  
**Follow-up ADR:** none yet. Wave 1 would amend [ADR 0004](../decisions/0004-in-memory-graph.md) only after an in-process journal exists. Wave 5 would replace ADR 0004 if a `GraphRepo` is wired.

## Summary

Evolve Graph-of-Thought from a one-shot in-memory engine into a **verifiable reasoning runtime** in a fixed order. Later waves are gated: no learned policy without trajectories; no Adaptive Graph of Thoughts (AGoT) loop without a journal; no Graph-of-Thoughts process reward model (GraphPRM) dataset import.

This RFC is the roadmap. It is **not** implemented. `docs/planning/` remains historical notes, not this plan.

## Motivation

Today a `Graph` lives for one library call or HTTP request ([ADR 0004](../decisions/0004-in-memory-graph.md)). Ops already return events (`NodeCreated`, `EdgeAdded`, `NodeConfidenceUpdated`, …) but nothing stores them. `Graph.version` / `increment_version()` exist; ops do not increment version. `GraphUpdated` has no producer. Propagation mutates `Confidence` without emitting events. Without a journal there is no replay, no diff, no process reward, and no honest debug.

Literature split (2023–2026):

- **Prompt topologies** ([GoT](https://arxiv.org/abs/2308.09687), [AGoT](https://arxiv.org/abs/2502.05078), [RGoT](https://arxiv.org/abs/2605.22195)): Graph of Operations / Graph Reasoning State for one inference. Ephemeral.
- **Task KG** ([KGoT](https://arxiv.org/abs/2504.02670)): evolving triples, still usually one task.
- **Agent memory** ([AriGraph](https://arxiv.org/abs/2407.04363), [SodaMem](https://arxiv.org/abs/2608.08055)): persist *what is currently true*, with contradiction / supersession.

This repo already has typed nodes, `CONTRADICTS`, atomic ops, and a deterministic engine ([ADR 0001](../decisions/0001-llm-interpreter-vs-deterministic-core.md)). The missing substrate is the **operation journal**.

## What is already known

| Fact | Where |
|------|--------|
| LLM interprets; domain reasons | ADR 0001, `got/domain/reasoning` |
| In-memory only; empty `GraphRepo` / JSON repo | ADR 0004, empty `got/domain/ports/graph_repo.py` |
| Validate then always propagate | ADR 0005 |
| Events returned, not stored | `docs/operations/observability.md` |
| `blocked_paths` / `viable_paths` always 0 | `AnalyzeReasoningUseCase` |
| Empty hexagonal persistence | `got/infrastructure/persistence/` |
| RFC then ADR | ADR 0006, RFC 0001 |

Do not treat Cursor `*-agent.mdc` personas as the runtime.

## Open questions

1. ADR 0004 historical *why* (RFC 0001 Q3) is still unknown. This RFC does **not** fill that. It proposes a **future** change.
2. Exact on-disk format (JSONL vs SQLite) is deferred to the Wave 5 ADR. Wave 1 is in-process only.
3. Whether `REPLACES` / `INVALIDATES` are new `RelationType` values or edge metadata is a Wave 5 RFC amendment if the enum change is contentious.

## Gates (not a buffet)

```text
(1) Journal + version + replay + diff
        │
        ├─► (2) Deterministic AGoT loop (EXPAND|VERIFY|PRUNE|STOP)
        │         │
        │         ├─► (3) Budget + scheduler (TTC L2)
        │         │
        │         └─► (4) Rule-based transition reward (then small critic)
        │
        └─► (5) Scoped GraphRepo + REPLACES/INVALIDATES
                  (threat tests Zombie / TMA-NM from day 1 of this wave;
                   replay from (1) is the oracle)

(6) Learned policy (RGoT-class)  — only if (2)+(3)+(4) emit trajectories
```

A wave may be designed on paper while the previous wave is in review. It may not land in `got/` until its gate is green.

## Wave 1 — Observability and versions

**Aligns:** README (events unused), ADR 0004 (no replay), this RFC.

**Layer:** `got.domain` (event completeness, `Graph.version` on ops) + `got.application` (run log, replay, diff). No filesystem in `got/domain/reasoning`.

**In:** sequence of ops + optional `propagate_*` / `validate` / `analyze` on a `Graph`.

**Out:** `run_id`, append-only `EventLog`, `graph.version` after each mutating step, `replay(log) -> Graph`, `diff(g1, g2)` (node/edge/confidence delta).

**Must:**

- Every `AddNode` / `AddEdge` / `Remove*` / `UpdateNodeConfidence` already returns an event; the application **appends** it.
- Epistemic/causal propagation emits `NodeConfidenceUpdated` (today it mutates silently).
- Ops call `Graph.increment_version()` (or equivalent) so `GraphUpdated` can be produced if we keep that type.
- `replay` is deterministic given event order (same as current edge-list BFS).
- Unit tests: build sandbox graph via ops → replay → equal topology and confidences; diff two versions after one `CONTRADICTS` edge.

**Must not:** disk, Neo4j, OpenTelemetry exporter, LLM.

**Done when:** a synthetic test replays the basketball sandbox and the rain→grass test without calling OpenRouter.

Without Wave 1 there is no process reward (Wave 4) and no debug of Adaptive GoT (Wave 2).

## Wave 2 — Deterministic Adaptive GoT loop

**This is AGoT-class, not RGoT.** Heuristic policy, not RL.

**Layer:** `got.application` orchestrator. Policy is **deterministic Python**. Structural engine stays LLM-free.

**Actions:** `EXPAND | VERIFY | PRUNE | STOP`.

| Action | Who | Uses LLM? |
|--------|-----|-----------|
| `EXPAND` | application: ask structurer for a `GraphSpecDTO` **diff**, apply via ops | yes (existing OpenRouter path) |
| `VERIFY` | `Validator` + `AnalysisService` | no |
| `PRUNE` | domain ops `RemoveNode` / `RemoveEdge` under explicit rules | no |
| `STOP` | policy | no |

**Policy (v0):** score = `uncertainty × cost`. Uncertainty from low `Confidence`, contradiction clusters, validation violations. Cost = expansion count and/or token estimate from last LLM call. Expand only if score exceeds a threshold and budget remains.

**In:** `run_id`, current graph, remaining budget.

**Out:** next action + journal events for that step; STOP with reason (`goal`, `budget`, `converged`, `invalid`).

**Must not:** PPO / learned weights; LLM inside VERIFY/PRUNE/STOP; mutating topology inside `got/domain/reasoning`.

**Done when:** a stubbed `OpenRouterClient` drives two EXPAND then STOP on a synthetic spec; journal can replay the whole loop.

## Wave 3 — Budget and scheduler

**Aligns:** test-time compute surveys (L2 = allocate extra inference under a budget), not a new prompting paper.

**Layer:** application scheduler wrapping Wave 2.

**In:** token/time/expansion caps; task id.

**Out:** per-run measurements: tokens in/out (when LLM used), expansions, `contradiction_count`, `is_valid`, wall time. A small table in `docs/` or `examples/` for a few **synthetic** graphs plus optional live OpenRouter (not unit tests).

**Done when:** one documented command prints tokens vs contradiction count for the two sandbox graphs (LLM skip) and, if a key is present, one live `analyze-text` — labelled unverified if no key.

## Wave 4 — Transition reward

**GraphPRM ([2503.00845](https://arxiv.org/abs/2503.00845)) is an analogy** (process-level reward on graph *structure*), **not a dataset to ingest**. That paper is about graph *tasks*, not GoT prompting.

**Layer:** application, reading the Wave 1 journal.

**v0 (rules):** scalar `r` from Δviolations, Δcontradiction clusters, support-edge count, and expansion cost. Deterministic.

**v1 (later):** small critic on the same features. Still no GraphPRM weights.

**In:** `(graph_t, action, graph_t+1, cost)`.

**Out:** `r`, attached as metadata on the journal step (not a domain invariant).

**Done when:** tests assert reward sign: adding `CONTRADICTS` vs adding `SUPPORTS` on the rain graph.

## Wave 5 — Scoped persistence

**Revises ADR 0004** when implemented. Fill `GraphRepo` **properly** (port + one adapter), or keep it empty — do not half-wire.

**Scope:** persist **event log** per `run_id` (preferred) or snapshot+log. First adapter: JSONL files. Not a multi-tenant product.

**New relations (proposal):** `REPLACES` and `INVALIDATES` on `RelationType` (or documented metadata until an enum RFC). Invalidated nodes stay in the log; they leave the **live** working set.

**Threats from day 1 of this wave** (tests, not blog posts):

| Threat | Meaning here | Test |
|--------|----------------|------|
| **Zombie** | A node/edge marked invalid/replaced still participates in validate/propagate/analyze | After `INVALIDATES`, replay live set; zombie id absent from propagation seeds |
| **TMA-NM** | Temporal / identity attack: rewrite history in place, or merge two nodes because `concept` strings match | Journal is append-only (no update-in-place API); identity is `node_id`, not concept text |

Wave 1 replay is the oracle: `replay(log[:t])` is the belief at `t`.

**Must not:** vector DB as the graph; silent `Graph.add_node` bypass on the persist path.

## Wave 6 — Learned policy (RGoT-class)

**Only if** Waves 2+3+4 produce stored trajectories `(state, action, reward, next_state)`.

Train **outside** `got/domain/reasoning`. The engine remains the environment. Swap the Wave 2 heuristic for a policy module behind an application interface.

**Must not:** start here; train on GraphPRM graph-task data as if it were GoT runs.

## Consequences

If accepted:

- README Status and `AGENTS.md` point here instead of vague “roadmap ideas”.
- Each wave lands with its own follow-up ADR (or an amendment to 0004 for waves 1/5).
- `got/infrastructure/persistence` stays empty until Wave 5.
- Hugging Face traces (dataset of journals) become possible after Wave 1, not before.

## Alternatives

- **Implement all six at once:** rejected; gates exist because later waves need the journal.
- **Snapshot-only `GraphRepo.save(graph)`:** rejected as the *only* store; no replay, no PRM, no TMA-NM test. Snapshots may *accompany* the log.
- **AGoT-style LLM at every node:** rejected for VERIFY/PRUNE/STOP (ADR 0001).
- **Treat `docs/planning/` as this roadmap:** those notes predate the engine snapshot and are not sequenced.

## References (external)

- Besta et al., Graph of Thoughts, [arXiv:2308.09687](https://arxiv.org/abs/2308.09687) — GoO + GRS.
- Pandey et al., Adaptive Graph of Thoughts, [arXiv:2502.05078](https://arxiv.org/abs/2502.05078) — test-time DAG; Wave 2 analogue.
- Riesen & von Niederhäusern, Reinforced Graph of Thoughts, [arXiv:2605.22195](https://arxiv.org/abs/2605.22195) — Wave 6 only.
- Besta et al., Knowledge Graph of Thoughts, [arXiv:2504.02670](https://arxiv.org/abs/2504.02670) — evolving KG; not this engine.
- GraphPRM, [arXiv:2503.00845](https://arxiv.org/abs/2503.00845) — process reward *analogy*.
- Anokhin et al., AriGraph, [arXiv:2407.04363](https://arxiv.org/abs/2407.04363); SodaMem, [arXiv:2608.08055](https://arxiv.org/abs/2608.08055) — persist current truth; Wave 5 threats.
