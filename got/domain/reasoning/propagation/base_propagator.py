"""Base contract for graph propagation domain services."""
from typing import List, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from got.domain.model.graph import Graph

__all__ = ["BasePropagator"]


class BasePropagator(Protocol):
    """Protocol for propagation services.

    Contract:
    - Input: graph, starting_node_ids
    - Invariants: no nodes/edges added or removed; deterministic; domain-only
    - Transformation: traverse graph from starting nodes and update node state (e.g. confidence) in place
    - Output: None (side-effect on graph)
    """

    def propagate(self, graph: "Graph", starting_node_ids: List[str]) -> None:
        """Propagate from the given starting nodes. Mutates graph in place.

        Args:
            graph: The reasoning graph (aggregate root).
            starting_node_ids: Node IDs from which propagation starts (e.g. observed facts, initial hypotheses).
        """
        ...