"""Small deterministic parser; the LLM supplies the natural-language understanding."""
from __future__ import annotations
import re
from datetime import date
from src.constants.gender import normalize_gender
from src.constants.regions import REGIONS, normalize_region
from src.schemas.profile import YouthProfile
from src.services.age_calculator import AgeCalculator

class ProfileParser:
    def __init__(self, age_calculator: AgeCalculator | None = None) -> None:
        self.age_calculator = age_calculator or AgeCalculator()

    def parse(self, text: str) -> YouthProfile:
        birth_match = re.search(r"(19\d{2}|20\d{2})[.\-/년\s]+(\d{1,2})[.\-/월\s]+(\d{1,2})", text)
        birth_date, birth_year, age = None, None, None
        if birth_match:
            year, month, day = (int(value) for value in birth_match.groups())
            birth_year, birth_date = year, f"{year:04d}-{month:02d}-{day:02d}"
            try:
                age = self.age_calculator.calculate(birth_date)
            except ValueError:
                birth_date = None
        if birth_year is None:
            year_match = re.search(r"(?<!\d)((?:19|20)\d{2}|\d{2})\s*년생", text)
            if year_match:
                value = int(year_match.group(1))
                birth_year = value if value >= 100 else (2000 + value if value <= date.today().year % 100 else 1900 + value)
        explicit_age = re.search(r"(\d{1,2})\s*세", text)
        if age is None and explicit_age:
            age = int(explicit_age.group(1))
        region = next((normalize_region(item) for item in REGIONS if item in text), None)
        gender = "male" if any(word in text for word in ("남성", "남자", " 남 ")) else None
        gender = "female" if any(word in text for word in ("여성", "여자", " 여 ")) else gender
        employment = next((item for item in ("재직", "취업준비", "구직", "학생", "프리랜서", "자영업") if item in text), None)
        income = re.search(r"([1-9]|10)\s*분위", text)
        interests = [item for item in ("주거", "취업", "일자리", "교육", "창업", "금융", "문화", "복지") if item in text]
        return YouthProfile(
            birth_date=birth_date, birth_year=birth_year, age=age, region=region,
            gender=normalize_gender(gender), employment_status=employment,
            income_level=income.group(1) + "분위" if income else None,
            interests=interests, raw_text=text,
        )
