"""Orchestrator for graph propagation (Domain Service)."""
from typing import List

from got.domain.model.graph import Graph
from got.domain.reasoning.propagation.base_propagator import BasePropagator
from got.domain.reasoning.propagation.causal_propagator import CausalPropagator
from got.domain.reasoning.propagation.epistemic_propagator import EpistemicPropagator


class PropagationService:
    def __init__(self, epistemic_propagator=None, causal_propagator=None):
        self._epistemic = epistemic_propagator or EpistemicPropagator()
        self._causal = causal_propagator or CausalPropagator()

    def propagate_epistemic(self, graph, starting_node_ids):
        self._epistemic.propagate(graph, starting_node_ids)

    def propagate_causal(self, graph, starting_node_ids):
        self._causal.propagate(graph, starting_node_ids)

    def propagate_all(self, graph, starting_node_ids):
        self.propagate_epistemic(graph, starting_node_ids)
        self.propagate_causal(graph, starting_node_ids)