"""Domain Entity representing a semantic relation between concepts."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from got.domain.model.value_objects import Confidence, RelationType


@dataclass
class Edge:
    """Edge representing a semantic relation between two nodes.
    
    An Edge connects two concepts and expresses a relation
    (causality, dependency, contradiction, support, etc.).
    
    This is an Entity (has identity via source_id + target_id + relation_type),
    not a Value Object. The edge can evolve over time (confidence changes)
    while maintaining its identity.
    """
    source_id: str  # ID of the source node
    target_id: str  # ID of the target node
    relation_type: RelationType
    confidence: Confidence = field(default_factory=lambda: Confidence(0.5))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validates the edge after creation."""
        if self.source_id == self.target_id:
            raise ValueError("Edge cannot connect a node to itself")
        if not self.source_id or not self.target_id:
            raise ValueError("Edge source_id and target_id cannot be empty")
        # Ensure updated_at is initialized
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def connects(self, node1_id: str, node2_id: str) -> bool:
        """Checks if the edge connects two given nodes.
        
        Args:
            node1_id: First node ID
            node2_id: Second node ID
            
        Returns:
            True if edge connects these nodes (in any direction)
        """
        return (self.source_id == node1_id and self.target_id == node2_id) or \
               (self.source_id == node2_id and self.target_id == node1_id)
    
    def connects_to(self, node_id: str) -> bool:
        """Checks if the edge connects to a given node.
        
        Args:
            node_id: Node ID to check
            
        Returns:
            True if edge connects to this node (source or target)
        """
        return self.source_id == node_id or self.target_id == node_id
    
    def get_other_node(self, node_id: str) -> Optional[str]:
        """Gets the ID of the other node connected by this edge.
        
        Args:
            node_id: One of the node IDs
            
        Returns:
            The other node ID, or None if node_id is not connected
        """
        if self.source_id == node_id:
            return self.target_id
        if self.target_id == node_id:
            return self.source_id
        return None
    
    def is_contradictory(self) -> bool:
        """Checks if the relation expresses a contradiction."""
        return self.relation_type.is_contradictory()
    
    def is_causal(self) -> bool:
        """Checks if the relation is causal."""
        return self.relation_type.is_causal()
    
    def is_logical(self) -> bool:
        """Checks if the relation is logical."""
        return self.relation_type.is_logical()
    
    def get_layer(self) -> str:
        """Gets the layer of this edge.
        
        The layer represents the dimension of reasoning of the relation.
        
        Returns:
            str: The layer of the relation ("causal", "epistemic", "structural", "temporal", or "logical")
        """
        return self.relation_type.get_layer()
    
    def update_confidence(self, new_confidence: Confidence) -> None:
        """Updates the confidence level of the relation.
        
        Args:
            new_confidence: New confidence value
        """
        self.confidence = new_confidence
        self.updated_at = datetime.now()
    
    def weaken(self, factor: float = 0.1) -> None:
        """Weakens the edge's confidence.
        
        Args:
            factor: Amount to decrease confidence
        """
        self.update_confidence(self.confidence.weaken(factor))
    
    def strengthen(self, factor: float = 0.1) -> None:
        """Strengthens the edge's confidence.
        
        Args:
            factor: Amount to increase confidence
        """
        self.update_confidence(self.confidence.strengthen(factor))
    
    def is_epistemic(self) -> bool:
        """Checks if this edge is epistemic.
        
        Returns:
            True if this edge is epistemic, False otherwise
        """
        return self.relation_type.is_epistemic()
    
    def is_structural(self) -> bool:
        """ Verify if this edge is structural."""
        return self.relation_type.is_structural()
    
    def is_temporal(self) -> bool:
        """Verify if this edge is temporal."""
        return self.relation_type.is_temporal()

    def update_metadata(self, key: str, value: Any) -> None:
        """Updates metadata for the edge.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def __hash__(self) -> int:
        """Allows use in sets and as dictionary keys."""
        return hash((self.source_id, self.target_id, self.relation_type))
    
    def __eq__(self, other) -> bool:
        """Equality based on source, target, and relation type."""
        if not isinstance(other, Edge):
            return False
        return (self.source_id == other.source_id and
                self.target_id == other.target_id and
                self.relation_type == other.relation_type)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Edge({self.source_id[:8]}... --[{self.relation_type.value}]--> {self.target_id[:8]}..., confidence={self.confidence.value})"