"""Orchestrator for graph propagation (Domain Service)."""
from typing import List

from got.domain.model.graph import Graph
from got.domain.reasoning.propagation.base_propagator import BasePropagator
from got.domain.reasoning.propagation.confidence_propagator import ConfidencePropagator


class PropagationService:
    """Single entry point for propagation. Composes one or more propagators."""

    def __init__(self, confidence_propagator: BasePropagator | None = None):
        self._confidence = confidence_propagator or ConfidencePropagator()

    def propagate_epistemic(self, graph: Graph, starting_node_ids: List[str]) -> None:
        """Propagate confidence along epistemic edges from the given nodes. Mutates graph in place."""
        self._confidence.propagate(graph, starting_node_ids)