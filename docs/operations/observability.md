# Observability

Production-grade logging, metrics, and tracing are **not implemented**. This page describes what exists and what does not.

## Domain events

Ops return event dataclasses (`NodeCreated`, `EdgeAdded`, …). Validators attach `CycleDetected` and `ContradictionDetected` to `ValidationResult.events`.

`Validator` and `BaseValidator` accept an optional `event_handler` callback. The API and `ExecuteReasoningService` do not pass one. Events are not written to disk or a bus.

`GraphUpdated` has no producer on the live path.

Proposed (not implemented): an in-process event journal, `run_id`, replay, and graph diff — [RFC 0002](../rfcs/0002-sequenced-runtime-roadmap.md) Wave 1. Without that journal there is no process reward and no Adaptive GoT debug.

## HTTP

FastAPI default error responses only. `analyze_text` does not log. OpenRouter failures become unhandled `OpenRouterError` / `ValueError` (typically HTTP 500).

## Metrics

No counters, histograms, or health endpoint. Graph size and violation counts exist only as in-memory fields on `Graph` and `ValidationResult.get_summary()`.

The HTTP response includes `contradiction_count` derived from analysis clusters, not from `ValidationResult`.

## Cursor observability persona

`.cursor/rules/observability-agent.mdc` describes an intended read-only observability agent. It is editor guidance, not a running component.

## Practical debugging

- Library: print `ValidationResult` and `AnalyzeReasoningResult` as in `examples/simple_sandbox.py`.
- HTTP: FastAPI `/docs` and response JSON (`graph` + `analysis`).
- LLM: inspect `OpenRouterError` payloads (HTTP body is included in the exception message).
