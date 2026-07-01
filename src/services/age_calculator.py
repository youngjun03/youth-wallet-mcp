"""Date-of-birth based Korean international-age calculation."""
from __future__ import annotations
from datetime import date

class AgeCalculator:
    def calculate(self, birth_date: str, reference_date: str | None = None) -> int:
        born = date.fromisoformat(birth_date)
        today = date.fromisoformat(reference_date) if reference_date else date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
