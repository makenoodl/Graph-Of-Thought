# Configuration

There is no settings module, YAML config, or feature-flag system.

## Environment variables

| Variable | Required when | Read by | Default |
|----------|---------------|---------|---------|
| `OPENROUTER_API_KEY` | `POST /analyze-text` or any `OpenRouterClient.chat_json` call | `got/application/services/openrouter.py` via `os.getenv` | none — raises `OpenRouterError` |

`got/api/app.py` calls `load_dotenv()` at import time so a local `.env` is loaded for uvicorn. `.env` is gitignored.

CI sets `OPENROUTER_API_KEY=dummy` so the name exists; current tests do not use the client.

Do not document real key values. Do not commit `.env`.

## Hardcoded client defaults

`OpenRouterClient` dataclass fields (not env vars):

| Field | Default |
|-------|---------|
| `api_key_env` | `"OPENROUTER_API_KEY"` |
| `base_url` | `"https://openrouter.ai/api/v1/chat/completions"` |
| `model` | `"openai/gpt-4o-mini"` |
| `timeout_s` | `60` |
| `temperature` | `0.0` (method argument in `StructureTextServiceLLM`) |
| `max_tokens` | `1500` from the structurer (`chat_json` default is `1200`) |

Propagator `factor` defaults to `0.1` on `EpistemicPropagator` and `CausalPropagator`.

## Python versions

- `pyproject.toml`: `requires-python = ">=3.11"`
- `.python-version`: `3.13`
- CI `setup-python`: `3.11`

## Optional extras

`[project.optional-dependencies] llm` (`openai`, `transformers`) and `dev` (`pytest`, `ruff`) are declared. The running LLM path does not import those LLM libraries. uv also lists pytest/ruff under `[tool.uv] dev-dependencies`.
