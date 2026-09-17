> Historical planning note. Implementation truth: [architecture/overview.md](../architecture/overview.md). Persistence is not implemented.

# Graph-of-Thought Reasoning Engine

## Vision

This project explores **Reasoning by Structure**:  
reasoning is not a sequence of tokens, but a **persistent, inspectable graph of relations**.

LLMs are used as **interpreters**, not as autonomous thinkers.

The core hypothesis:
> Reasoning should persist, evolve, and be revisable as a first-class cognitive object.

---

## Problem

Current LLM-based reasoning (CoT, ToT):
- is linear
- ephemeral
- non-inspectable
- non-reusable

Even advanced prompting techniques optimize **answer quality**, not **reasoning representation**.

---

## Solution

A **Graph-of-Thought (GoT)** engine where:
- Nodes = concepts, hypotheses, facts, constraints
- Edges = typed semantic relations (causal, epistemic, support, contradiction)
- Graph = persistent cognitive structure

---

## Design Principles

- Graph-native cognition
- Persistent reasoning
- Human-interpretable structures
- Strict separation:
  - linguistic interpretation (LLM)
  - structural reasoning (domain core)

---

## Status (planning snapshot)

- Phase 1 (Domain Core): marked complete in this note
- MVP goal: Text → Graph → Persisted Reasoning

Verified later: the domain core exists; graphs are in-memory per process/request, not persisted.
