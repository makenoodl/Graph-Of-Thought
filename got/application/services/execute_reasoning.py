from __future__ import annotations

from typing import Iterable, Optional, Dict, Any

from got.domain.model.graph import Graph
from got.domain.reasoning.validation.base_validator import ValidationResult
from got.domain.reasoning.analysis.analysis_service import AnalysisResult
from got.application.use_cases.validate_and_propagate_graph import (
    ValidateAndPropagateGraphUseCase,
)
from got.application.use_cases.analyze_graph import AnalyzeGraphUseCase


class ExecuteReasoningService:
    """
    High-level application service that runs a full reasoning cycle on a graph:

    1) validate the graph (multi-layer validators)
    2) propagate confidence (epistemic and optionally causal)
    3) analyze the resulting graph (contradictions, connectivity, paths)

    This service does NOT contain domain logic itself: it orchestrates
    domain services / use cases.
    """

    def __init__(
        self,
        validate_and_propagate_uc: Optional[ValidateAndPropagateGraphUseCase] = None,
        analyze_uc: Optional[AnalyzeGraphUseCase] = None,
    ) -> None:
        self._validate_and_propagate = (
            validate_and_propagate_uc or ValidateAndPropagateGraphUseCase()
        )
        self._analyze = analyze_uc or AnalyzeGraphUseCase()

    def run(
        self,
        graph: Graph,
        starting_node_ids: Iterable[str],
        propagate_causal: bool = False,
        analyze: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute the full reasoning pipeline on the given graph.

        Args:
            graph: Domain graph to reason on (will be mutated by propagation).
            starting_node_ids: Node IDs from which to start propagation.
            propagate_causal: If True, run both epistemic + causal propagation.
                              If False, run epistemic only.
            analyze: If True, run structural analysis after propagation.

        Returns:
            dict with:
                - "graph": updated Graph
                - "validation": ValidationResult
                - "analysis": AnalysisResult | None
        """
        # 1) Validate + propagate
        vp_result = self._validate_and_propagate.execute(
            graph=graph,
            starting_node_ids=list(starting_node_ids),
            propagate_causal=propagate_causal,
        )

        updated_graph: Graph = vp_result["graph"]
        validation_result: ValidationResult = vp_result["validation_result"]

        # 2) Analyze
        analysis_result: AnalysisResult | None = None
        if analyze:
            analysis_result = self._analyze.execute(updated_graph)

        # 3) Aggregate output
        return {
            "graph": updated_graph,
            "validation": validation_result,
            "analysis": analysis_result,
        }