"""MCP tool for factual side-by-side comparison."""
from __future__ import annotations
from typing import Any
from src.services.policy_comparator import PolicyComparator

def register_compare_tools(mcp: Any, comparator: PolicyComparator) -> None:
    @mcp.tool(
        name="compare_youth_policies",
        description="""Use when the user explicitly asks to compare two or more already identified policies: 'A와 B 차이', '어느 쪽이 더 나아?', '조건과 신청기간 비교해줘'. policies must be a JSON list containing 2 or more policy objects returned by a search/detail tool. Do not pass policy names or IDs alone. This returns factual fields for the LLM to explain in the user's context; it does not silently select a winner."""
    )
    def compare_youth_policies(policies: list[dict[str, Any]]) -> dict[str, Any]:
        """Bridge policy objects to the comparison service."""
        if len(policies) < 2:
            return {"ok": False, "error": "비교하려면 정책 객체가 최소 2개 필요합니다."}
        return {"ok": True, **comparator.compare(policies)}
