"""Domain event fired when the graph is updated."""
from dataclasses import dataclass, field
from datetime import datetime

from got.domain.model.graph import Graph


@dataclass(frozen=True)
class GraphUpdated:
    """Event fired when the graph is updated.
    
    This event is generated when significant changes occur to the graph,
    such as version increments or major structural modifications.
    
    Key concepts:
    - Version tracking: Records graph version changes
    - Temporal reasoning: Enables rollback and version comparison
    - Checkpoint: Provides checkpoints for analysis
    - Collaborative reasoning: Tracks who changed what (via metadata)
    """
    graph_version: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_graph(cls, graph: Graph) -> "GraphUpdated":
        """Factory method to create event from graph.
        
        Why factory method?
        - Encapsulates event creation from graph state
        - Ensures consistency with graph version
        - Makes it easy to generate events after graph modifications
        
        Args:
            graph: Graph that was updated
            
        Returns:
            GraphUpdated event instance
        """
        return cls(
            graph_version=graph.version,
            timestamp=graph.updated_at
        )