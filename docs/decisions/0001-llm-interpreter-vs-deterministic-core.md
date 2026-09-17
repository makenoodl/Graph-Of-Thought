# ADR 0001: LLM interprets; domain reasons

**Status:** Accepted (implemented)  
**Date:** unknown (present in README and package split)  
**Code:** `got/application/services/structure_text_service_llm.py`, `got/domain/reasoning/`

## Context

LLM chain-of-thought is opaque and hard to test. This project needs a reasoning artifact that can be validated deterministically.

## Decision

Use a language model only to map natural language to `GraphSpecDTO`. All validation, confidence propagation, and analysis run in `got/domain/reasoning` with no LLM imports. OpenRouter calls use `temperature=0.0`.

## Consequences

- HTTP `POST /analyze-text` cannot run without `OPENROUTER_API_KEY`.
- The library path (`examples/simple_sandbox.py`, tests) can reason without an LLM.
- LLM JSON must be sanitized and schema-validated before it touches `Graph`.
- Structural engine changes must stay free of I/O.

## Rationale

Stated in `README.md` and `got/domain/reasoning/README.md`: the engine is deterministic and non-LLM; models transform language into structure.

## Alternatives

Empty files `got/infrastructure/structuring/rule_based.py` and `llm_based.py` suggest a planned hybrid structurer. They are not implemented. Optional extras `openai` and `transformers` are unused.
