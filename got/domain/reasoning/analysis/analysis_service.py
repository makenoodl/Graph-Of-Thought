"""Orchestrator for graph analysis (Domain Service)."""
from dataclasses import dataclass, field
from typing import List, Optional

from got.domain.model.graph import Graph
from got.domain.reasoning.analysis.contradiction_detector import (
    ContradictionDetector,
    ContradictionCluster,
)
from got.domain.reasoning.analysis.connectivity import (
    ConnectivityAnalyzer,
    ConnectivityResult,
)
from got.domain.reasoning.analysis.critical_paths import (
    CriticalPathAnalyzer,
    CriticalPathsResult,
)


@dataclass
class AnalysisResult:
    """Aggregated result of full graph analysis."""
    contradiction_clusters: List[ContradictionCluster] = field(default_factory=list)
    connectivity: Optional[ConnectivityResult] = None
    critical_paths: dict[str, CriticalPathsResult] = field(default_factory=dict)


class AnalysisService:
    """Coordinates all analysis modules.
    
    Provides a single entry point for graph analysis.
    """

    def __init__(
        self,
        contradiction_detector: Optional[ContradictionDetector] = None,
        connectivity_analyzer: Optional[ConnectivityAnalyzer] = None,
        critical_path_analyzer: Optional[CriticalPathAnalyzer] = None,
    ):
        self._contradiction = contradiction_detector or ContradictionDetector()
        self._connectivity = connectivity_analyzer or ConnectivityAnalyzer()
        self._critical_paths = critical_path_analyzer or CriticalPathAnalyzer()

    def analyze(self, graph: Graph) -> AnalysisResult:
        """Runs full analysis on the graph.
        
        Returns:
            AnalysisResult with contradictions, connectivity, and critical paths
        """
        return AnalysisResult(
            contradiction_clusters=self._contradiction.detect(graph),
            connectivity=self._connectivity.analyze(graph),
            critical_paths={},  # Populated per-target if needed
        )

    def analyze_contradictions(self, graph: Graph) -> List[ContradictionCluster]:
        """Analyzes contradictions only."""
        return self._contradiction.detect(graph)

    def analyze_connectivity(self, graph: Graph) -> ConnectivityResult:
        """Analyzes connectivity only."""
        return self._connectivity.analyze(graph)

    def analyze_critical_paths(
        self, graph: Graph, target_node_ids: Optional[List[str]] = None
    ) -> dict[str, CriticalPathsResult]:
        """Analyzes support paths for target node(s).
        
        If target_node_ids is None, uses all nodes as targets.
        """
        if target_node_ids is None:
            target_node_ids = list(graph.nodes.keys())
        return {
            tid: self._critical_paths.analyze(graph, tid)
            for tid in target_node_ids
            if graph.has_node(tid)
        }