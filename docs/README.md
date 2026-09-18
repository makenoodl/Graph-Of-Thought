# Documentation index

This tree documents the **implemented** Graph-of-Thought engine. Planning notes that predate this set live in [planning/](planning/README.md) and are not the source of truth.

## Start here

| Audience | Read first |
|----------|------------|
| New contributor | [development/getting-started.md](development/getting-started.md) |
| AI coding agent | [../AGENTS.md](../AGENTS.md) |
| Architecture | [architecture/overview.md](architecture/overview.md) |
| Domain changes | [domain/model.md](domain/model.md), [domain/invariants.md](domain/invariants.md) |

## Architecture

- [overview.md](architecture/overview.md) — components, runtime topology, implemented vs planned
- [components.md](architecture/components.md) — module responsibilities and boundaries
- [data-flow.md](architecture/data-flow.md) — graph and DTO data movement
- [execution-flow.md](architecture/execution-flow.md) — HTTP and in-process pipelines

## Domain

- [model.md](domain/model.md) — entities, value objects, events, operations
- [invariants.md](domain/invariants.md) — enforced constraints and how to verify them

## Decisions, RFCs, and roadmap

- [roadmap.md](roadmap.md) — proposed evolution (not code); [RFC 0002](rfcs/0002-sequenced-runtime-roadmap.md)
- [rfcs/README.md](rfcs/README.md) — proposals before architecture changes; [RFC 0001](rfcs/0001-rfc-adr-process-and-historical-motivations.md) recovers historical motivations
- [decisions/README.md](decisions/README.md) — ADR index and [template](decisions/template.md)

## Development

- [getting-started.md](development/getting-started.md)
- [conventions.md](development/conventions.md)
- [testing.md](development/testing.md)

## Operations

- [configuration.md](operations/configuration.md)
- [observability.md](operations/observability.md)

## In-package docs

- [got/domain/reasoning/README.md](../got/domain/reasoning/README.md) — structural reasoning engine
