"""Domain event fired when a node is created."""
from dataclasses import dataclass
from datetime import datetime

from got.domain.model.node import Node


@dataclass(frozen=True)
class NodeCreated:
    """Event fired when a node is created.
    
    This event captures the essential information about a newly created node
    for tracking and audit purposes.
    
    Key concepts:
    - Immutable (frozen=True): Cannot be modified after creation
    - Timestamp: Records when the event occurred
    - Factory method: Creates event from domain entity
    """
    node_id: str
    concept: str
    node_type: str
    confidence: float
    timestamp: datetime
    
    @classmethod
    def from_node(cls, node: Node) -> "NodeCreated":
        """Factory method to create event from node.
        
        Why factory method?
        - Encapsulates event creation logic
        - Ensures consistency
        - Makes it easy to generate events from domain entities
        
        Args:
            node: Node that was created
            
        Returns:
            NodeCreated event instance
        """
        return cls(
            node_id=node.id,
            concept=node.concept,
            node_type=node.node_type.value,
            confidence=node.confidence.value,
            timestamp=node.created_at
        )