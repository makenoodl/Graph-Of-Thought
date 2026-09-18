# ADR 0004: In-memory graph, no repository

**Status:** Accepted (current)  
**Date:** unknown  
**Code:** `got/domain/model/graph.py`; empty `got/infrastructure/persistence/`

## Context

Planning notes describe persisted reasoning and a `GraphRepo` port.

## Decision

Live code keeps `Graph` in memory on the caller or HTTP request. There is no save/load implementation. Persistence modules are empty files.

## Consequences

- Restarting uvicorn drops all graphs.
- No multi-user isolation beyond process memory.
- `Graph.version` is unused by ops; temporal rollback is not implemented.
- Domain events cannot be replayed from storage.

Proposed successor (not accepted): [RFC 0002](../rfcs/0002-sequenced-runtime-roadmap.md) Wave 1 (in-process journal) then Wave 5 (scoped `GraphRepo`). This ADR stays current until that work lands.

## Rationale

**Unknown.** Observable fact: no working repository is wired.

## Alternatives

Empty `got/domain/ports/graph_repo.py`, `got/infrastructure/persistence/json_repo.py`, `memory_repo.py`.
