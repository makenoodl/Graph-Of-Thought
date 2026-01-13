"""Atomic operation to add a node to the graph."""
from got.domain.model import Graph, Node
from got.domain.model.value_objects.node_type import NodeType
from got.domain.model.value_objects.confidence import Confidence
from got.domain.events import NodeCreated


class AddNode:
    """Operation to add a node to the graph.
    
    This operation is FUNDAMENTAL because:
    - It ensures atomicity (all or nothing)
    - It generates events for traceability
    - It validates before modification
    - It encapsulates the creation logic
    
    Why separate from Graph.add_node()?
    - Graph maintains integrity (structural)
    - Ops maintain traceability (temporal)
    - Separation of concerns
    """
    
    def execute(
        self, 
        graph: Graph, 
        concept: str, 
        node_type: NodeType,
        confidence: Confidence = None
    ) -> NodeCreated:
        """
        Core logic:
        1. Create node (domain entity)
        2. Add to graph (validates integrity)
        3. Generate event (for traceability)
        4. Return event (for event store)
        
        Args:
            graph: Graph to add node to
            concept: Textual representation of concept
            node_type: Type of cognitive concept
            confidence: Initial confidence level (default: 0.5)
            
        Returns:
            NodeCreated event for tracking
            
        Raises:
            ValueError: If node with same ID already exists
        """
        # 1. Create node (domain entity)
        if confidence is None:
            confidence = Confidence(0.5)
        
        node = Node(
            concept=concept,
            node_type=node_type,
            confidence=confidence
        )
        
        # 2. Add to graph (validates no duplicate)
        graph.add_node(node)
        
        # 3. Generate event (for traceability)
        event = NodeCreated.from_node(node)
        
        # 4. Return event (for event store or logging)
        return event