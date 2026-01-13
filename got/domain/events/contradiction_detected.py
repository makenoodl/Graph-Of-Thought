"""Domain event fired when a contradiction is detected."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ContradictionDetected:
    """Event fired when a contradiction is detected.
    
    This event is FUNDAMENTAL because:
    - It tracks when reasoning conflicts are discovered
    - It enables alerting and notification systems
    - It supports revision strategies (how to resolve?)
    - It provides audit trail for decision-making
    """
    node1_id: str
    node2_id: str
    edge_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)