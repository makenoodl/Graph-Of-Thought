from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from got.application.use_cases.create_graph_from_text import CreateGraphFromTextUseCase
from got.application.use_cases.analyze_reasoning import AnalyzeReasoningUseCase
from got.application.schemas.graph import GraphDTO
from got.application.schemas.analysis import AnalysisSummaryDTO


router = APIRouter(tags=["analysis"])


class AnalyzeTextRequest(BaseModel):
    text: str = Field(min_length=1)


class AnalyzeTextResponse(BaseModel):
    graph: GraphDTO
    analysis: AnalysisSummaryDTO


@router.post("/analyze-text", response_model=AnalyzeTextResponse)
def analyze_text(payload: AnalyzeTextRequest) -> AnalyzeTextResponse:
    # 1) Texte -> Graph (via LLM)
    graph, starting_node_ids = CreateGraphFromTextUseCase().execute(payload.text)

    # 2) Raisonnement structurel complet
    uc = AnalyzeReasoningUseCase()
    result = uc.execute(
        graph=graph,
        starting_node_ids=starting_node_ids,
        propagate_causal=False,
    )

    # 3) Mapping vers DTO pour l’API
    return AnalyzeTextResponse(
        graph=GraphDTO.from_domain(result.graph),
        analysis=result.summary,
    )