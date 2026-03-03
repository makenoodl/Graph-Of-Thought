from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Dict, Any

from got.domain.model.graph import Graph
from got.domain.reasoning.validation.base_validator import ValidationResult
from got.domain.reasoning.analysis.analysis_service import AnalysisResult
from got.application.schemas.analysis import AnalysisSummaryDTO
from got.application.services.execute_reasoning import ExecuteReasoningService


@dataclass
class AnalyzeReasoningResult:
    """
    High-level result of a reasoning analysis use case.

    - graph: updated reasoning graph after propagation
    - validation: detailed validation result (violations, warnings, events)
    - analysis: raw structural analysis (contradiction clusters, connectivity, ...)
    - summary: compact, human-oriented summary (blocked_paths, viable_paths, recommendation)
    """

    graph: Graph
    validation: ValidationResult
    analysis: AnalysisResult | None
    summary: AnalysisSummaryDTO


class AnalyzeReasoningUseCase:
    """
    Application use case: run a full reasoning cycle on a graph
    and return both raw results and a high-level summary.

    This does not contain domain logic: it orchestrates application services
    and shapes the output for API/CLI/LLM consumers.
    """

    def __init__(self, executor: ExecuteReasoningService | None = None) -> None:
        self._executor = executor or ExecuteReasoningService()

    def execute(
        self,
        graph: Graph,
        starting_node_ids: Iterable[str],
        propagate_causal: bool = False,
    ) -> AnalyzeReasoningResult:
        """
        Run validation + propagation + analysis on the graph,
        then compute a compact summary.
        """
        result: Dict[str, Any] = self._executor.run(
            graph=graph,
            starting_node_ids=list(starting_node_ids),
            propagate_causal=propagate_causal,
            analyze=True,
        )

        updated_graph: Graph = result["graph"]
        validation: ValidationResult = result["validation"]
        analysis: AnalysisResult | None = result["analysis"]

        # For now, we derive a very simple summary from analysis.
        # You can later plug in critical paths, blocked paths, etc.
        contradiction_count = 0
        if analysis is not None:
            contradiction_count = len(analysis.contradiction_clusters)

        # TODO later: real computation of blocked_paths / viable_paths
        blocked_paths = 0
        viable_paths = 0

        summary = AnalysisSummaryDTO.simple_recommendation(
            blocked_paths=blocked_paths,
            viable_paths=viable_paths,
            contradiction_count=contradiction_count,
        )

        return AnalyzeReasoningResult(
            graph=updated_graph,
            validation=validation,
            analysis=analysis,
            summary=summary,
        )