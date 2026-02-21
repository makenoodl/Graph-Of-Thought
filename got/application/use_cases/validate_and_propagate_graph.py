"""Use case: validate graph then propagate (epistemic + optional causal)."""
from typing import List

from got.domain.model.graph import Graph
from got.domain.reasoning.validation import Validator
from got.domain.reasoning.validation.base_validator import ValidationResult
from got.domain.reasoning.propagation import PropagationService


class ValidateAndPropagateGraphUseCase:
    """Validates the graph then runs epistemic (and optionally causal) propagation."""

    def __init__(self, validator: Validator | None = None, propagation_service: PropagationService | None = None):
        self._validator = validator or Validator()
        self._propagation = propagation_service or PropagationService()

    def execute(
        self,
        graph: Graph,
        starting_node_ids: List[str],
        propagate_causal: bool = False,
    ) -> dict:
        """
        Returns:
            dict with keys: validation_result (ValidationResult), graph (same graph, mutated if propagation ran).
        """
        validation_result: ValidationResult = self._validator.validate(graph)
        if propagate_causal:
            self._propagation.propagate_all(graph, starting_node_ids)
        else:
            self._propagation.propagate_epistemic(graph, starting_node_ids)
        return {"validation_result": validation_result, "graph": graph}