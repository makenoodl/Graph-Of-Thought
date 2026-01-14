"""Atomic operation to remove a node from the graph."""
from got.domain.model import Graph
from got.domain.events import NodeRemoved


class RemoveNode:
    """Operation to remove a node from the graph.
    
    This operation is FUNDAMENTAL because:
    - It ensures atomicity (all or nothing)
    - It generates events for traceability
    - It validates before modification
    - It encapsulates the removal logic
    
    Why separate from Graph.remove_node()?
    - Graph maintains integrity (structural)
    - Ops maintain traceability (temporal)
    - Separation of concerns
    """
    
    def execute(self, graph: Graph, node_id: str) -> NodeRemoved:
        """
        Core logic:
        1. Get node before removal (for event)
        2. Remove from graph (validates integrity)
        3. Generate event (for traceability)
        4. Return event (for event store)
        
        Args:
            graph: Graph to remove node from
            node_id: ID of node to remove
            
        Returns:
            NodeRemoved event for tracking
            
        Raises:
            ValueError: If node does not exist
        """
        # 1. Get node before removal (for event)
        node = graph.get_node(node_id)
        if not node:
            raise ValueError(f"Node {node_id} does not exist")
        
        # 2. Remove from graph (removes edges automatically)
        graph.remove_node(node_id)
        
        # 3. Generate event (for traceability)
        event = NodeRemoved.from_node(node)
        
        # 4. Return event (for event store or logging)
        return event