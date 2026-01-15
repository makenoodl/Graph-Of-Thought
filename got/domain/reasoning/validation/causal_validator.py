"""Validator for causal relations (cause-effect relationships)."""
from typing import List, Dict, Optional, Tuple
from got.domain.model.graph import Graph
from got.domain.model.edge import Edge
from got.domain.model.value_objects import RelationType
from got.domain.reasoning.validation.base_validator import BaseValidator, ValidationResult
from got.domain.events.cycle_detected import CycleDetected


class CausalValidator(BaseValidator):
    """Validates causal relations.
    
    Detects:
    - Causal cycles (problematic circular dependencies)
    - Temporal inconsistencies (A CAUSES B but A FOLLOWS B)
    
    DDD Principles:
    - Pure domain logic (algorithms are deterministic)
    - Uses domain model (Graph, Edge, RelationType)
    - Emits domain events (CycleDetected)
    - No external dependencies
    """
    
    def get_layer(self) -> str:
        return "causal"
    
    def validate(self, graph: Graph) -> ValidationResult:
        """Validates the causal layer."""
        result = ValidationResult()
        
        # 1. Detect causal cycles
        cycles = self._detect_causal_cycles(graph)
        for cycle in cycles:
            message = f"Cycle causal détecté: {' → '.join(cycle)}"
            event = CycleDetected(  # ← CycleDetected utilisé ici !
                layer="causal",
                cycle_path=cycle,
                cycle_type="causal"
            )
            result.add_warning(message, event)  # Warning, not error (cycles can be valid)
            self._emit_event(event)  # ← Émet l'événement
        
        # 2. Check temporal consistency
        temporal_conflicts = self._check_temporal_consistency(graph)
        for conflict in temporal_conflicts:
            result.add_warning(conflict["message"])
        
        return result
    
    def _detect_causal_cycles(self, graph: Graph) -> List[List[str]]:
        """
        Detects cycles in the causal graph.
        
        Algorithm: DFS with coloring (WHITE/GRAY/BLACK)
        - WHITE (0): Not visited
        - GRAY (1): Currently being visited (in recursion stack)
        - BLACK (2): Completely visited
        
        Complexity: O(V + E) where V = nodes, E = edges
        
        Returns:
            List of cycles (each cycle = list of node IDs)
        """
        causal_edges = graph.get_causal_edges()
        if not causal_edges:
            return []
        
        # Build directed graph adjacency list
        adjacency: Dict[str, List[str]] = {}
        for edge in causal_edges:
            if edge.source_id not in adjacency:
                adjacency[edge.source_id] = []
            adjacency[edge.source_id].append(edge.target_id)
        
        # States: WHITE=0, GRAY=1, BLACK=2
        color: Dict[str, int] = {node_id: 0 for node_id in graph.nodes.keys()}
        parent: Dict[str, Optional[str]] = {node_id: None for node_id in graph.nodes.keys()}
        cycles: List[List[str]] = []
        
        def dfs(node_id: str) -> None:
            """DFS with cycle detection."""
            color[node_id] = 1  # GRAY
            
            if node_id in adjacency:
                for neighbor in adjacency[node_id]:
                    if color[neighbor] == 0:  # WHITE
                        parent[neighbor] = node_id
                        dfs(neighbor)
                    elif color[neighbor] == 1:  # GRAY → Cycle detected!
                        # Reconstruct the cycle
                        cycle = self._reconstruct_cycle(node_id, neighbor, parent)
                        cycles.append(cycle)
            
            color[node_id] = 2  # BLACK
        
        # Traverse all nodes (for disconnected graphs)
        for node_id in graph.nodes.keys():
            if color[node_id] == 0:
                dfs(node_id)
        
        return cycles
    
    def _reconstruct_cycle(
        self, 
        start: str, 
        end: str, 
        parent: Dict[str, Optional[str]]
    ) -> List[str]:
        """Reconstructs the cycle from start to end."""
        cycle = [end]
        current = start
        visited_in_path = {end}
        
        while current != end and current is not None:
            if current in visited_in_path:
                # Prevent infinite loops
                break
            cycle.append(current)
            visited_in_path.add(current)
            current = parent.get(current)
        
        cycle.append(end)  # Close the cycle
        return cycle[::-1]  # Reverse to get correct order
    
    def _check_temporal_consistency(self, graph: Graph) -> List[Dict[str, str]]:
        """
        Checks temporal consistency.
        
        If A CAUSES B, then A cannot FOLLOWS B (temporal inconsistency).
        
        Returns:
            List of conflict dictionaries with "message" key
        """
        conflicts = []
        causal_edges = graph.get_causal_edges()
        temporal_edges = graph.get_temporal_edges()
        
        if not causal_edges or not temporal_edges:
            return conflicts
        
        # Index temporal relations
        temporal_map: Dict[Tuple[str, str], RelationType] = {}
        for edge in temporal_edges:
            temporal_map[(edge.source_id, edge.target_id)] = edge.relation_type
        
        # Check each causal edge for temporal conflicts
        for causal_edge in causal_edges:
            pair = (causal_edge.source_id, causal_edge.target_id)
            if pair in temporal_map:
                temporal_rel = temporal_map[pair]
                if temporal_rel == RelationType.FOLLOWS:
                    conflicts.append({
                        "message": (
                            f"Conflit temporel: {causal_edge.source_id} CAUSES "
                            f"{causal_edge.target_id} mais FOLLOWS aussi. "
                            f"Si A cause B, A doit précéder B temporellement."
                        )
                    })
        
        return conflicts