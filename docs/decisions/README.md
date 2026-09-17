# Architecture decision records

ADRs in this folder record decisions that can be **observed in the repository**. Motivations are taken from code comments or commits when present. Otherwise rationale is marked **unknown**.

Do not treat [../planning/](../planning/README.md) as ADRs.

## Index

| ID | Title | Status |
|----|-------|--------|
| [0001](0001-llm-interpreter-vs-deterministic-core.md) | LLM interprets; domain reasons | Accepted (implemented) |
| [0002](0002-layered-domain-application-api.md) | Domain / application / API packages | Accepted (implemented) |
| [0003](0003-openrouter-stdlib-http.md) | OpenRouter via stdlib HTTP | Accepted (implemented) |
| [0004](0004-in-memory-graph.md) | In-memory graph, no repository | Accepted (current) |
| [0005](0005-validation-does-not-block-propagation.md) | Validate then always propagate | Accepted (implemented) |

## Template

Copy [template.md](template.md) to `NNNN-short-title.md` with the next unused number.
