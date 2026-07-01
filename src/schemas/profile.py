from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass
class YouthProfile:
    birth_date: str | None = None
    birth_year: int | None = None
    age: int | None = None
    region: str | None = None
    gender: str | None = None
    employment_status: str | None = None
    income_level: str | None = None
    interests: list[str] = field(default_factory=list)
    raw_text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
