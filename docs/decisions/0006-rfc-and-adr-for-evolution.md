# ADR 0006: RFC then ADR for architecture evolution

**Status:** Accepted  
**Date:** 2026-09-17  
**Code:** `docs/rfcs/`, `docs/decisions/` (process only; no runtime change)  
**RFC:** [../rfcs/0001-rfc-adr-process-and-historical-motivations.md](../rfcs/0001-rfc-adr-process-and-historical-motivations.md)  
**Issue:** https://github.com/makenoodl/Graph-Of-Thought/issues/1

## Context

ADRs 0001–0005 record decisions visible in code. Several rationales are unknown. Phase notes under `docs/planning/` and Cursor agent rules describe intent that is not always implemented. There was no place to propose a change and attach a GitHub discussion before editing the engine.

## Decision

- Proposals that change architecture, invariants, public HTTP/DTO contracts, persistence, or LLM boundaries are written as RFCs in `docs/rfcs/`.
- Each Proposed RFC is linked to a GitHub issue.
- Accepted outcomes are recorded as ADRs in `docs/decisions/`, with RFC and issue links.
- Historical motivations missing from ADRs 0001–0005 are filled only after the RFC 0001 issue is answered, with citations. Unknown remains unknown until then.

## Consequences

- `docs/rfcs/README.md` is the process index.
- `AGENTS.md` points agents at RFCs for nontrivial architecture work.
- Empty scaffolding and agent personas stay documented as unimplemented until an RFC says otherwise.

## Rationale

Git can reconstruct **order**. It cannot reconstruct **why** empty ports exist, why OpenRouter was chosen, or why validation does not block propagation. A written RFC + issue is the minimum artifact that can capture maintainer knowledge going forward.

## Alternatives

Continuing with implementation-only ADRs, which is what 0001–0005 already do.
