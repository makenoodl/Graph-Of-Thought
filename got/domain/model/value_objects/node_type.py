"""Types of nodes in the reasoning graph."""
from enum import Enum


class NodeType(str, Enum):
    """Types of cognitive concepts represented by nodes."""
    
    CONCEPT = "concept"  # General concept
    HYPOTHESIS = "hypothesis"  # Hypothesis to validate
    FACT = "fact"  # Established fact
    GOAL = "goal"  # Goal to achieve
    STATE = "state"  # System state
    PROBLEM = "problem"  # Identified problem
    SOLUTION = "solution"  # Proposed solution
    CONSTRAINT = "constraint"  # Constraint
    
    def __str__(self) -> str:
        """Returns the enum value."""
        return self.value