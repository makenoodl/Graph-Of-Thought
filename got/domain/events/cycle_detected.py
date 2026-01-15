"""Domain event fired when a cycle is detected in a graph layer."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class CycleDetected:
    """Event fired when a cycle is detected in a specific layer.
    
    This event is FUNDAMENTAL because:
    - It tracks when reasoning cycles are discovered
    - It enables alerting and notification systems
    - It supports cycle resolution strategies
    - It provides audit trail for graph quality
    
    A cycle path must:
    - Have at least 2 nodes
    - Start and end with the same node
    - Contain at least 2 different nodes (not just A→A)
    
    Example valid cycles:
    - ['A', 'B', 'A']  # Simple cycle
    - ['A', 'B', 'C', 'A']  # Longer cycle
    
    Example invalid cycles:
    - ['A', 'B']  # Doesn't return to start
    - ['A']  # Too short
    - ['A', 'A']  # Trivial cycle (only one unique node)
    """
    layer: str  # "causal", "structural", etc.
    cycle_path: List[str]  # List of node IDs forming the cycle
    cycle_type: str  # "causal", "hierarchical", etc.
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validates the cycle path.
        
        Raises:
            ValueError: If cycle path is invalid
        """
        # 1. Check minimum length
        if not self.cycle_path or len(self.cycle_path) < 2:
            raise ValueError(
                f"Cycle path must contain at least 2 nodes, got {len(self.cycle_path) if self.cycle_path else 0}"
            )
        
        # 2. Check that cycle starts and ends with same node
        if self.cycle_path[0] != self.cycle_path[-1]:
            raise ValueError(
                f"Cycle path must start and end with same node. "
                f"Got: starts with '{self.cycle_path[0]}' but ends with '{self.cycle_path[-1]}'"
            )
        
        # 3. Check that cycle has at least 2 different nodes
        unique_nodes = set(self.cycle_path)
        if len(unique_nodes) < 2:
            raise ValueError(
                f"Cycle must contain at least 2 different nodes. "
                f"Got: {unique_nodes} (trivial cycle)"
            )
        
        # 4. Optional: Check that the validation logic is consistent
        # A valid cycle should have: len(cycle_path) == len(unique_nodes) + 1
        # (because one node appears twice: at start and end)
        expected_length = len(unique_nodes) + 1
        if len(self.cycle_path) != expected_length:
            # This shouldn't happen if the cycle is correctly constructed
            # But we check it as a safety measure
            raise ValueError(
                f"Invalid cycle structure: expected length {expected_length} "
                f"(unique nodes: {len(unique_nodes)} + 1), got {len(self.cycle_path)}. "
                f"Cycle path: {self.cycle_path}"
            )