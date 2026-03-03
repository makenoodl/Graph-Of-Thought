from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ContradictionDTO(BaseModel):
    node1_id: str
    node2_id: Optional[str] = None
    description: Optional[str] = None
    detected_at: Optional[datetime] = None


class AnalysisSummaryDTO(BaseModel):
    blocked_paths: int = Field(default=0)
    viable_paths: int = Field(default=0)
    recommendation: str = Field(default="")
    contradiction_count: int = Field(default=0)

    @classmethod
    def simple_recommendation(
        cls,
        blocked_paths: int,
        viable_paths: int,
        contradiction_count: int,
    ) -> "AnalysisSummaryDTO":
        if viable_paths == 0 and blocked_paths > 0:
            recommendation = (
                "No viable path to the goal. Revisit constraints or consider alternatives."
            )
        elif viable_paths > 0 and contradiction_count == 0:
            recommendation = "Viable paths exist with no major contradictions."
        else:
            recommendation = "Some paths exist but the reasoning contains inconsistencies."

        return cls(
            blocked_paths=blocked_paths,
            viable_paths=viable_paths,
            recommendation=recommendation,
            contradiction_count=contradiction_count,
        )


class FullAnalysisDTO(BaseModel):
    contradictions: List[ContradictionDTO] = Field(default_factory=list)
    summary: AnalysisSummaryDTO