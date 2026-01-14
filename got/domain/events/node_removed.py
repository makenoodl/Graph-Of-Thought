"""Domain event fired when a node is removed."""
from dataclasses import dataclass
from datetime import datetime
from got.domain.model.node import Node


@dataclass(frozen=True)
class NodeRemoved:
    """Event fired when a node is removed.
    
    This event captures the essential information about a removed node
    for tracking and audit purposes.
    """
    node_id: str
    concept: str
    node_type: str
    timestamp: datetime
    
    @classmethod
    def from_node(cls, node: Node) -> "NodeRemoved":
        """Factory method to create event from node.
        
        Args:
            node: Node that was removed
            
        Returns:
            NodeRemoved event instance
        """
        return cls(
            node_id=node.id,
            concept=node.concept,
            node_type=node.node_type.value,
            timestamp=datetime.now()
        )