"""Propagates confidence along causal edges (Domain Service)."""
from collections import deque
from typing import List

from got.domain.model.graph import Graph
from got.domain.model.value_objects import Confidence, RelationType

# Cause strengthens effect (A causes/enables/requires B → B gains confidence)
_STRENGTHENING = frozenset({
    RelationType.CAUSES,
    RelationType.REQUIRES,
    RelationType.DEPENDS_ON,
    RelationType.ENABLES,
})
# Cause weakens effect (A prevents B → B loses confidence)
_WEAKENING = frozenset({
    RelationType.PREVENTS,
})

DEFAULT_FACTOR = 0.1


class CausalPropagator:
    """Propagates confidence from starting nodes along causal edges. Conforms to BasePropagator."""

    def __init__(self, factor: float = DEFAULT_FACTOR):
        self.factor = factor

    def propagate(self, graph: Graph, starting_node_ids: List[str]) -> None:
        """Propagate along causal edges (cause → effect). Mutates graph in place. BFS on causal edges only."""
        if not starting_node_ids:
            return

        queue = deque()
        visited = set()

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
                if not edge.relation_type.is_causal():
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