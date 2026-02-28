"""Detects minimal conflicting subgraphs in the reasoning graph.

This module is part of the Structural Reasoning Engine (Phase 2). It identifies
sets of nodes and edges that are jointly inconsistent—contradictions that
undermine the epistemic coherence of the reasoning graph.

Unlike the EpistemicValidator (which flags violations during validation),
the ContradictionDetector produces structured analysis output: ContradictionCluster
objects that describe *where* and *how* the graph is inconsistent. This supports
explainability, debugging, and downstream tools (e.g. suggesting corrections).

Detected patterns:
- Direct contradictions: A CONTRADICTS B
- Belief conflicts: same pair with opposing relations (SUPPORTS + CONTRADICTS,
  STRENGTHENS + WEAKENS, EVIDENCE_FOR + EVIDENCE_AGAINST)
- Evidence conflicts: a node with both EVIDENCE_FOR and EVIDENCE_AGAINST
  from different sources

This layer is strictly non-LLM and deterministic.
"""


from dataclasses import dataclass, field
from typing import List, Set

from got.domain.model.graph import Graph
from got.domain.model.edge import Edge
from got.domain.model.value_objects import RelationType


@dataclass
class ContradictionCluster:
    """A minimal set of nodes and edges that are jointly inconsistent."""
    node_ids: Set[str] = field(default_factory=set)
    edge_ids: List[str] = field(default_factory=list)  # (source, target, type) as identifier
    description: str = ""


class ContradictionDetector:
    """Identifies minimal conflicting subgraphs.
    
    Reuses patterns from EpistemicValidator but structures output
    as subgraphs for analysis and explainability.
    """

    def detect(self, graph: Graph) -> List[ContradictionCluster]:
        """Detects all contradiction clusters in the graph.
        
        Returns:
            List of ContradictionCluster (minimal conflicting subgraphs)
        """
        clusters = []

        # 1. Direct CONTRADICTS edges
        for edge in graph.get_epistemic_edges():
            if edge.relation_type == RelationType.CONTRADICTS:
                clusters.append(ContradictionCluster(
                    node_ids={edge.source_id, edge.target_id},
                    edge_ids=[f"{edge.source_id}:{edge.target_id}:{edge.relation_type.value}"],
                    description=f"Direct contradiction: {edge.source_id} CONTRADICTS {edge.target_id}"
                ))

        # 2. Belief conflicts (same pair, opposing relations)
        clusters.extend(self._detect_belief_conflicts(graph))

        # 3. Evidence conflicts (same target, EVIDENCE_FOR and EVIDENCE_AGAINST)
        clusters.extend(self._detect_evidence_conflicts(graph))

        return clusters

    def _detect_belief_conflicts(self, graph: Graph) -> List[ContradictionCluster]:
        """Detects pairs with opposing relations (SUPPORTS+CONTRADICTS, etc.)."""
        clusters = []
        epistemic_edges = graph.get_epistemic_edges()
        pair_edges: dict[tuple[str, str], list[Edge]] = {}

        for edge in epistemic_edges:
            pair = (edge.source_id, edge.target_id)
            pair_edges.setdefault(pair, []).append(edge)

        for (src, tgt), edges in pair_edges.items():
            if len(edges) < 2:
                continue
            types = {e.relation_type for e in edges}

            if (RelationType.SUPPORTS in types and RelationType.CONTRADICTS in types) or \
               (RelationType.STRENGTHENS in types and RelationType.WEAKENS in types) or \
               (RelationType.EVIDENCE_FOR in types and RelationType.EVIDENCE_AGAINST in types):
                clusters.append(ContradictionCluster(
                    node_ids={src, tgt},
                    edge_ids=[f"{e.source_id}:{e.target_id}:{e.relation_type.value}" for e in edges],
                    description=f"Belief conflict between {src} and {tgt}"
                ))

        return clusters

    def _detect_evidence_conflicts(self, graph: Graph) -> List[ContradictionCluster]:
        """Detects nodes with both EVIDENCE_FOR and EVIDENCE_AGAINST."""
        clusters = []
        evidence_for: dict[str, list[Edge]] = {}
        evidence_against: dict[str, list[Edge]] = {}

        for edge in graph.get_epistemic_edges():
            if edge.relation_type == RelationType.EVIDENCE_FOR:
                evidence_for.setdefault(edge.target_id, []).append(edge)
            elif edge.relation_type == RelationType.EVIDENCE_AGAINST:
                evidence_against.setdefault(edge.target_id, []).append(edge)

        for node_id in set(evidence_for.keys()) & set(evidence_against.keys()):
            edges = evidence_for[node_id] + evidence_against[node_id]
            node_ids = {node_id}
            for e in edges:
                node_ids.add(e.source_id)
            clusters.append(ContradictionCluster(
                node_ids=node_ids,
                edge_ids=[f"{e.source_id}:{e.target_id}:{e.relation_type.value}" for e in edges],
                description=f"Evidence conflict on {node_id}"
            ))

        return clusters