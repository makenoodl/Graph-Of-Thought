

"""
graph_spec.py — LLM → Application contract (internal DTO)

This module defines the Pydantic schema for the JSON we REQUIRE from the LLM (OpenRouter).
Goals:
- Force a STRUCTURED output (nodes/edges/starting_node_ids) instead of free-form text.
- Validate the JSON (types, bounds, references) BEFORE building the domain Graph.
- Prevent hallucinated or incomplete JSON from creating an inconsistent graph.

DDD placement:
- Domain (got/domain): Graph/Node/Edge + validators/propagators/analyzers (deterministic core)
- Application (got/application): orchestration + I/O mapping
- graph_spec.py belongs to the Application layer and represents the boundary:
    LLM (interpreter) -> Application (Graph construction)
It should contain no business logic, only a data contract and validation rules.
"""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field, model_validator

from got.domain.model.value_objects import NodeType, RelationType


class NodeSpecDTO(BaseModel):
    id: str = Field(min_length=1)
    concept: str = Field(min_length=1)
    node_type: NodeType
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EdgeSpecDTO(BaseModel):
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    relation_type: RelationType
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphSpecDTO(BaseModel):
    nodes: List[NodeSpecDTO] = Field(default_factory=list)
    edges: List[EdgeSpecDTO] = Field(default_factory=list)
    starting_node_ids: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_references(self) -> "GraphSpecDTO":
        node_ids = {n.id for n in self.nodes}

        # starting_node_ids must refer to existing nodes
        missing_start = [nid for nid in self.starting_node_ids if nid not in node_ids]
        if missing_start:
            raise ValueError(f"starting_node_ids contains unknown node ids: {missing_start}")

        # edges must refer to existing nodes
        bad_edges = [
            (e.source_id, e.target_id, e.relation_type.value)
            for e in self.edges
            if e.source_id not in node_ids or e.target_id not in node_ids
        ]
        if bad_edges:
            raise ValueError(f"edges contain unknown node references: {bad_edges}")

        return self