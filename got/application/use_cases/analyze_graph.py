"""Use case: analyze a graph (contradictions, connectivity, critical paths)."""
from typing import Optional

from got.domain.model.graph import Graph
from got.domain.reasoning.analysis import AnalysisService
from got.domain.reasoning.analysis.analysis_service import AnalysisResult


class AnalyzeGraphUseCase:
    """Use case for analyzing a graph."""

    def __init__(self, analysis_service: Optional[AnalysisService] = None):
        self._analysis_service = analysis_service or AnalysisService()

    def execute(self, graph: Graph) -> AnalysisResult:
        """Execute the use case."""
        return self._analysis_service.analyze(graph)