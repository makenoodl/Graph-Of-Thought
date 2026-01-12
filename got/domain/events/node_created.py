# Principle: Each important modification generates an event

# got/domain/events/node_created.py
from dataclasses import dataclass, field
import datetime
from typing import Optional

from got.domain.model.edge import Edge
from got.domain.model.node import Node


@dataclass(frozen=True)
class NodeCreated:
    """Event fired when a node is created."""
    node_id: str
    concept: str
    node_type: str
    confidence: float
    timestamp: datetime
    
    @classmethod
    def from_node(cls, node: Node) -> "NodeCreated":
        """Factory method to create event from node."""
        return cls(
            node_id=node.id,
            concept=node.concept,
            node_type=node.node_type.value,
            confidence=node.confidence.value,
            timestamp=node.created_at
        )


