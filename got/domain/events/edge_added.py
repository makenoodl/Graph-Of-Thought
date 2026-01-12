# got/domain/events/edge_added.py
from dataclasses import dataclass
import datetime

from got.domain.model.edge import Edge


@dataclass(frozen=True)
class EdgeAdded:
    """Event fired when an edge is added."""
    source_id: str
    target_id: str
    relation_type: str
    confidence: float
    timestamp: datetime
    
    @classmethod
    def from_edge(cls, edge: Edge) -> "EdgeAdded":
        return cls(
            source_id=edge.source_id,
            target_id=edge.target_id,
            relation_type=edge.relation_type.value,
            confidence=edge.confidence.value,
            timestamp=edge.created_at
        )
