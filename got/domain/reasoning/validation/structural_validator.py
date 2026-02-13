"""Validator for structural relations (composition, hierarchy, type relationships)."""
from typing import List, Dict, Set, Tuple, Optional
from got.domain.model.graph import Graph
from got.domain.model.edge import Edge
from got.domain.model.value_objects import RelationType
from got.domain.reasoning.validation.base_validator import BaseValidator, ValidationResult
from got.domain.events.cycle_detected import CycleDetected


class StructuralValidator(BaseValidator):
    """Validates structural relations.
    
    Detects:
    - Hierarchical cycles (A PART_OF B, B PART_OF C, C PART_OF A)
    - Anti-symmetry violations (A CONTAINS B and B CONTAINS A)
    - Transitivity violations (A CONTAINS B, B CONTAINS C, but A doesn't contain C)
    - Missing inverse relations (A CONTAINS B but no B PART_OF A)
    - Type hierarchy inconsistencies (A INSTANCE_OF B and B INSTANCE_OF A)
    - SIMILAR_TO asymmetry (A SIMILAR_TO B but no B SIMILAR_TO A)
    
    DDD Principles:
    - Pure domain logic (algorithms are deterministic)
    - Uses domain model (Graph, Edge, RelationType)
    - Emits domain events (CycleDetected)
    - No external dependencies
    """
    
    def get_layer(self) -> str:
        """Returns the layer this validator validates."""
        return "structural"
    
    def validate(self, graph: Graph) -> ValidationResult:
        """Validates the structural layer.
        
        Pipeline:
        1. Retrieve all structural edges
        2. Detect hierarchical cycles → violations
        3. Detect anti-symmetry violations → violations
        4. Detect transitivity violations → warnings
        5. Detect missing inverse relations → warnings
        6. Detect type hierarchy inconsistencies → violations
        7. Detect SIMILAR_TO asymmetry → warnings
        8. Return ValidationResult with all issues
        
        Args:
            graph: Graph to validate
            
        Returns:
            ValidationResult with violations, warnings, and events
        """
        result = ValidationResult()
        
        # STEP 1: Detect hierarchical cycles (violations)
        cycles = self._detect_hierarchical_cycles(graph)
        for cycle in cycles:
            message = f"Hierarchical cycle detected: {' → '.join(cycle)}"
            event = CycleDetected(
                layer="structural",
                cycle_path=cycle,
                cycle_type="hierarchical"
            )
            result.add_violation(message, event)
            self._emit_event(event)
        
        # STEP 2: Detect anti-symmetry violations (violations)
        anti_symmetry_violations = self._detect_anti_symmetry_violations(graph)
        for violation in anti_symmetry_violations:
            result.add_violation(violation['message'])
        
        # STEP 3: Detect transitivity violations (warnings)
        transitivity_violations = self._detect_transitivity_violations(graph)
        for violation in transitivity_violations:
            result.add_warning(violation['message'])
        
        # STEP 4: Detect missing inverse relations (warnings)
        missing_inverses = self._detect_missing_inverses(graph)
        for missing in missing_inverses:
            result.add_warning(missing['message'])
        
        # STEP 5: Detect type hierarchy inconsistencies (violations)
        type_inconsistencies = self._detect_type_inconsistencies(graph)
        for inconsistency in type_inconsistencies:
            result.add_violation(inconsistency['message'])
        
        # STEP 6: Detect SIMILAR_TO asymmetry (warnings)
        similarity_asymmetry = self._detect_similarity_asymmetry(graph)
        for asymmetry in similarity_asymmetry:
            result.add_warning(asymmetry['message'])
        
        return result
    
    def _detect_hierarchical_cycles(self, graph: Graph) -> List[List[str]]:
        """Detects cycles in hierarchical relations (PART_OF, CONTAINS, INSTANCE_OF, TYPE_OF).
        
        Reasoning:
        - Hierarchical relations should form a DAG (Directed Acyclic Graph)
        - Cycles indicate logical inconsistencies
        - Example: A PART_OF B, B PART_OF C, C PART_OF A → cycle
        
        Algorithm:
        - Use DFS with coloring (similar to CausalValidator)
        - Build adjacency list for hierarchical edges
        - Detect back edges (GRAY nodes) → cycles
        
        Args:
            graph: Graph to analyze
            
        Returns:
            List of cycles (each cycle = list of node IDs)
        """
        structural_edges = graph.get_structural_edges()
        if not structural_edges:
            return []
        
        # Build adjacency list for hierarchical relations
        # PART_OF, CONTAINS, INSTANCE_OF, TYPE_OF form hierarchies
        hierarchical_relations = {
            RelationType.PART_OF,
            RelationType.CONTAINS,
            RelationType.INSTANCE_OF,
            RelationType.TYPE_OF
        }
        
        adjacency: Dict[str, List[str]] = {}
        for edge in structural_edges:
            if edge.relation_type in hierarchical_relations:
                if edge.source_id not in adjacency:
                    adjacency[edge.source_id] = []
                adjacency[edge.source_id].append(edge.target_id)
        
        if not adjacency:
            return []
        
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
                break
            cycle.append(current)
            visited_in_path.add(current)
            current = parent.get(current)
        
        cycle.append(end)  # Close the cycle
        return cycle[::-1]  # Reverse to get correct order
    
    def _detect_anti_symmetry_violations(self, graph: Graph) -> List[Dict[str, str]]:
        """Detects anti-symmetry violations.
        
        Reasoning:
        - Anti-symmetry: If A CONTAINS B, then B cannot CONTAINS A
        - Same for PART_OF, INSTANCE_OF, TYPE_OF
        - These are VIOLATIONS (logical contradictions)
        
        Examples:
        - A CONTAINS B and B CONTAINS A → violation
        - A PART_OF B and B PART_OF A → violation
        
        Args:
            graph: Graph to analyze
            
        Returns:
            List of violation dicts with 'message' key
        """
        violations = []
        structural_edges = graph.get_structural_edges()
        
        # Group edges by relation type
        edges_by_type: Dict[RelationType, List[Edge]] = {}
        for edge in structural_edges:
            if edge.relation_type not in edges_by_type:
                edges_by_type[edge.relation_type] = []
            edges_by_type[edge.relation_type].append(edge)
        
        # Check anti-symmetry for each relation type
        anti_symmetric_relations = {
            RelationType.CONTAINS,
            RelationType.PART_OF,
            RelationType.INSTANCE_OF,
            RelationType.TYPE_OF
        }
        
        for relation_type in anti_symmetric_relations:
            if relation_type not in edges_by_type:
                continue
            
            # Build set of (source, target) pairs
            pairs: Set[Tuple[str, str]] = set()
            for edge in edges_by_type[relation_type]:
                pairs.add((edge.source_id, edge.target_id))
            
            # Check for reverse pairs
            for source_id, target_id in pairs:
                reverse_pair = (target_id, source_id)
                if reverse_pair in pairs:
                    violations.append({
                        'message': (
                            f"Anti-symmetry violation: {source_id} {relation_type.value} "
                            f"{target_id} and {target_id} {relation_type.value} {source_id}"
                        )
                    })
        
        return violations
    
    def _detect_transitivity_violations(self, graph: Graph) -> List[Dict[str, str]]:
        """Detects transitivity violations.
        
        Reasoning:
        - Transitivity: If A CONTAINS B and B CONTAINS C, then A should CONTAINS C
        - If the transitive relation is missing, it's a WARNING (not a violation)
        - We detect missing transitive relations
        
        Algorithm:
        1. Build transitive closure for hierarchical relations
        2. Check if actual edges match expected transitive relations
        3. Report missing transitive edges as warnings
        
        Args:
            graph: Graph to analyze
            
        Returns:
            List of violation dicts with 'message' key
        """
        violations = []
        structural_edges = graph.get_structural_edges()
        
        # Focus on CONTAINS and PART_OF (most common transitive relations)
        transitive_relations = {
            RelationType.CONTAINS,
            RelationType.PART_OF,
            RelationType.INSTANCE_OF,
            RelationType.TYPE_OF
        }
        
        # Build adjacency list for each transitive relation
        for relation_type in transitive_relations:
            adjacency: Dict[str, List[str]] = {}
            existing_edges: Set[Tuple[str, str]] = set()
            
            for edge in structural_edges:
                if edge.relation_type == relation_type:
                    if edge.source_id not in adjacency:
                        adjacency[edge.source_id] = []
                    adjacency[edge.source_id].append(edge.target_id)
                    existing_edges.add((edge.source_id, edge.target_id))
            
            if not adjacency:
                continue
            
            # Compute transitive closure (simplified: 2-step transitivity)
            # For A → B → C, check if A → C exists
            for source in adjacency:
                for intermediate in adjacency.get(source, []):
                    for target in adjacency.get(intermediate, []):
                        expected_edge = (source, target)
                        if expected_edge not in existing_edges:
                            violations.append({
                                'message': (
                                    f"Transitivity violation: {source} {relation_type.value} "
                                    f"{intermediate} and {intermediate} {relation_type.value} "
                                    f"{target}, but {source} {relation_type.value} {target} is missing"
                                )
                            })
        
        return violations
    
    def _detect_missing_inverses(self, graph: Graph) -> List[Dict[str, str]]:
        """Detects missing inverse relations.
        
        Reasoning:
        - Inverse relations: A CONTAINS B should imply B PART_OF A
        - A INSTANCE_OF B should imply B TYPE_OF A
        - Missing inverses are WARNINGS (not violations, as they might be implicit)
        
        Args:
            graph: Graph to analyze
            
        Returns:
            List of missing inverse dicts with 'message' key
        """
        missing = []
        structural_edges = graph.get_structural_edges()
        
        # Define inverse pairs
        inverse_pairs = {
            RelationType.CONTAINS: RelationType.PART_OF,
            RelationType.PART_OF: RelationType.CONTAINS,
            RelationType.INSTANCE_OF: RelationType.TYPE_OF,
            RelationType.TYPE_OF: RelationType.INSTANCE_OF
        }
        
        # Build sets of existing edges by type
        edges_by_type: Dict[RelationType, Set[Tuple[str, str]]] = {}
        for edge in structural_edges:
            if edge.relation_type not in edges_by_type:
                edges_by_type[edge.relation_type] = set()
            edges_by_type[edge.relation_type].add((edge.source_id, edge.target_id))
        
        # Check for missing inverses
        for relation_type, inverse_type in inverse_pairs.items():
            if relation_type not in edges_by_type:
                continue
            
            for source_id, target_id in edges_by_type[relation_type]:
                expected_inverse = (target_id, source_id)
                if inverse_type not in edges_by_type:
                    missing.append({
                        'message': (
                            f"Missing inverse: {source_id} {relation_type.value} {target_id}, "
                            f"but {target_id} {inverse_type.value} {source_id} is missing"
                        )
                    })
                elif expected_inverse not in edges_by_type[inverse_type]:
                    missing.append({
                        'message': (
                            f"Missing inverse: {source_id} {relation_type.value} {target_id}, "
                            f"but {target_id} {inverse_type.value} {source_id} is missing"
                        )
                    })
        
        return missing
    
    def _detect_type_inconsistencies(self, graph: Graph) -> List[Dict[str, str]]:
        """Detects type hierarchy inconsistencies.
        
        Reasoning:
        - A INSTANCE_OF B means A is an instance of type B
        - B INSTANCE_OF A would mean B is an instance of type A
        - This creates a circular type relationship (violation)
        - Similar for TYPE_OF
        
        Args:
            graph: Graph to analyze
            
        Returns:
            List of inconsistency dicts with 'message' key
        """
        inconsistencies = []
        structural_edges = graph.get_structural_edges()
        
        # Check INSTANCE_OF and TYPE_OF for circular relationships
        instance_edges: Set[Tuple[str, str]] = set()
        type_edges: Set[Tuple[str, str]] = set()
        
        for edge in structural_edges:
            if edge.relation_type == RelationType.INSTANCE_OF:
                instance_edges.add((edge.source_id, edge.target_id))
            elif edge.relation_type == RelationType.TYPE_OF:
                type_edges.add((edge.source_id, edge.target_id))
        
        # Check for circular INSTANCE_OF
        for source_id, target_id in instance_edges:
            reverse = (target_id, source_id)
            if reverse in instance_edges:
                inconsistencies.append({
                    'message': (
                        f"Type inconsistency: {source_id} INSTANCE_OF {target_id} and "
                        f"{target_id} INSTANCE_OF {source_id} (circular type relationship)"
                    )
                })
        
        # Check for circular TYPE_OF
        for source_id, target_id in type_edges:
            reverse = (target_id, source_id)
            if reverse in type_edges:
                inconsistencies.append({
                    'message': (
                        f"Type inconsistency: {source_id} TYPE_OF {target_id} and "
                        f"{target_id} TYPE_OF {source_id} (circular type relationship)"
                    )
                })
        
        return inconsistencies
    
    def _detect_similarity_asymmetry(self, graph: Graph) -> List[Dict[str, str]]:
        """Detects SIMILAR_TO asymmetry.
        
        Reasoning:
        - SIMILAR_TO should be symmetric: A SIMILAR_TO B implies B SIMILAR_TO A
        - Missing symmetric edges are WARNINGS (not violations, as similarity might be implicit)
        
        Args:
            graph: Graph to analyze
            
        Returns:
            List of asymmetry dicts with 'message' key
        """
        asymmetries = []
        structural_edges = graph.get_structural_edges()
        
        # Build set of SIMILAR_TO edges
        similar_edges: Set[Tuple[str, str]] = set()
        for edge in structural_edges:
            if edge.relation_type == RelationType.SIMILAR_TO:
                similar_edges.add((edge.source_id, edge.target_id))
        
        # Check for missing symmetric edges
        for source_id, target_id in similar_edges:
            reverse = (target_id, source_id)
            if reverse not in similar_edges:
                asymmetries.append({
                    'message': (
                        f"Similarity asymmetry: {source_id} SIMILAR_TO {target_id}, "
                        f"but {target_id} SIMILAR_TO {source_id} is missing"
                    )
                })
        
        return asymmetries