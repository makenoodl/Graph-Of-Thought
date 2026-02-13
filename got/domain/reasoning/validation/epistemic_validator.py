"""Validator for epistemic relations (belief and evidence relationships)."""
from typing import List, Dict, Tuple
from got.domain.model.graph import Graph
from got.domain.model.edge import Edge
from got.domain.model.value_objects import RelationType
from got.domain.reasoning.validation.base_validator import BaseValidator, ValidationResult
from got.domain.events.contradiction_detected import ContradictionDetected


class EpistemicValidator(BaseValidator):
    """Validates epistemic relations.
    
    Detects:
    - Direct contradictions (A CONTRADICTS B)
    - Belief conflicts (A SUPPORTS B but A CONTRADICTS B)
    - Evidence conflicts (EVIDENCE_FOR and EVIDENCE_AGAINST on same concept)
    - Confidence inconsistencies (high confidence with conflicting evidence)
    
    DDD Principles:
    - Pure domain logic (algorithms are deterministic)
    - Uses domain model (Graph, Edge, RelationType, Confidence)
    - Emits domain events (ContradictionDetected)
    - No external dependencies
    """
    
    def get_layer(self) -> str:
        """Returns the layer this validator validates."""
        return "epistemic"
    
    def validate(self, graph: Graph) -> ValidationResult:
        """Validates the epistemic layer.
        
        Pipeline:
        1. Retrieve all epistemic edges
        2. Detect direct contradictions → violations
        3. Detect belief conflicts → warnings
        4. Detect evidence conflicts → warnings
        5. Check confidence consistency → warnings
        6. Return ValidationResult with all issues
        
        Args:
            graph: Graph to validate
            
        Returns:
            ValidationResult with violations, warnings, and events
        """
        result = ValidationResult()
        
        # STEP 1: Detect direct contradictions (violations)
        contradictions = self._detect_direct_contradictions(graph)
        for contradiction in contradictions:
            message = (
                f"Direct contradiction: {contradiction['source']} CONTRADICTS "
                f"{contradiction['target']}"
            )
            event = ContradictionDetected(
                node1_id=contradiction['source'],
                node2_id=contradiction['target']
            )
            result.add_violation(message, event)
            self._emit_event(event)
        
        # STEP 2: Detect belief conflicts (warnings)
        belief_conflicts = self._detect_belief_conflicts(graph)
        for conflict in belief_conflicts:
            event = ContradictionDetected(
                node1_id=conflict['node1'],
                node2_id=conflict['node2']
            )
            result.add_warning(conflict['message'], event)
            self._emit_event(event)
        
        # STEP 3: Detect evidence conflicts (warnings)
        evidence_conflicts = self._detect_evidence_conflicts(graph)
        for conflict in evidence_conflicts:
            # For evidence conflicts, we have a single node
            # ContradictionDetected requires 2 nodes, so we duplicate
            event = ContradictionDetected(
                node1_id=conflict['node_id'],
                node2_id=conflict['node_id']  # Same node (internal conflict)
            )
            result.add_warning(conflict['message'], event)
            self._emit_event(event)
        
        # STEP 4: Check confidence consistency (warnings)
        confidence_issues = self._check_confidence_consistency(graph)
        for issue in confidence_issues:
            result.add_warning(issue)
        
        return result
    
    def _detect_direct_contradictions(self, graph: Graph) -> List[Dict[str, str]]:
        """Detects direct contradictions (CONTRADICTS relations).
        
        Reasoning:
        - Iterates through all epistemic edges
        - If relation_type == CONTRADICTS → direct contradiction
        - This is a VIOLATION (not just a warning)
        
        Args:
            graph: Graph to analyze
            
        Returns:
            List of contradiction dicts with 'source' and 'target' keys
        """
        contradictions = []
        epistemic_edges = graph.get_epistemic_edges()
        
        for edge in epistemic_edges:
            if edge.relation_type == RelationType.CONTRADICTS:
                contradictions.append({
                    'source': edge.source_id,
                    'target': edge.target_id
                })
        
        return contradictions
    
    def _detect_belief_conflicts(self, graph: Graph) -> List[Dict[str, any]]:
        """Detects belief conflicts between same nodes.
        
        Reasoning:
        - A conflict = same pair (A, B) with opposing relations
        - Examples of conflicts:
          * A SUPPORTS B AND A CONTRADICTS B
          * A STRENGTHENS B AND A WEAKENS B
          * A EVIDENCE_FOR B AND A EVIDENCE_AGAINST B
        
        Algorithm:
        1. Group edges by pair (source_id, target_id)
        2. For each pair with ≥2 edges:
           - Extract relation_types
           - Check for oppositions
        3. Return detected conflicts
        
        Args:
            graph: Graph to analyze
            
        Returns:
            List of conflict dicts with 'node1', 'node2', 'message'
        """
        conflicts = []
        epistemic_edges = graph.get_epistemic_edges()
        
        # STEP 1: Group edges by pair (source_id, target_id)
        edge_map: Dict[Tuple[str, str], List[Edge]] = {}
        for edge in epistemic_edges:
            pair = (edge.source_id, edge.target_id)
            if pair not in edge_map:
                edge_map[pair] = []
            edge_map[pair].append(edge)
        
        # STEP 2: Check conflicts in each pair
        for (source_id, target_id), edges in edge_map.items():
            # Need at least 2 edges to have a conflict
            if len(edges) < 2:
                continue
            
            # Extract relation types
            relation_types = {edge.relation_type for edge in edges}
            
            # CONFLICT 1: SUPPORTS vs CONTRADICTS
            if RelationType.SUPPORTS in relation_types and RelationType.CONTRADICTS in relation_types:
                conflicts.append({
                    'node1': source_id,
                    'node2': target_id,
                    'message': (
                        f"Belief conflict: {source_id} SUPPORTS and CONTRADICTS "
                        f"{target_id} simultaneously"
                    )
                })
            
            # CONFLICT 2: STRENGTHENS vs WEAKENS
            if RelationType.STRENGTHENS in relation_types and RelationType.WEAKENS in relation_types:
                conflicts.append({
                    'node1': source_id,
                    'node2': target_id,
                    'message': (
                        f"Belief conflict: {source_id} STRENGTHENS and WEAKENS "
                        f"{target_id} simultaneously"
                    )
                })
            
            # CONFLICT 3: EVIDENCE_FOR vs EVIDENCE_AGAINST
            if RelationType.EVIDENCE_FOR in relation_types and RelationType.EVIDENCE_AGAINST in relation_types:
                conflicts.append({
                    'node1': source_id,
                    'node2': target_id,
                    'message': (
                        f"Evidence conflict: {source_id} is EVIDENCE_FOR and "
                        f"EVIDENCE_AGAINST {target_id} simultaneously"
                    )
                })
        
        return conflicts
    
    def _detect_evidence_conflicts(self, graph: Graph) -> List[Dict[str, any]]:
        """Detects nodes with contradictory evidence.
        
        Reasoning:
        - A node has evidence conflict if it has:
          * EVIDENCE_FOR edges (evidence supporting)
          * AND EVIDENCE_AGAINST edges (evidence contradicting)
        - Different from belief conflicts:
          * Belief conflicts = same source, opposing relations
          * Evidence conflicts = same target, different sources
        
        Algorithm:
        1. Group edges by target_id (node receiving evidence)
        2. Separate EVIDENCE_FOR and EVIDENCE_AGAINST
        3. Find nodes with both types
        4. Return conflicts
        
        Args:
            graph: Graph to analyze
            
        Returns:
            List of conflict dicts with 'node_id' and 'message'
        """
        conflicts = []
        epistemic_edges = graph.get_epistemic_edges()
        
        # STEP 1: Group edges by target (node receiving evidence)
        evidence_for: Dict[str, List[Edge]] = {}  # node_id → supporting edges
        evidence_against: Dict[str, List[Edge]] = {}  # node_id → contradicting edges
        
        for edge in epistemic_edges:
            target = edge.target_id
            
            if edge.relation_type == RelationType.EVIDENCE_FOR:
                if target not in evidence_for:
                    evidence_for[target] = []
                evidence_for[target].append(edge)
            
            elif edge.relation_type == RelationType.EVIDENCE_AGAINST:
                if target not in evidence_against:
                    evidence_against[target] = []
                evidence_against[target].append(edge)
        
        # STEP 2: Find nodes with both types of evidence
        conflicted_nodes = set(evidence_for.keys()) & set(evidence_against.keys())
        
        # STEP 3: Create conflict messages
        for node_id in conflicted_nodes:
            for_count = len(evidence_for[node_id])
            against_count = len(evidence_against[node_id])
            
            conflicts.append({
                'node_id': node_id,
                'message': (
                    f"Evidence conflict on {node_id}: "
                    f"{for_count} evidence(s) for, {against_count} evidence(s) against"
                )
            })
        
        return conflicts
    
    def _check_confidence_consistency(self, graph: Graph) -> List[str]:
        """Checks consistency between node confidence and their relations.
        
        Reasoning:
        - If a node has high confidence (>0.7) but many weakening relations
          → Suspicious inconsistency
        - If a node has low confidence (<0.3) but many supporting relations
          → Suspicious inconsistency
        
        Algorithm:
        1. Count supporting vs weakening relations per node
        2. For each node:
           - Compare confidence vs number of relations
           - Detect inconsistencies
        3. Return warnings
        
        Args:
            graph: Graph to analyze
            
        Returns:
            List of warning messages
        """
        issues = []
        epistemic_edges = graph.get_epistemic_edges()
        
        # STEP 1: Count relations per node
        node_support: Dict[str, int] = {}  # node_id → supporting count
        node_weaken: Dict[str, int] = {}  # node_id → weakening count
        
        for edge in epistemic_edges:
            target = edge.target_id
            
            # Supporting relations
            if edge.relation_type in {
                RelationType.SUPPORTS,
                RelationType.STRENGTHENS,
                RelationType.EVIDENCE_FOR
            }:
                node_support[target] = node_support.get(target, 0) + 1
            
            # Weakening relations
            elif edge.relation_type in {
                RelationType.WEAKENS,
                RelationType.EVIDENCE_AGAINST
            }:
                node_weaken[target] = node_weaken.get(target, 0) + 1
        
        # STEP 2: Check consistency for each node
        for node_id, node in graph.nodes.items():
            confidence = node.confidence.value
            support_count = node_support.get(node_id, 0)
            weaken_count = node_weaken.get(node_id, 0)
            
            # INCONSISTENCY 1: High confidence but more weakening relations
            if confidence > 0.7 and weaken_count > support_count and weaken_count > 0:
                issues.append(
                    f"Confidence inconsistency: {node_id} has high confidence "
                    f"({confidence:.2f}) but {weaken_count} weakening relation(s) "
                    f"vs {support_count} supporting relation(s)"
                )
            
            # INCONSISTENCY 2: Low confidence but more supporting relations
            elif confidence < 0.3 and support_count > weaken_count and support_count > 0:
                issues.append(
                    f"Confidence inconsistency: {node_id} has low confidence "
                    f"({confidence:.2f}) but {support_count} supporting relation(s) "
                    f"vs {weaken_count} weakening relation(s)"
                )
        
        return issues