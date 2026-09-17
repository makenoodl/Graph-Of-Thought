# Historical planning notes

These files are **phase planning notes** written before the current documentation set. They describe intended milestones, not a verified implementation snapshot.

Use [architecture/overview.md](../architecture/overview.md) as the source of truth. Treat statements in this folder as **planned or outdated** unless the same fact is confirmed in architecture or domain docs.

| File | Original role | Status relative to code |
|------|---------------|-------------------------|
| [overview.md](overview.md) | Vision and phase checklist | Vision still valid. “Phase 1 complete” overstates test coverage. Persistence is not implemented. |
| [foundation.md](foundation.md) | Domain core plan | Mostly implemented. `MergeNodes` is an empty file. `GraphUpdated` is defined but not emitted by ops. |
| [reasoning.md](reasoning.md) | Structural engine plan | Modules exist. Causal propagator updates confidence; it does not add inferred causal edges. |
| [semantic.md](semantic.md) | Ports + hybrid structuring | Ports and `got/infrastructure/structuring/` are empty. Live path is `StructureTextServiceLLM` + OpenRouter. |
| [application.md](application.md) | Application-layer plan | `ExecuteReasoningService`, `CreateGraphFromText`, and `AnalyzeReasoning` exist. `EnrichGraphService` and `QueryGraphService` do not. |
| [infrastructure.md](infrastructure.md) | Copy of the application plan | Filename does not match contents. `got/infrastructure/` is unused scaffolding. |
| [objective.md](objective.md) | Agent memory / design intent | Design intent still useful. Persistence across sessions is **not** implemented. |

Do not implement features solely because they appear in this folder.

Verified git timeline and unanswered historical questions: [../rfcs/0001-rfc-adr-process-and-historical-motivations.md](../rfcs/0001-rfc-adr-process-and-historical-motivations.md).
