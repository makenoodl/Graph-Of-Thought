"""Représentation d'un concept cognitif dans le graphe."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from got.domain.model.value_objects import Confidence, NodeType


@dataclass
class Node:
    """Node representing a cognitive concept.
    
    A node is the atomic unit of thought in the system.
    It represents a concept, a hypothesis, a fact, etc.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    concept: str  # Textual representation of the concept
    node_type: NodeType = NodeType.CONCEPT
    confidence: Confidence = field(default_factory=lambda: Confidence(0.5))
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validates the node after creation."""
        if not self.concept or not self.concept.strip():
            raise ValueError("Node concept cannot be empty")
    
    def update_confidence(self, new_confidence: Confidence) -> None:
        """Updates the confidence level of the node."""
        self.confidence = new_confidence
    
    def weaken(self, factor: float = 0.1) -> None:
        """Weaken the confidence of the node."""
        self.confidence = self.confidence.weaken(factor)
    
    def strengthen(self, factor: float = 0.1) -> None:
        """Strengthen the confidence of the node."""
        self.confidence = self.confidence.strengthen(factor)
    
    def is_hypothesis(self) -> bool:
        """Checks if the node is a hypothesis."""
        return self.node_type == NodeType.HYPOTHESIS
    
    def is_fact(self) -> bool:
        """Checks if the node is a fact."""
        return self.node_type == NodeType.FACT
    
    def __hash__(self) -> int:
        """Allows the use in sets."""
        return hash(self.id)
    
    def __eq__(self, other) -> bool:
        """Comparison by ID."""
        if not isinstance(other, Node):
            return False
        return self.id == other.id