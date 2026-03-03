from __future__ import annotations

import re
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from got.domain.model.graph import Graph
from got.domain.model.value_objects import Confidence, NodeType
from got.domain.ops import AddNode

from got.application.use_cases.analyze_reasoning import AnalyzeReasoningUseCase
from got.application.schemas.graph import GraphDTO
from got.application.schemas.analysis import AnalysisSummaryDTO


router = APIRouter(tags=["analysis"])


class AnalyzeTextRequest(BaseModel):
    text: str = Field(min_length=1)


class AnalyzeTextResponse(BaseModel):
    graph: GraphDTO
    analysis: AnalysisSummaryDTO


def _naive_text_to_graph(text: str) -> tuple[Graph, List[str]]:
    """
    V0 (no LLM): split text into sentences and create CONCEPT nodes.
    Returns (graph, starting_node_ids).
    """
    graph = Graph()
    add_node = AddNode()

    # Very simple sentence splitting
    parts = [p.strip() for p in re.split(r"[.\n]+", text) if p.strip()]

    starting_node_ids: list[str] = []
    for i, concept in enumerate(parts):
        ev = add_node.execute(
            graph,
            concept=concept,
            node_type=NodeType.CONCEPT,
            confidence=Confidence(0.5),
        )
        if i == 0:
            starting_node_ids.append(ev.node_id)

    return graph, starting_node_ids


@router.post("/analyze-text", response_model=AnalyzeTextResponse)
def analyze_text(payload: AnalyzeTextRequest) -> AnalyzeTextResponse:
    graph, starting_node_ids = _naive_text_to_graph(payload.text)

    uc = AnalyzeReasoningUseCase()
    result = uc.execute(graph, starting_node_ids=starting_node_ids, propagate_causal=False)

    return AnalyzeTextResponse(
        graph=GraphDTO.from_domain(result.graph),
        analysis=result.summary,
    )