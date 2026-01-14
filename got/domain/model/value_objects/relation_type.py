"""Types of semantic relations between concepts."""
from enum import Enum


class RelationType(str, Enum):
    """Types of relations in the reasoning graph."""
    
    # Causal relations
    CAUSES = "causes"  # A causes B
    REQUIRES = "requires"  # A requires B
    DEPENDS_ON = "depends_on"  # A depends on B
    ENABLES = "enables"  # A enables B (facilitates without guaranteeing)
    PREVENTS = "prevents"  # A prevents B (negative causality)
    
    # Logical relations
    IMPLIES = "implies"  # A implies B
    SUPPORTS = "supports"  # A supports B
    CONTRADICTS = "contradicts"  # A contradicts B
    BLOCKS = "blocks"  # A blocks B

    # Epistemic relations
    WEAKENS = "weakens"  # A weakens B (diminishes confidence without full contradiction)
    STRENGTHENS = "strengthens"  # A strengthens B (increases confidence)
    EVIDENCE_FOR = "evidence_for"  # A is evidence for B (factual proof)
    EVIDENCE_AGAINST = "evidence_against"  # A is evidence against B (factual counter-proof)
    EXPLAINS = "explains"  # A explains B (epistemic justification)
    
    # Structural relations
    CONTAINS = "contains"  # A contains B
    PART_OF = "part_of"  # A is part of B
    SIMILAR_TO = "similar_to"  # A similar to B
    INSTANCE_OF = "instance_of"  # A is instance of B
    TYPE_OF = "type_of"  # A is type of B
    IMPLEMENTS = "implements"  # A implements B (interface/contract)
    
    # Temporal relations
    PRECEDES = "precedes"  # A precedes B
    FOLLOWS = "follows"  # A follows B
    
    def __str__(self) -> str:
        """Returns the enum value."""
        return self.value

    def get_layer(self) -> str:
        """Returns the layer (dimension) of this relation type.
        
        Layers represent different dimensions of reasoning:
        - causal: cause-effect relationships
        - epistemic: belief and evidence relationships
        - structural: composition and type relationships
        - temporal: time-based relationships
        - logical: general logical relationships
        
        Returns:
            str: The layer name ("causal", "epistemic", "structural", "temporal", or "logical")
        """
        # Check causal layer first
        if self.is_causal():
            return "causal"
        
        # Check epistemic layer (includes SUPPORTS, CONTRADICTS, and new types)
        if self.is_epistemic():
            return "epistemic"
        
        # Check structural layer (includes new types)
        if self.is_structural():
            return "structural"
        
        # Check temporal layer
        if self.is_temporal():
            return "temporal"
        
        # Default to logical for remaining relations
        return "logical"
    
    def is_causal(self) -> bool:
        """Checks if the relation is causal.
        
        Causal relations express cause-effect, dependency, or enabling relationships.
        """
        return self in {
            RelationType.CAUSES,
            RelationType.REQUIRES,
            RelationType.DEPENDS_ON,
            RelationType.ENABLES,
            RelationType.PREVENTS,
        }
    
    def is_logical(self) -> bool:
        """Checks if the relation is logical.
        
        Logical relations express general logical relationships.
        Note: Some relations (SUPPORTS, CONTRADICTS) are also epistemic.
        """
        return self in {
            RelationType.IMPLIES,
            RelationType.SUPPORTS,
            RelationType.CONTRADICTS,
            RelationType.BLOCKS
        }
    
    def is_epistemic(self) -> bool:
        """Checks if the relation is epistemic.
        
        Epistemic relations express belief, evidence, or justification relationships.
        They model how confidence in one concept affects confidence in another.
        """
        return self in {
            RelationType.SUPPORTS,  # Already exists, but epistemic
            RelationType.CONTRADICTS,  # Already exists, but epistemic
            RelationType.WEAKENS,
            RelationType.STRENGTHENS,
            RelationType.EVIDENCE_FOR,
            RelationType.EVIDENCE_AGAINST,
            RelationType.EXPLAINS,
        }
    
    def is_structural(self) -> bool:
        """Checks if the relation is structural.
        
        Structural relations express composition, type hierarchy, or implementation relationships.
        """
        return self in {
            RelationType.CONTAINS,
            RelationType.PART_OF,
            RelationType.SIMILAR_TO,
            RelationType.INSTANCE_OF,
            RelationType.TYPE_OF,
            RelationType.IMPLEMENTS,
        }
    
    def is_temporal(self) -> bool:
        """Checks if the relation is temporal.
        
        Temporal relations express time-based ordering between concepts.
        """
        return self in {
            RelationType.PRECEDES,
            RelationType.FOLLOWS,
        }
    
    def is_contradictory(self) -> bool:
        """Checks if the relation expresses a contradiction."""
        return self == RelationType.CONTRADICTS


