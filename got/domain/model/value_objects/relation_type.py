"""Types of semantic relations between concepts."""
from enum import Enum


class RelationType(str, Enum):
    """Types of relations in the reasoning graph."""
    
    # Causal relations
    CAUSES = "causes"  # A causes B
    REQUIRES = "requires"  # A requires B
    DEPENDS_ON = "depends_on"  # A depends on B
    
    # Logical relations
    IMPLIES = "implies"  # A implies B
    SUPPORTS = "supports"  # A supports B
    CONTRADICTS = "contradicts"  # A contradicts B
    BLOCKS = "blocks"  # A blocks B
    
    # Structural relations
    CONTAINS = "contains"  # A contains B
    PART_OF = "part_of"  # A is part of B
    SIMILAR_TO = "similar_to"  # A similar to B
    
    # Temporal relations
    PRECEDES = "precedes"  # A precedes B
    FOLLOWS = "follows"  # A follows B
    
    def __str__(self) -> str:
        """Returns the enum value."""
        return self.value
    
    def is_causal(self) -> bool:
        """Checks if the relation is causal."""
        return self in {
            RelationType.CAUSES,
            RelationType.REQUIRES,
            RelationType.DEPENDS_ON
        }
    
    def is_logical(self) -> bool:
        """Checks if the relation is logical."""
        return self in {
            RelationType.IMPLIES,
            RelationType.SUPPORTS,
            RelationType.CONTRADICTS,
            RelationType.BLOCKS
        }
    
    def is_contradictory(self) -> bool:
        """Checks if the relation expresses a contradiction."""
        return self == RelationType.CONTRADICTS