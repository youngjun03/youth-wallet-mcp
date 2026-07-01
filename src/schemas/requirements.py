from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass
class PolicyRequirements:
    policy_id: str
    age_min: int | None = None
    age_max: int | None = None
    regions: list[str] = field(default_factory=list)
    genders: list[str] = field(default_factory=list)
    employment_statuses: list[str] = field(default_factory=list)
    income_note: str | None = None
    documents: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
