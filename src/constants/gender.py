"""Normalized gender values accepted by profile-related tools."""
GENDER_ALIASES = {
    "남": "male", "남성": "male", "male": "male",
    "여": "female", "여성": "female", "female": "female",
    "기타": "other", "other": "other",
    "무관": "unspecified", "미입력": "unspecified", "unspecified": "unspecified",
}

def normalize_gender(value: str | None) -> str | None:
    return None if value is None else GENDER_ALIASES.get(value.strip().lower(), value.strip().lower())
