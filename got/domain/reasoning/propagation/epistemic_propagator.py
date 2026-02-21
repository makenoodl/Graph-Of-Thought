"""Propagates confidence along epistemic edges (Domain Service)."""
from collections import deque
from typing import List

from got.domain.model.graph import Graph
from got.domain.model.value_objects import Confidence, RelationType


# Relation types that strengthen the target's confidence
_STRENGTHENING = frozenset({
    RelationType.STRENGTHENS,
    RelationType.SUPPORTS,
    RelationType.EVIDENCE_FOR,
    RelationType.IMPLIES,
    RelationType.EXPLAINS,
})
# Relation types that weaken the target's confidence
_WEAKENING = frozenset({
    RelationType.WEAKENS,
    RelationType.EVIDENCE_AGAINST,
    RelationType.CONTRADICTS,
    RelationType.BLOCKS,
})

DEFAULT_FACTOR = 0.1


class EpistemicPropagator:
    """Propagates confidence from starting nodes along epistemic edges. Conforms to BasePropagator."""

    def __init__(self, factor: float = DEFAULT_FACTOR):
        self.factor = factor

    def propagate(self, graph: Graph, starting_node_ids: List[str]) -> None:
        """Propagate confidence from starting nodes. Mutates graph in place. Uses BFS on epistemic edges only."""
        if not starting_node_ids:
            return

        queue: deque = deque()
        visited: set = set()

        for nid in starting_node_ids:
            if graph.has_node(nid) and nid not in visited:
                queue.append(nid)
                visited.add(nid)

        while queue:
            node_id = queue.popleft()
            source = graph.get_node(node_id)
            if not source:
                continue

            for edge in graph.get_edges_from(node_id):
                if not edge.relation_type.is_epistemic():
                    continue
                target = graph.get_node(edge.target_id)
                if not target:
                    continue

                if edge.relation_type in _STRENGTHENING:
                    new_conf = target.confidence.strengthen(self.factor)
                elif edge.relation_type in _WEAKENING:
                    new_conf = target.confidence.weaken(self.factor)
                else:
                    continue

                target.update_confidence(new_conf)

                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append(edge.target_id)