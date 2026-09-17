# RFC 0001: RFC/ADR process and historical motivation recovery

**Status:** Accepted (process). Historical questions remain open on the GitHub issue.  
**Date:** 2026-09-17  
**Author:** documentation pass (repository reconstruction)  
**Issue:** https://github.com/makenoodl/Graph-Of-Thought/issues/1  
**Follow-up ADR:** [../decisions/0006-rfc-and-adr-for-evolution.md](../decisions/0006-rfc-and-adr-for-evolution.md)

## Summary

Adopt a written RFC → issue → ADR loop so future architecture changes have recorded motivation. Use the same loop to **recover** rationale that current ADRs mark as unknown, without inventing history.

## Motivation

ADRs [0001](../decisions/0001-llm-interpreter-vs-deterministic-core.md)–[0005](../decisions/0005-validation-does-not-block-propagation.md) describe what the code does. Several **why** fields are unknown. Phase notes in [../planning/](../planning/README.md) were written around 2026-02-09 and were gitignored until 2026-09-17, so they never served as a decision log.

Without RFCs and issues, the next contributor cannot tell:

- which empty files are still intended
- which Cursor agent personas were a product direction vs editor experiments
- whether in-memory graphs and non-blocking validation were deliberate

## What is already known

The following timeline is from `git log` only. It is **evolution**, not motivation.

| When | Evidence | What landed |
|------|----------|-------------|
| 2026-01-09 | `c7e2ade`–`342b1c8` | Project bootstrap. Commit `5c2ed7a` added the **full package tree as empty files**, including ports, infrastructure (OpenAI, JSON/memory repos, rule-based + LLM structurers), `enrich_graph.py`, `query_graph.py`, `merge_nodes.py`, and `tests/`. Value objects `Confidence` and `NodeType` were the first non-empty domain files. `RelationType`, `Edge`, `Graph`, `Node` filled the same day. |
| 2026-01-09 | `bad58b9` | Empty `tests/test_domain.py` and `tests/test_structure.py` removed. |
| 2026-01-09 | `cccf943` | Long `Confidence` commentary: epistemic belief, not statistical probability. This is the earliest written domain rationale still in tree. |
| 2026-01-12–15 | events + ops | `NodeCreated`, `EdgeAdded`, `ContradictionDetected`, `GraphUpdated`, `CycleDetected`, `AddNode`/`AddEdge`/`Remove*`. |
| 2026-01-15–16 | validators | `CausalValidator`, `Validator` orchestrator. |
| 2026-01-17 | `99c2dde`, `fa1c307` | First public hypothesis in README: reasoning as a graph rather than a sequence; “thought-centric” vs “answer-centric”. |
| 2026-02-09 | `d86c272`, `7b56659` | `.gitignore` started ignoring `docs/`. Structural engine README added under `got/domain/reasoning/`. |
| 2026-02-12–21 | epistemic + structural validators, propagation | Belief/evidence checks; `BasePropagator`; epistemic then causal confidence BFS. |
| 2026-02-22 | use cases | Application use-case files start filling. |
| 2026-02-28 | `ca8476d`–`3f3dc22` | Cursor `*-agent.mdc` personas (orchestrator, research, decomposition, planner, execute, critic, reflection, expander, memory, observability, pruning). Same day: analysis modules (`ContradictionDetector`, connectivity, critical paths). |
| 2026-03-02–03 | DTO + FastAPI + OpenRouter | `GraphDTO`, `ExecuteReasoningService`, FastAPI, `GraphSpecDTO`, `.env` loading. Live LLM path is application-layer OpenRouter, not `got/infrastructure/llm`. |
| 2026-03-11 | `99e67c0` | GitHub Actions CI (Ruff then pytest). |
| 2026-07-19 | `317ea1f` | Sanitize unknown LLM enum values before `GraphSpecDTO`. |
| 2026-09-17 | `91337b6`–`1f052b4` | Docs versioned; ADRs 0001–0005 record **observed** decisions. |

Stated motivations that **do** appear in-tree (do not treat as complete):

- README / engine README: LLM as interpreter; domain engine deterministic and testable.
- `Confidence` docstring: non-binary belief, revision instead of hard deletion.
- Planning `objective.md`: graph is the reasoning state; do not collapse thought into disposable text.

## Open questions

These cannot be answered from git messages or code comments. They are the subject of the companion GitHub issue.

1. **Hexagonal scaffolding (ADR 0002 / 0004):** Why commit empty ports and `got/infrastructure` on day one, then implement FastAPI and OpenRouter under `got/api` and `got/application`? Abandoned hexagonal plan, deferred MVP, or leftover from a template?
2. **OpenRouter + stdlib (ADR 0003):** Why not the declared `openai` extra or `openai_client.py`? Cost, lock-in, simplicity, or time pressure?
3. **No persistence (ADR 0004):** Was “persistent reasoning” in planning notes a near-term goal that slipped, or a long-horizon vision? Should `GraphRepo` stay?
4. **Validate then always propagate (ADR 0005):** Intentional “beliefs update even under contradiction”, or an incomplete guard?
5. **Cursor agents (2026-02-28):** Product direction for a multi-agent runtime on the graph, or Cursor-only workflow? `planner-agent.mdc` duplicates `decomposition-agent.mdc` — known?
6. **Deleted tests (2026-01-09):** Why remove the first test files instead of filling them?
7. **`docs/` gitignored (2026-02-09):** Avoid committing BMAD/scratch notes, or an accident?
8. **Causal cycles as warnings:** Why warnings for causal cycles and violations for hierarchical cycles / `CONTRADICTS`?

Until those answers exist, ADRs must keep **unknown** where they already do. Filling them belongs in ADR amendments after the issue is answered, not in speculative prose.

## Proposal

1. Keep RFCs in `docs/rfcs/` using [template.md](template.md).
2. Open a GitHub issue for each Proposed RFC (labels `documentation` and/or `question`).
3. When a proposal is accepted, add or update an ADR. Link RFC ↔ ADR ↔ issue.
4. Use RFC 0001’s issue specifically to collect maintainer answers to the open questions above, then amend ADRs 0002–0005 (and 0001 dates) with cited replies or commits — still no invented rationale.
5. Agents and humans treat [README.md](README.md) as the process entry; they do not implement features only because [../planning/](../planning/README.md) names them.

## Consequences

- Architecture discussion has a durable paper trail (RFC + issue + ADR).
- Historical recovery is explicit work, not guessed in overview docs.
- Slight process overhead for large changes; none for local bugfixes.

## Alternatives

- **ADRs only:** already insufficient where rationale is unknown.
- **Planning notes as history:** they mix intent and unimplemented modules; they were not versioned until 2026-09-17.
- **Git log as the only history:** shows sequence, not rejected alternatives or goals.
