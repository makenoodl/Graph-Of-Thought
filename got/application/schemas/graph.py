from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field

from got.domain.model.graph import Graph
from got.domain.model.node import Node
from got.domain.model.edge import Edge
from got.domain.model.value_objects import Confidence, NodeType, RelationType


class NodeDTO(BaseModel):
    id: str
    concept: str
    node_type: NodeType = Field(default=NodeType.CONCEPT)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    metadata: Dict = Field(default_factory=dict)


class EdgeDTO(BaseModel):
    source_id: str
    target_id: str
    relation_type: RelationType
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    metadata: Dict = Field(default_factory=dict)


class GraphDTO(BaseModel):
    nodes: List[NodeDTO] = Field(default_factory=list)
    edges: List[EdgeDTO] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)

    @classmethod
    def from_domain(cls, graph: Graph) -> "GraphDTO":
        """Create a DTO from a domain Graph."""
        return cls(
            nodes=[
                NodeDTO(
                    id=node.id,
                    concept=node.concept,
                    node_type=node.node_type,
                    confidence=float(node.confidence),
                    metadata=node.metadata or {},
                )
                for node in graph.nodes.values()
            ],
            edges=[
                EdgeDTO(
                    source_id=edge.source_id,
                    target_id=edge.target_id,
                    relation_type=edge.relation_type,
                    confidence=float(edge.confidence),
                    metadata=edge.metadata or {},
                )
                for edge in graph.edges
            ],
            metadata=graph.metadata or {},
        )

    def to_domain(self) -> Graph:
        """Rebuild a domain Graph from this DTO."""
        graph = Graph(metadata=dict(self.metadata))

        # Recreate nodes
        for n in self.nodes:
            node = Node(
                concept=n.concept,
                id=n.id,
                node_type=n.node_type,
                confidence=Confidence.from_float(n.confidence),
                metadata=dict(n.metadata),
            )
            graph.add_node(node)

        # Recreate edges
        for e in self.edges:
            edge = Edge(
                source_id=e.source_id,
                target_id=e.target_id,
                relation_type=e.relation_type,
                confidence=Confidence.from_float(e.confidence),
                metadata=dict(e.metadata),
            )
            graph.add_edge(edge)

        return graph