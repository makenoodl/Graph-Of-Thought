# ADR 0003: OpenRouter via stdlib HTTP

**Status:** Accepted (implemented)  
**Date:** unknown  
**Code:** `got/application/services/openrouter.py`

## Context

Text-to-graph needs a chat-completions provider. `pyproject.toml` optional extra `llm` lists `openai` and `transformers`.

## Decision

`OpenRouterClient` calls `https://openrouter.ai/api/v1/chat/completions` with `urllib.request`. Default model is `openai/gpt-4o-mini`. API key from `OPENROUTER_API_KEY`. No SDK.

## Consequences

- Runtime LLM dependency is an API key plus stdlib HTTP, not the `openai` package.
- Errors are wrapped in `OpenRouterError`; the FastAPI route does not map them to specific status codes.
- Model name is a dataclass field default, not an environment variable.

## Rationale

**Unknown** beyond the class docstring (“Minimal OpenRouter client (HTTP only)”).

## Alternatives

- Optional dependency `openai>=1.0` is declared and unused.
- `got/infrastructure/llm/openai_client.py` is empty.
