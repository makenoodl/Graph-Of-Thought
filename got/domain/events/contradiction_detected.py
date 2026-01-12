from dataclasses import dataclass, field
import datetime
from typing import Optional


@dataclass(frozen=True)
class ContradictionDetected:
    """Event fired when a contradiction is detected."""
    node1_id: str
    node2_id: str
    edge_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)