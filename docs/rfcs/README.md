# RFCs

RFCs propose a change **before** it becomes an architecture decision.

ADRs in [../decisions/](../decisions/README.md) record what was **accepted and implemented** (or explicitly deferred). Git history and [../planning/](../planning/README.md) show what happened; they do not replace an RFC.

## When to write an RFC

Write one for a change that would:

- alter a layer boundary (`got/domain`, `got/application`, `got/api`)
- add persistence, a new LLM path, or a new public HTTP contract
- change an invariant in [../domain/invariants.md](../domain/invariants.md)
- fill or delete empty scaffolding (`got/domain/ports`, `got/infrastructure`)
- recover or revise historical rationale on an existing ADR

Skip an RFC for typo-level docs, tests on the current contract, or small bugfixes inside an existing module.

## Lifecycle

```text
Draft RFC → GitHub issue discussion → Accepted RFC → ADR (implementation decision)
```

| Status | Meaning |
|--------|---------|
| Draft | Authoring in this folder |
| Proposed | Linked from a GitHub issue; open for comment |
| Accepted | Follow-up ADR exists or is in progress |
| Rejected | Not pursued; keep the RFC for history |
| Superseded | Replaced by a later RFC |

## Index

| ID | Title | Status |
|----|-------|--------|
| [0001](0001-rfc-adr-process-and-historical-motivations.md) | RFC/ADR process and historical motivation recovery | Accepted (process); history recovery open |

## Template

Copy [template.md](template.md) to `NNNN-short-title.md`.
