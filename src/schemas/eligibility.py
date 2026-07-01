from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass
class EligibilityResult:
    policy_id: str
    status: str
    matched_conditions: list[str] = field(default_factory=list)
    unmet_conditions: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    disclaimer: str = "최종 자격은 정책 공고 및 운영기관 확인이 필요합니다."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
