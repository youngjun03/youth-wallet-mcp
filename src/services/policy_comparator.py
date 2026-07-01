from __future__ import annotations

class PolicyComparator:
    def compare(self, policies: list[dict]) -> dict:
        fields = ("name", "summary", "category", "application_period", "application_url", "benefits", "requirements")
        return {"count": len(policies), "policies": [{field: policy.get(field) for field in fields} | {"policy_id": policy.get("policy_id")} for policy in policies]}
