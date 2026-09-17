> Historical agent-memory note. Engineering contract: [AGENTS.md](../../AGENTS.md). Persistence across sessions is not implemented.

# Graph-of-Thought — Agent Objective (Cursor Memory)

## Purpose

The Graph-of-Thought (GoT) system exists to **externalize human reasoning into an explicit graph structure**.

The primary output of this system is **a graph**, not text.

Text is only an input/output interface.

---

## What This Agent Must Do

When interacting with this project, the agent must:

- Treat reasoning as a **persistent graph of nodes and typed edges**
- Prefer **structural changes to the graph** over generating explanations
- Assume reasoning **must be stored, updated, and validated**
- Never treat reasoning as disposable text

---

## What This Agent Must NOT Do

- Do NOT optimize for “better answers”
- Do NOT rely on Chain-of-Thought or hidden reasoning
- Do NOT collapse reasoning back into linear text
- Do NOT treat LLM output as ground truth

LLMs are **interpreters**, not reasoners.

---

## Mental Model to Use

- Nodes = concepts, hypotheses, facts, constraints
- Edges = causal, epistemic, support, contradiction, dependency
- The graph = the reasoning state

If something “changes in thinking”, it must appear as a **graph mutation**.

---

## Design Rules

- Reasoning must be **inspectable**
- Reasoning must be **revisable**
- Reasoning must be **auditable**
- Reasoning must be **persistent across sessions**

If reasoning is not represented in the graph, it does not exist.

---

## Separation of Concerns

- Language = interpretation layer
- Graph = cognition layer
- Validation = deterministic, non-LLM

Never mix these responsibilities.

---

## Goal Reminder

This project is not a chatbot.

It is a **graph-native cognitive system**.

Act accordingly.
