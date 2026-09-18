---
title: Graph of Thought
emoji: 🕸️
colorFrom: indigo
colorTo: purple
sdk: static
pinned: false
short_description: Typed graph engine — validate, propagate, no LLM
tags:
  - graph
  - reasoning
  - evaluation
---

# Graph-of-Thought (deterministic sandbox)

In-memory typed reasoning graph: **validation**, **confidence propagation**, **contradiction analysis**. This Space does **not** call a language model.

This Hub page is a **static** snapshot of two v0.1 engine runs. Hugging Face now requires [PRO](https://huggingface.co/pro) to host Gradio Spaces on compute. The live Python UI is still in the git repo (`spaces/hf-demo/app.py`) for local use.

The LLM path in the library (`POST /analyze-text` via OpenRouter) is optional and is not used here. See [ADR 0001](https://github.com/makenoodl/Graph-Of-Thought/blob/main/docs/decisions/0001-llm-interpreter-vs-deterministic-core.md).

## What this is / is not

- **Is:** a v0.1 engine demo. Graph lives for one run. `blocked_paths` and `viable_paths` are always `0`.
- **Is not:** Adaptive Graph of Thoughts, test-time compute, persistent memory, or a Hub `from_pretrained` model library.

## Related papers

- [Graph of Thoughts (Besta et al., 2308.09687)](https://huggingface.co/papers/2308.09687)
- [Adaptive Graph of Thoughts (2502.05078)](https://huggingface.co/papers/2502.05078)
- [KGoT (2504.02670)](https://huggingface.co/papers/2504.02670)

## Source

GitHub: [makenoodl/Graph-Of-Thought](https://github.com/makenoodl/Graph-Of-Thought)

Publish (Hub **Write** token):

```bash
hf auth login
uv run --with huggingface_hub python spaces/hf-demo/publish.py
```
