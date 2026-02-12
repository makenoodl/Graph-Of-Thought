from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ValidationViolation:
    code: str
    message: str
    node_ids: list[str]  # remplace par NodeId si tu l'as
    edge_ids: list[str]  # idem pour EdgeId


@dataclass(frozen=True)
class ValidationReport:
    violations: List[ValidationViolation]

    @property
    def is_valid(self) -> bool:
        return len(self.violations) == 0