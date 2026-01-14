# got/domain/ops/remove_edge.py
"""Atomic operation to remove an edge from the graph."""
from got.domain.model import Graph
from got.domain.model.value_objects.relation_type import RelationType
from got.domain.events import EdgeRemoved


class RemoveEdge:
    """Operation to remove an edge from the graph."""
    
    def execute(
        self,
        graph: Graph,
        source_id: str,
        target_id: str,
        relation_type: RelationType
    ) -> EdgeRemoved:
        """Remove an edge and return the event."""
        # 1. Get edge before removal
        edge = graph.get_edge(source_id, target_id, relation_type)
        if not edge:
            raise ValueError("Edge does not exist")
        
        # 2. Remove from graph
        graph.edges.remove(edge)
        graph._update_timestamp()
        
        # 3. Generate event
        event = EdgeRemoved.from_edge(edge)
        
        # 4. Return event
        return event