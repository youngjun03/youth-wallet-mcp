"""MCP tools for finding and reading Youth Wallet policies."""
from __future__ import annotations
from typing import Any
from src.services.policy_detail_service import PolicyDetailService
from src.services.policy_search_service import PolicySearchService

def register_policy_search_tools(mcp: Any, search_service: PolicySearchService, detail_service: PolicyDetailService) -> None:
    @mcp.tool(
        name="search_youth_policies",
        description="""Use when the user asks to find, recommend, browse, or list Korean youth policies, benefits, grants, housing support, jobs, education, startup, welfare, or finance programs. Examples: '서울 청년 월세 지원 찾아줘', '취준생 지원정책 뭐 있어?', '청년 대출 알려줘'. query is a concise Korean search phrase, not a full user profile. region is optional and should be a top-level Korean area such as '서울' or '경기'. category is an optional upstream policy-area code only when already known; otherwise omit it. page starts at 1 and limit is 1–50. This searches; it does not decide whether a user qualifies."""
    )
    def search_youth_policies(
        query: str | None = None, region: str | None = None, category: str | None = None,
        page: int = 1, limit: int = 10,
    ) -> dict[str, Any]:
        """Bridge the LLM's search intent to the policy-search service."""
        return search_service.search(query=query, region=region, category=category, page=page, limit=limit)

    @mcp.tool(
        name="get_youth_policy_detail",
        description="""Use after search_youth_policies when the user asks about one specific policy's details, application period, requirements, benefits, or link. policy_id must be the exact policy_id returned by search_youth_policies, not a policy name. Do not use for a broad recommendation request; search first."""
    )
    def get_youth_policy_detail(policy_id: str) -> dict[str, Any]:
        """Bridge one policy ID to the policy-detail service."""
        return detail_service.get_detail(policy_id)
