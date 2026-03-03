from __future__ import annotations

import json
from typing import List, Tuple

from got.domain.model.graph import Graph
from got.domain.model.node import Node
from got.domain.model.edge import Edge
from got.domain.model.value_objects import Confidence
from got.domain.ops import AddNode, AddEdge

from got.application.schemas.graph_spec import GraphSpecDTO
from got.application.services.openrouter import OpenRouterClient, OpenRouterError


class StructureTextServiceLLM:
    """
    Text -> Graph via LLM (OpenRouter).

    Pipeline:
    1) Build a strict JSON-only prompt (system + user)
    2) Call OpenRouterClient.chat_json(...)
    3) json.loads(content) -> dict
    4) GraphSpecDTO.model_validate(dict) -> spec
    5) Build a domain Graph via AddNode / AddEdge

    Returns:
        (graph, starting_node_ids)
    """

    def __init__(self, client: OpenRouterClient | None = None) -> None:
        self._client = client or OpenRouterClient()
        self._add_node = AddNode()
        self._add_edge = AddEdge()

    def from_text(self, text: str) -> Tuple[Graph, List[str]]:
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(text)

        try:
            content = self._client.chat_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.0,
                max_tokens=1500,
            )
        except OpenRouterError as e:
            # For now, re-raise; later you can add fallbacks/logging
            raise

        try:
            raw_spec = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM did not return valid JSON: {content[:500]}") from e

        spec = GraphSpecDTO.model_validate(raw_spec)

        graph = Graph()
        id_map: dict[str, str] = {}

    

        # Simpler version: build graph directly without using AddNode events
        graph = Graph()
        for node_spec in spec.nodes:
            node = Node(
                concept=node_spec.concept,
                node_type=node_spec.node_type,
                confidence=Confidence.from_float(node_spec.confidence),
                metadata=node_spec.metadata,
            )
            graph.add_node(node)
            id_map[node_spec.id] = node.id

        # 2) Create edges
        for edge_spec in spec.edges:
            source_id = id_map[edge_spec.source_id]
            target_id = id_map[edge_spec.target_id]
            edge = Edge(
                source_id=source_id,
                target_id=target_id,
                relation_type=edge_spec.relation_type,
                confidence=Confidence.from_float(edge_spec.confidence),
                metadata=edge_spec.metadata,
            )
            graph.add_edge(edge)

        # 3) Map starting_node_ids
        starting_node_ids: List[str] = []
        for nid in spec.starting_node_ids:
            if nid in id_map:
                starting_node_ids.append(id_map[nid])

        return graph, starting_node_ids

    def _build_system_prompt(self) -> str:
        return (
            "You are a Graph-of-Thought structurer. "
            "Given a business reasoning text, you MUST return ONLY a JSON object with this exact schema:\n"
            "{\n"
            '  "nodes": [\n'
            "    {\n"
            '      "id": "n1",\n'
            '      "concept": "string",\n'
            '      "node_type": "goal|solution|problem|constraint|fact|hypothesis|concept|state",\n'
            '      "confidence": 0.0-1.0,\n'
            '      "metadata": { "source": "..." }\n'
            "    }\n"
            "  ],\n"
            '  "edges": [\n'
            "    {\n"
            '      "source_id": "n1",\n'
            '      "target_id": "n2",\n'
            '      "relation_type": "requires|depends_on|causes|enables|prevents|supports|contradicts|weakens|strengthens|evidence_for|evidence_against|explains|contains|part_of|similar_to|instance_of|type_of|implements|precedes|follows",\n'
            '      "confidence": 0.0-1.0,\n'
            '      "metadata": {}\n'
            "    }\n"
            "  ],\n"
            '  "starting_node_ids": ["n1"]\n'
            "}\n"
            "No explanations, no prose, no markdown. JSON ONLY."
        )

    def _build_user_prompt(self, text: str) -> str:
        return (
            "Transform the following reasoning text into a graph-of-thought.\n"
            "- Identify at least one GOAL node if possible.\n"
            "- Identify SOLUTION(S), PROBLEM(S), CONSTRAINT(S), FACT(S), HYPOTHESIS nodes.\n"
            "- Create edges that represent requires/depends_on/causes/supports/contradicts, etc.\n"
            "- starting_node_ids should usually contain the main GOAL node id.\n\n"
            f"Text:\n{text}\n"
        )