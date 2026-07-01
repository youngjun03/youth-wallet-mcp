from __future__ import annotations
from typing import Any
from src.services.policy_search_service import PolicySearchService

class PolicyDetailService:
    def __init__(self, search_service: PolicySearchService) -> None:
        self.search_service = search_service

    def get_detail(self, policy_id: str) -> dict[str, Any]:
        result = self.search_service.search(query=policy_id, limit=20)
        for policy in result.get("policies", []):
            if policy.get("policy_id") == policy_id:
                return {"ok": True, "policy": policy}
        return {"ok": False, "error": "정책을 찾지 못했습니다. 정책 ID를 확인하세요."}
