"""Atomic operation to add an edge to the graph."""
from got.domain.model import Graph, Edge
from got.domain.model.value_objects.relation_type import RelationType
from got.domain.model.value_objects.confidence import Confidence
from got.domain.events import EdgeAdded


class AddEdge:
    """Operation to add an edge to the graph.
    
    This operation is FUNDAMENTAL because:
    - It ensures atomicity (all or nothing)
    - It generates events for traceability
    - It validates before modification
    - It encapsulates the creation logic
    """
    
    def execute(
        self, 
        graph: Graph, 
        source_id: str, 
        target_id: str, 
        relation_type: RelationType,
        confidence: Confidence = None
    ) -> EdgeAdded:
        """
        Core logic:
        1. Create edge (domain entity)
        2. Add to graph (validates integrity)
        3. Generate event (for traceability)
        4. Return event (for event store)
        
        Args:
            graph: Graph to add edge to
            source_id: ID of the source node
            target_id: ID of the target node
            relation_type: Type of semantic relation
            confidence: Initial confidence level (default: 0.5)
            
        Returns:
            EdgeAdded event for tracking
            
        Raises:
            ValueError: If source or target node doesn't exist, 
                       if edge already exists, or if edge connects node to itself
        """
        # 1. Create edge (domain entity)
        if confidence is None:
            confidence = Confidence(0.5)
        
        edge = Edge(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            confidence=confidence
        )
        
        # 2. Add to graph (validates integrity)
        graph.add_edge(edge)
        
        # 3. Generate event (for traceability)
        event = EdgeAdded.from_edge(edge)
        
        # 4. Return event (for event store or logging)
        return event