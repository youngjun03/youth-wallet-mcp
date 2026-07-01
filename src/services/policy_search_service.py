"""Policy search orchestration; transport remains in the client layer."""
from __future__ import annotations
from typing import Any
from src.clients.youth_wallet_client import YouthWalletClient, YouthWalletClientError
from src.schemas.policy import Policy

class PolicySearchService:
    def __init__(self, client: YouthWalletClient | None = None) -> None:
        self.client = client

    def search(self, query: str | None = None, region: str | None = None, category: str | None = None, page: int = 1, limit: int = 10) -> dict[str, Any]:
        if self.client is None:
            return {"ok": False, "error": "온통청년 API 키가 설정되지 않았습니다. YOUTH_CENTER_API_KEY 환경변수를 설정하세요.", "policies": []}
        try:
            response = self.client.search_policies(query=query, page=page, display=limit, keywords=[region] if region else None, policy_area_codes=[category] if category else None)
        except YouthWalletClientError as exc:
            return {"ok": False, "error": str(exc), "policies": []}
        records = self._find_records(response.get("data", {}))
        return {"ok": True, "policies": [self._to_policy(record).to_dict() for record in records], "source": response.get("endpoint")}

    def _find_records(self, node: Any) -> list[dict[str, Any]]:
        if isinstance(node, list):
            return [item for item in node if isinstance(item, dict)]
        if not isinstance(node, dict):
            return []
        for key in ("youthPolicy", "youthPlcy", "item", "list"):
            value = node.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
            if isinstance(value, dict):
                return [value]
        for value in node.values():
            found = self._find_records(value)
            if found:
                return found
        return []

    def _to_policy(self, record: dict[str, Any]) -> Policy:
        get = lambda *keys: next((str(record[key]) for key in keys if record.get(key) not in (None, "")), "")
        return Policy(
            policy_id=get("plcyNo", "policyId", "id"),
            name=get("plcyNm", "policyName", "name") or "정책명 미상",
            summary=get("plcyExplnCn", "summary", "description"),
            category=get("plcySprtCn", "category") or None,
            application_period=get("aplyYmd", "applicationPeriod") or None,
            application_url=get("aplyUrlAddr", "applicationUrl") or None,
            raw=record,
        )
