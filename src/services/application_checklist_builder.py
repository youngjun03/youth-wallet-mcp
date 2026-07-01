from __future__ import annotations
from src.schemas.checklist import ApplicationChecklist

class ApplicationChecklistBuilder:
    def build(self, policy: dict, additional_items: list[str] | None = None) -> ApplicationChecklist:
        items = ["공고의 신청 기간과 대상 조건을 확인", "본인 인증 수단을 준비", *policy.get("requirements", []), *(additional_items or [])]
        return ApplicationChecklist(policy_id=policy.get("policy_id", ""), items=list(dict.fromkeys(items)), application_url=policy.get("application_url"), application_period=policy.get("application_period"), notes=["제출 서류와 절차는 공고문 원문을 다시 확인하세요."])
