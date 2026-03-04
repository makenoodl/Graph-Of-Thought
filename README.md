# Graph-of-Thought Reasoning Engine
## A Deterministic Structural Core for LLM-Centric Cognitive Systems

Most LLM reasoning approaches (Chain-of-Thought, Tree-of-Thought, prompt-based Graph-of-Thought) treat reasoning as a sequence of tokens or a tree of generated text.

These approaches remain:

- **Opaque** — reasoning is not a first-class computational object
- **Ephemeral** — reasoning disappears after generation
- **Difficult to audit** — intermediate reasoning steps cannot be structurally inspected
- **Difficult to test deterministically** — reasoning cannot easily be validated as system state 

This project takes the opposite approach.

> [!IMPORTANT]
> Reasoning should be represented as a persistent, typed, and manipulable graph — not a transient stream of tokens.

# Overview

The Graph-of-Thought (GoT) Reasoning Engine externalizes reasoning as an explicit graph-structured cognitive state, composed of conceptual nodes and typed relational edges.

Within this framework:

- nodes represent units of thought (facts, hypotheses, goals, constraints, concepts)
- edges represent semantic relationships (support, contradiction, causality, structural relations, temporal relations)

- confidence values propagate through the graph to represent epistemic belief

A _deterministic reasoning_ engine then operates on this graph to perform:
- structural validation
- belief propagation
- contradiction detection
- graph-level reasoning analysis

> [!IMPORTANT]
> The reasoning engine itself is fully deterministic.
Language models are only used to transform natural language into a structured graph representation.

# Motivation

Large Language Models have recently demonstrated strong reasoning abilities through prompting techniques such as:
- Chain-of-Thought
- Tree-of-Thought
- prompt-based Graph-of-Thought
However, these approaches still represent reasoning as generated text.
This leads to several limitations:
- reasoning cannot easily be **verified**
- reasoning cannot be **reused across reasoning steps**
- reasoning cannot be treated as **a structured computational object**

Graph-of-Thought explores a different paradigm:

> Reasoning should be represented as structured state, not just generated language.

# Approach
The system separates two distinct computational roles:
```
LLMs → semantic interpretation
Graph engine → deterministic reasoning
```

The architecture follows a two-stage process:

**1. Semantic Interpretation**
Natural language reasoning is interpreted by a language model and converted into a structured graph specification.

**2. Deterministic Reasoning**
Once constructed, the reasoning graph becomes the central object of computation.
Deterministic algorithms then operate on the graph to:
- validate reasoning structure
- propagate epistemic confidence
- detect contradictions
- analyze reasoning paths.

>[!TIP]
>Treating reasoning as a graph data structure allows reasoning to be inspected, debugged, and extended programmatical

# Installation
This project uses uv for dependency management, but you can also use plain pip.
## With uv (recommended)
```python 
# 1) Create and activate a virtual environment
uv venv .venv
source .venv/bin/activate  # macOS / Linux
# On Windows:
# .venv\Scripts\activate

# 2) Install dependencies from pyproject / lockfile
uv sync

```
Then you can run the API or examples:

```python
# FastAPI app (dev)
uv run uvicorn got.api.app:app --reload

# Example sandbox
uv run python examples/simple_sandbox.py
```
### With plain pip

```python
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

pip install -e .
```

You also need an OpenRouter API key (used by the LLM structuring service).
Set it via environment variable or `.env` (loaded by the FastAPI app):
```bash
export OPENROUTER_API_KEY=your_key_here
```

# Getting Started
There are two main ways to use the engine:
As an HTTP API (send text, receive graph + analysis)
As a Python library (manipulate graphs directly in-process)
1. HTTP API: `/analyze-text`
```bash
uv run uvicorn got.api.app:app --reload
```
Then call: 
```bash
curl -X POST http://localhost:8000/analyze-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "We want to increase B2B revenue by 30% next year. \
             Options: raise prices, expand to new segments, or improve conversion. \
             We have strong evidence that current SMB pricing is already at its ceiling."
  }' | jq

```
