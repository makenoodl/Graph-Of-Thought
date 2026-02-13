"""Main validator orchestrator for multi-layer validation."""
from typing import List, Callable, Optional
from got.domain.model.graph import Graph
from got.domain.reasoning.validation.base_validator import BaseValidator, ValidationResult
from got.domain.reasoning.validation.causal_validator import CausalValidator
from got.domain.reasoning.validation.epistemic_validator import EpistemicValidator
from got.domain.reasoning.validation.structural_validator import StructuralValidator


class Validator:
    """
    Multi-layer validation orchestrator.
    
    This is a Domain Service that coordinates multiple validators.
    
    DDD Principles:
    - Domain Service (orchestrates domain logic)
    - Single Responsibility (coordination only)
    - Encapsulation (clients don't need to know individual validators)
    - Open/Closed (easy to add new validators without changing clients)
    
    Pattern: Facade Pattern
    - Provides a simple interface to a complex subsystem
    - Hides the complexity of multiple validators
    """
    
    def __init__(self, event_handler: Optional[Callable] = None):
        """
        Args:
            event_handler: Optional callback for each emitted event.
                          If None, events are stored in ValidationResult.
        """
        self.event_handler = event_handler
        
        # Register all validators
        # This is where you add new validators as you implement them
        self.validators: List[BaseValidator] = [
            CausalValidator(event_handler=event_handler),
            EpistemicValidator(event_handler=event_handler),
            StructuralValidator(event_handler=event_handler),
        ]
    
    def validate(self, graph: Graph) -> ValidationResult:
        """
        Validates the graph across all layers.
        
        This is the main entry point for validation.
        Clients don't need to know about individual validators.
        
        Args:
            graph: Graph to validate
            
        Returns:
            ValidationResult with aggregated results from all validators
        """
        # Early return for empty graph (optimization)
        if graph.is_empty():
            return ValidationResult(
                is_valid=True,
                violations=[],
                warnings=["Graph is empty - nothing to validate"],
                events=[]
            )
        
        # Early return if no validators registered (safety check)
        if not self.validators:
            return ValidationResult(
                is_valid=True,
                violations=[],
                warnings=["No validators registered"],
                events=[]
            )
        
        all_violations = []
        all_warnings = []
        all_events = []
        
        # Call each validator
        for validator in self.validators:
            result = validator.validate(graph)
            
            # Aggregate results
            all_violations.extend(result.violations)
            all_warnings.extend(result.warnings)
            all_events.extend(result.events)
            
            # Emit events if handler provided
            if self.event_handler:
                for event in result.events:
                    self.event_handler(event)
        
        # Return aggregated result
        return ValidationResult(
            is_valid=len(all_violations) == 0,
            violations=all_violations,
            warnings=all_warnings,
            events=all_events
        )
    
    def validate_layer(self, graph: Graph, layer: str) -> ValidationResult:
        """
        Validates a specific layer.
        
        Useful for debugging or layer-specific validation.
        
        Args:
            graph: Graph to validate
            layer: Layer name ("causal", "epistemic", "structural", etc.)
            
        Returns:
            ValidationResult for the specified layer
            
        Raises:
            ValueError: If layer is unknown
        """
        for validator in self.validators:
            if validator.get_layer() == layer:
                return validator.validate(graph)
        
        available_layers = [v.get_layer() for v in self.validators]
        raise ValueError(
            f"Unknown layer: {layer}. Available layers: {available_layers}"
        )