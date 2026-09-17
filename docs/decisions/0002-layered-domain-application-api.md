# ADR 0002: Domain / application / API packages

**Status:** Accepted (implemented)  
**Date:** unknown  
**Code:** `got/domain`, `got/application`, `got/api`

## Context

The codebase needs a place for pure graph logic and a place for HTTP and LLM I/O without mixing them.

## Decision

- `got/domain`: aggregate, ops, events, reasoning engine
- `got/application`: use cases, OpenRouter client, DTOs
- `got/api`: FastAPI factory and routes

Application imports domain. API imports application. Domain does not import application or API.

## Consequences

- Use cases coordinate existing domain services; they should not reimplement propagation rules.
- DTOs (`GraphDTO`, `GraphSpecDTO`) sit at the application boundary.
- Empty `got/infrastructure` and `got/domain/ports` are **not** the live adapter layer.

## Rationale

Package layout and comments on use cases (“does not contain domain logic”). Historical motivation for rejecting a full hexagonal layout is **unknown**.

## Alternatives

`got/domain/ports` and `got/infrastructure` exist as empty scaffolding and are unused by `got/api`.
