# Graph-of-Thought Reasoning Engine
## A Deterministic Structural Core for LLM-Centric Cognitive Systems

Most LLM reasoning approaches (Chain-of-Thought, Tree-of-Thought, prompt-based Graph-of-Thought) treat reasoning as a sequence of tokens or a tree of generated text.

These approaches remain:
- Opaque (reasoning is not a first-class object)-
- Ephemeral (no persistent cognitive state)
- Difficult to audit
- Difficult to test deterministically

This project takes the opposite approach:

Reasoning should be a persistent, typed, and manipulable graph — not a stream of tokens.

The Graph-of-Thought (GoT) Reasoning Engine is designed to externalize reasoning as an explicit graph-structured cognitive state, composed of conceptual nodes and typed relational edges.
