from __future__ import annotations

from typing import List, Tuple

from got.domain.model.graph import Graph
from got.application.services.structure_text_service_llm import StructureTextServiceLLM


class CreateGraphFromTextUseCase:
    """
    Application use case: turn raw text into a domain Graph
    using the LLM-based StructureTextServiceLLM.
    """

    def __init__(self, service: StructureTextServiceLLM | None = None) -> None:
        self._service = service or StructureTextServiceLLM()

    def execute(self, text: str) -> Tuple[Graph, List[str]]:
        """
        Args:
            text: raw reasoning text

        Returns:
            (graph, starting_node_ids) built from the LLM graph spec.
        """
        return self._service.from_text(text)