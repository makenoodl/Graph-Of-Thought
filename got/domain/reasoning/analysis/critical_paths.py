
"""Critical reasoning paths - support chains for a target node.

This module is part of the Structural Reasoning Engine (Phase 2). It extracts
the key support paths for a target node (e.g. a conclusion).

It helps understand why the system considers a claim justified.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import List

from got.domain.model.graph import Graph
from got.domain.model.value_objects import RelationType


# Relation types that support the target (source supports target)
_SUPPORTING = frozenset({
    RelationType.SUPPORTS,
    RelationType.EVIDENCE_FOR,
    RelationType.STRENGTHENS,
    RelationType.EXPLAINS,
    RelationType.IMPLIES,
})


@dataclass
class SupportPath:
    """A path of supporting relations leading to a target node."""
    node_ids: List[str] = field(default_factory=list)
    edge_types: List[str] = field(default_factory=list)


@dataclass
class CriticalPathsResult:
    """Result of critical path analysis for a target node."""
    target_node_id: str
    paths: List[SupportPath] = field(default_factory=list)
    supporting_node_ids: set = field(default_factory=set)


class CriticalPathAnalyzer:
    """Extracts support paths for a given target node."""

    def analyze(self, graph: Graph, target_node_id: str) -> CriticalPathsResult:
        """Finds all support paths leading to the target node.
        
        Uses reverse BFS: from target, follow incoming SUPPORT/EVIDENCE_FOR edges.
        
        Args:
            graph: Graph to analyze
            target_node_id: Node to find support for
            
        Returns:
            CriticalPathsResult with paths and supporting nodes
        """
        if not graph.has_node(target_node_id):
            return CriticalPathsResult(target_node_id=target_node_id)

        paths: list[SupportPath] = []
        supporting: set[str] = set()
        queue: deque[tuple[str, SupportPath]] = deque([(target_node_id, SupportPath(node_ids=[target_node_id]))])
        visited_paths: set[tuple[str, ...]] = set()

        while queue:
            node_id, path_so_far = queue.popleft()
            path_key = tuple(path_so_far.node_ids)
            if path_key in visited_paths:
                continue
            visited_paths.add(path_key)

            for edge in graph.get_edges_to(node_id):
                if edge.relation_type not in _SUPPORTING:
                    continue
                source_id = edge.source_id
                supporting.add(source_id)

                new_path = SupportPath(
                    node_ids=[source_id] + path_so_far.node_ids,
                    edge_types=[edge.relation_type.value] + path_so_far.edge_types
                )
                paths.append(new_path)
                if source_id not in path_so_far.node_ids:  # Avoid cycles
                    queue.append((source_id, new_path))

        if not paths:
            paths = [SupportPath(node_ids=[target_node_id])]

        return CriticalPathsResult(
            target_node_id=target_node_id,
            paths=paths,
            supporting_node_ids=supporting
        )