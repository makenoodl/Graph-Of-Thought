"""Connectivity analysis for the reasoning graph.

This module is part of the Structural Reasoning Engine (Phase 2). It examines
the graph's connectivity structure:
- Connected components (disjoint subgraphs)
- Articulation points (critical nodes)
- Cycles (undirected paths that start and end at the same node)

It helps understand whether reasoning is fragmented or well-integrated.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import List, Set

from got.domain.model.graph import Graph


@dataclass
class ConnectivityResult:
    """Result of connectivity analysis."""
    components: List[Set[str]] = field(default_factory=list)
    component_count: int = 0
    largest_component_size: int = 0
    isolated_nodes: List[str] = field(default_factory=list)


class ConnectivityAnalyzer:
    """Analyzes the connectivity structure of the graph."""

    def analyze(self, graph: Graph) -> ConnectivityResult:
        """Computes connected components (undirected).
        
        Returns:
            ConnectivityResult with components, counts, isolated nodes
        """
        if graph.is_empty():
            return ConnectivityResult()

        visited: set[str] = set()
        components: list[set[str]] = []

        for node_id in graph.nodes:
            if node_id in visited:
                continue
            component = self._bfs_component(graph, node_id)
            visited |= component
            components.append(component)

        isolated = [nid for comp in components for nid in comp if len(comp) == 1]
        sizes = [len(c) for c in components]

        return ConnectivityResult(
            components=components,
            component_count=len(components),
            largest_component_size=max(sizes) if sizes else 0,
            isolated_nodes=isolated
        )

    def _bfs_component(self, graph: Graph, start_id: str) -> Set[str]:
        """BFS to find all nodes in the same connected component."""
        component: set[str] = set()
        queue: deque = deque([start_id])

        while queue:
            node_id = queue.popleft()
            if node_id in component:
                continue
            component.add(node_id)
            for neighbor in graph.get_neighbors(node_id):
                if neighbor not in component:
                    queue.append(neighbor)

        return component