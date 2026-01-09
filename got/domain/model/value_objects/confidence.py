"""Value Object representing a confidence level."""
from dataclasses import dataclass
from typing import Union

"""
Confidence is a domain-level Value Object representing epistemic belief
within the Graph-of-Thought system.

It models how strongly the system (or the human user) believes in a given
concept, hypothesis, or relation at a specific point in time.

This is NOT a statistical probability and NOT a measure of model accuracy.
Instead, it represents a cognitive confidence level, explicitly encoding
uncertainty as a first-class concept in the reasoning process.

Key properties:
- Bounded between 0.0 (no confidence) and 1.0 (full confidence)
- Immutable (Value Object): any change produces a new instance
- Comparable by value, not identity
- Designed to evolve over time through reasoning operations

Confidence enables:
- Non-binary reasoning (beliefs can be weak or strong)
- Hypothesis revision instead of hard deletion
- Confidence propagation across graph relations
- Auditable and explainable reasoning dynamics

By modeling confidence explicitly, the system avoids treating reasoning
as absolute truth and instead supports gradual belief updates, closer
to human cognitive processes.
"""

@dataclass(frozen=True)
class Confidence:
    """Confidence level in a concept or relation.
    
    Value between 0.0 (no confidence) and 1.0 (full confidence).
    """
    value: float
    
    def __post_init__(self):
        """Validates that confidence is in the interval [0.0, 1.0]."""
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.value}")
    
    def __float__(self) -> float:
        """Allows conversion to float."""
        return self.value
    
    def weaken(self, factor: float = 0.1) -> "Confidence":
        """Weakens the confidence by a given factor.
        
        Args:
            factor: Amount to decrease confidence (default: 0.1)
            
        Returns:
            New Confidence instance with decreased value (minimum 0.0)
        """
        new_value = max(0.0, self.value - factor)
        return Confidence(new_value)
    
    def strengthen(self, factor: float = 0.1) -> "Confidence":
        """Strengthens the confidence by a given factor.
        
        Args:
            factor: Amount to increase confidence (default: 0.1)
            
        Returns:
            New Confidence instance with increased value (maximum 1.0)
        """
        new_value = min(1.0, self.value + factor)
        return Confidence(new_value)
    
    @classmethod
    def from_float(cls, value: Union[float, "Confidence"]) -> "Confidence":
        """Creates a Confidence from a float or returns existing Confidence.
        
        This method is idempotent: if value is already a Confidence,
        it returns it unchanged. Useful for functions that accept
        both float and Confidence types.
        
        Args:
            value: Either a float or an existing Confidence instance
            
        Returns:
            Confidence instance (new or existing)
        """
        if isinstance(value, Confidence):
            return value
        return cls(value)