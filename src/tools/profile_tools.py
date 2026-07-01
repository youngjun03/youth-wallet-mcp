"""MCP tools for extracting a structured youth profile."""
from __future__ import annotations
from typing import Any
from src.schemas.profile import YouthProfile
from src.services.profile_parser import ProfileParser

def register_profile_tools(mcp: Any, parser: ProfileParser) -> None:
    @mcp.tool(
        name="extract_youth_profile",
        description="""Use when the user describes themselves in free-form Korean and you need structured eligibility/search facts. Typical intents: '나는 2001년생 서울 거주 취준생인데', '내 조건으로 지원금 찾아줘'. Pass the user's original statement as text without summarizing away dates, location, job status, or interests. Returns birth_date (YYYY-MM-DD when found), birth_year for expressions such as '03년생', exact international age only when calculable, region, gender, employment_status, income_level, and interests. This tool extracts facts only; it does not search policies or determine final eligibility."""
    )
    def extract_youth_profile(text: str) -> dict[str, Any]:
        """Convert one user's free-form self-description into a reusable profile."""
        return parser.parse(text).to_dict()

    @mcp.tool(
        name="build_youth_profile",
        description="""Use when the conversation already contains explicit profile fields and a normalized profile object is needed for another tool. Do not call to infer missing facts. birth_date must be YYYY-MM-DD if supplied; birth_year is a four-digit year when only the year is known; age is an exact international age as an integer; region should be a Korean top-level region such as '서울' or '경기'; interests is a list of short strings. All fields are optional, but include every fact known from the user."""
    )
    def build_youth_profile(
        birth_date: str | None = None, birth_year: int | None = None, age: int | None = None,
        region: str | None = None, gender: str | None = None,
        employment_status: str | None = None, income_level: str | None = None,
        interests: list[str] | None = None,
    ) -> dict[str, Any]:
        """Return a validated, tool-ready profile without making policy judgments."""
        return YouthProfile(birth_date=birth_date, birth_year=birth_year, age=age, region=region, gender=gender, employment_status=employment_status, income_level=income_level, interests=interests or []).to_dict()
