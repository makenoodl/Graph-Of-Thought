> Historical planning note. Implementation truth: [architecture/execution-flow.md](../architecture/execution-flow.md). Ports and infrastructure structuring modules are empty files.

# Phase 3 — Semantic Structuring (LLM Layer)

## Objective

Transform **unstructured text → structured reasoning graph**.

LLMs act as:
> linguistic interpreters, not reasoners.

---

## Ports (Interfaces)

Path: `got/domain/ports/`

- Structurer
- LLMInterpreter
- GraphRepo

These define the **contract**, not the implementation.

Verified later: `got/domain/ports/*.py` are empty. No runtime code depends on them.

---

## Implementations

### Rule-based Structuring

Path: `got/infrastructure/structuring/rule_based.py`

- Regex & linguistic heuristics
- Deterministic
- Used for:
  - Baseline
  - Tests
  - Validation

Verified later: the file is empty.

---

### LLM-based Structuring

Path: `got/infrastructure/structuring/llm_based.py`

Responsibilities:
- Prompt design
- Output parsing
- Validation against domain rules
- Error / hallucination handling

Verified later: the live implementation is `got/application/services/structure_text_service_llm.py` calling `OpenRouterClient`.

---

## Hybrid Strategy

- Rules for structure guarantees
- LLM for semantic richness
- Confidence assigned to LLM-derived edges

Verified later: hybrid rule+LLM structuring is not implemented. LLM JSON is sanitized for unknown enums, then validated by `GraphSpecDTO`.

---

## Outcome

Text becomes a **candidate cognitive structure**, validated by the domain.
