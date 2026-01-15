"""Base classes for graph validation."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Callable, Optional, Union, Type, Any
from got.domain.model.graph import Graph
from got.domain.events.cycle_detected import CycleDetected
from got.domain.events.contradiction_detected import ContradictionDetected


@dataclass
class ValidationResult:
    """Result of a validation operation.
    
    Contains violations, warnings, and emitted events.
    Validation is informative (non-destructive): it detects
    problems but doesn't modify the graph.
    """
    is_valid: bool = True
    violations: List[str] = field(default_factory=list)  # Error messages
    warnings: List[str] = field(default_factory=list)  # Warning messages
    events: List[Union[CycleDetected, ContradictionDetected]] = field(
        default_factory=list
    )  # Domain events
    
    def add_violation(
        self, 
        message: str, 
        event: Optional[Union[CycleDetected, ContradictionDetected]] = None
    ) -> None:
        """Adds a violation and its associated event.
        
        Args:
            message: Violation message (cannot be empty)
            event: Optional domain event associated with the violation
            
        Raises:
            ValueError: If message is empty
        """
        if not message or not message.strip():
            raise ValueError("Violation message cannot be empty")
        
        self.is_valid = False
        self.violations.append(message)
        if event:
            self.events.append(event)
    
    def add_warning(
        self, 
        message: str, 
        event: Optional[Union[CycleDetected, ContradictionDetected]] = None
    ) -> None:
        """Adds a warning and its associated event.
        
        Args:
            message: Warning message (cannot be empty)
            event: Optional domain event associated with the warning
            
        Raises:
            ValueError: If message is empty
        """
        if not message or not message.strip():
            raise ValueError("Warning message cannot be empty")
        
        self.warnings.append(message)
        if event:
            self.events.append(event)
    
    def has_issues(self) -> bool:
        """Checks if there are any issues (violations or warnings).
        
        Returns:
            True if there are violations or warnings
        """
        return len(self.violations) > 0 or len(self.warnings) > 0
    
    def get_events_by_type(
        self, 
        event_type: Type[Union[CycleDetected, ContradictionDetected]]
    ) -> List[Union[CycleDetected, ContradictionDetected]]:
        """Gets events of a specific type.
        
        Args:
            event_type: Type of event to filter (CycleDetected or ContradictionDetected)
            
        Returns:
            List of events of the specified type
        """
        return [e for e in self.events if isinstance(e, event_type)]
    
    def has_cycles(self) -> bool:
        """Checks if any cycles were detected.
        
        Returns:
            True if any CycleDetected events exist
        """
        return any(isinstance(e, CycleDetected) for e in self.events)
    
    def has_contradictions(self) -> bool:
        """Checks if any contradictions were detected.
        
        Returns:
            True if any ContradictionDetected events exist
        """
        return any(isinstance(e, ContradictionDetected) for e in self.events)
    
    def get_summary(self) -> dict:
        """Returns a summary of validation results.
        
        Returns:
            Dictionary with summary statistics
        """
        return {
            "is_valid": self.is_valid,
            "violation_count": len(self.violations),
            "warning_count": len(self.warnings),
            "event_count": len(self.events),
            "has_cycles": self.has_cycles(),
            "has_contradictions": self.has_contradictions(),
            "cycle_count": len(self.get_events_by_type(CycleDetected)),
            "contradiction_count": len(self.get_events_by_type(ContradictionDetected))
        }


class BaseValidator(ABC):
    """Base interface for all layer-specific validators.
    
    Each validator validates a specific layer (causal, epistemic, structural, etc.)
    and emits domain events when problems are detected.
    
    DDD Principles:
    - Pure domain logic (no external dependencies)
    - Emits domain events (non-destructive)
    - Single responsibility (one layer per validator)
    """
    
    def __init__(self, event_handler: Optional[Callable] = None):
        """
        Args:
            event_handler: Optional callback to handle events as they're emitted.
                          If None, events are stored in ValidationResult.
                          Callback signature: (event: DomainEvent) -> None
        """
        self.event_handler = event_handler
    
    @abstractmethod
    def validate(self, graph: Graph) -> ValidationResult:
        """Validates the graph according to layer-specific rules.
        
        Args:
            graph: Graph to validate
            
        Returns:
            ValidationResult with violations, warnings, and events
        """
        pass
    
    @abstractmethod
    def get_layer(self) -> str:
        """Returns the layer this validator validates.
        
        Returns:
            Layer name ("causal", "epistemic", "structural", "temporal", "logical")
        """
        pass
    
    def _create_result(self) -> ValidationResult:
        """Factory method to create a ValidationResult.
        
        Returns:
            New ValidationResult instance
        """
        return ValidationResult()
    
    def _emit_event(
        self, 
        event: Union[CycleDetected, ContradictionDetected]
    ) -> None:
        """Emits a domain event via the handler or stores it.
        
        Args:
            event: Domain event to emit
        """
        if self.event_handler:
            self.event_handler(event)