from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass
class ApplicationChecklist:
    policy_id: str
    items: list[str] = field(default_factory=list)
    application_url: str | None = None
    application_period: str | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
