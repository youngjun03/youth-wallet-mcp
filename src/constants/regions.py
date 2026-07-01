"""Korean top-level regions and common aliases."""
REGIONS = ("서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주")
REGION_ALIASES = {"서울시": "서울", "경기도": "경기", "제주도": "제주"}

def normalize_region(value: str | None) -> str | None:
    return None if value is None else REGION_ALIASES.get(value.strip(), value.strip())
