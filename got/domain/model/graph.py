"""Domain Aggregate Root representing the reasoning graph structure."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set

from got.domain.model.edge import Edge
from got.domain.model.node import Node
from got.domain.model.value_objects import NodeType, RelationType


@dataclass
class Graph:
    """Reasoning graph aggregate root.
    
    The Graph is the main aggregate root in the domain.
    It contains nodes (concepts) and edges (relations) that together
    represent the structured reasoning state.
    
    This aggregate ensures consistency:
    - Edges can only connect existing nodes
    - Graph maintains versioning for temporal reasoning
    - All modifications update the timestamp
    """
    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)
    version: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    
    def add_node(self, node: Node) -> None:
        """Adds a node to the graph.
        
        Args:
            node: Node to add
            
        Raises:
            ValueError: If node with same ID already exists
        """
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists in graph")
        self.nodes[node.id] = node
        self._update_timestamp()
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Gets a node by its ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node if found, None otherwise
        """
        return self.nodes.get(node_id)
    
    def has_node(self, node_id: str) -> bool:
        """Checks if a node exists in the graph.
        
        Args:
            node_id: Node ID to check
            
        Returns:
            True if node exists
        """
        return node_id in self.nodes
    
    def remove_node(self, node_id: str) -> None:
        """Removes a node and all its connected edges.
        
        Args:
            node_id: ID of node to remove
            
        Raises:
            ValueError: If node does not exist
        """
        if not self.has_node(node_id):
            raise ValueError(f"Node {node_id} does not exist")
        
        # Remove all edges connected to this node
        self.edges = [e for e in self.edges 
                     if e.source_id != node_id and e.target_id != node_id]
        
        # Remove the node
        del self.nodes[node_id]
        self._update_timestamp()
    
    def add_edge(self, edge: Edge) -> None:
        """Adds an edge to the graph.
        
        Args:
            edge: Edge to add
            
        Raises:
            ValueError: If source or target node doesn't exist, or edge already exists
        """
        # Validate nodes exist
        if not self.has_node(edge.source_id):
            raise ValueError(f"Source node {edge.source_id} does not exist")
        if not self.has_node(edge.target_id):
            raise ValueError(f"Target node {edge.target_id} does not exist")
        
        # Check for duplicate edge
        if edge in self.edges:
            raise ValueError(
                f"Edge already exists: {edge.source_id} --[{edge.relation_type.value}]--> {edge.target_id}"
            )
        
        self.edges.append(edge)
        self._update_timestamp()
    
    def get_edge(self, source_id: str, target_id: str, relation_type: RelationType) -> Optional[Edge]:
        """Gets a specific edge.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            relation_type: Type of relation
            
        Returns:
            Edge if found, None otherwise
        """
        for edge in self.edges:
            if (edge.source_id == source_id and 
                edge.target_id == target_id and 
                edge.relation_type == relation_type):
                return edge
        return None
    
    def get_edges_from(self, node_id: str) -> List[Edge]:
        """Gets all edges starting from a node.
        
        Args:
            node_id: Source node ID
            
        Returns:
            List of outgoing edges
        """
        return [e for e in self.edges if e.source_id == node_id]
    
    def get_edges_to(self, node_id: str) -> List[Edge]:
        """Gets all edges ending at a node.
        
        Args:
            node_id: Target node ID
            
        Returns:
            List of incoming edges
        """
        return [e for e in self.edges if e.target_id == node_id]
    
    def get_edges_connected_to(self, node_id: str) -> List[Edge]:
        """Gets all edges connected to a node (incoming and outgoing).
        
        Args:
            node_id: Node ID
            
        Returns:
            List of all connected edges
        """
        return [e for e in self.edges 
                if e.source_id == node_id or e.target_id == node_id]
    
    def get_neighbors(self, node_id: str) -> Set[str]:
        """Gets the IDs of neighboring nodes.
        
        Args:
            node_id: Node ID
            
        Returns:
            Set of neighboring node IDs
        """
        neighbors = set()
        for edge in self.edges:
            if edge.source_id == node_id:
                neighbors.add(edge.target_id)
            elif edge.target_id == node_id:
                neighbors.add(edge.source_id)
        return neighbors
    
    def get_contradictory_edges(self) -> List[Edge]:
        """Gets all edges expressing contradictions.
        
        Returns:
            List of contradictory edges
        """
        return [e for e in self.edges if e.is_contradictory()]
    
    def get_causal_edges(self) -> List[Edge]:
        """Gets all causal edges.
        
        Returns:
            List of causal edges
        """
        return self.get_edges_by_layer("causal")
    
    def get_edges_by_layer(self, layer: str) -> List[Edge]:
        """Gets all edges of a specific layer."""
        valid_layers = {"causal", "epistemic", "structural", "temporal", "logical"}
        if layer not in valid_layers:
            raise ValueError(f"Invalid layer: {layer}. Must be one of {valid_layers}")
        return [e for e in self.edges if e.get_layer() == layer]
    
    def get_epistemic_edges(self) -> List[Edge]:
        """Gets all epistemic edges.
        
        Returns:
            List of epistemic edges
        """
        return self.get_edges_by_layer("epistemic")
    
    def get_structural_edges(self) -> List[Edge]:
        """Gets all structural edges.
        
        Returns:
            List of structural edges
        """
        return self.get_edges_by_layer("structural")
    
    def get_temporal_edges(self) -> List[Edge]:
        """Gets all temporal edges.
        
        Returns:
            List of temporal edges
        """
        return self.get_edges_by_layer("temporal")
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[Node]:
        """Gets all nodes of a specific type.
        
        Args:
            node_type: NodeType to filter by
            
        Returns:
            List of nodes matching the type
        """
        return [node for node in self.nodes.values() if node.node_type == node_type]
    
    def get_hypotheses(self) -> List[Node]:
        """Gets all hypothesis nodes.
        
        Returns:
            List of hypothesis nodes
        """
        return self.get_nodes_by_type(NodeType.HYPOTHESIS)
    
    def increment_version(self) -> None:
        """Increments the graph version.
        
        Used for temporal reasoning and versioning.
        """
        self.version += 1
        self._update_timestamp()
    
    def get_node_count(self) -> int:
        """Gets the number of nodes in the graph.
        
        Returns:
            Number of nodes
        """
        return len(self.nodes)
    
    def get_edge_count(self) -> int:
        """Gets the number of edges in the graph.
        
        Returns:
            Number of edges
        """
        return len(self.edges)
    
    def is_empty(self) -> bool:
        """Checks if the graph is empty.
        
        Returns:
            True if graph has no nodes
        """
        return len(self.nodes) == 0
    
    def _update_timestamp(self) -> None:
        """Internal method to update the timestamp."""
        self.updated_at = datetime.now()
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Graph(nodes={self.get_node_count()}, edges={self.get_edge_count()}, version={self.version})"