from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass
class Policy:
    policy_id: str
    name: str
    summary: str = ""
    category: str | None = None
    region: str | None = None
    age_min: int | None = None
    age_max: int | None = None
    application_period: str | None = None
    application_url: str | None = None
    requirements: list[str] = field(default_factory=list)
    benefits: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
