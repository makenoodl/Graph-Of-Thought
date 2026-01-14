# got/domain/ops/update_node_confidence.py
"""Atomic operation to update node confidence."""
from datetime import datetime
from got.domain.model import Graph
from got.domain.model.value_objects.confidence import Confidence
from got.domain.events import NodeConfidenceUpdated


class UpdateNodeConfidence:
    """Operation to update a node's confidence level."""
    
    def execute(
        self,
        graph: Graph,
        node_id: str,
        new_confidence: Confidence
    ) -> NodeConfidenceUpdated:
        """Update node confidence and return event."""
        # 1. Get node
        node = graph.get_node(node_id)
        if not node:
            raise ValueError(f"Node {node_id} does not exist")
        
        # 2. Update confidence
        old_confidence = node.confidence
        node.update_confidence(new_confidence)
        graph._update_timestamp()
        
        # 3. Generate event
        event = NodeConfidenceUpdated(
            node_id=node_id,
            old_confidence=old_confidence.value,
            new_confidence=new_confidence.value,
            timestamp=datetime.now()
        )
        
        # 4. Return event
        return event