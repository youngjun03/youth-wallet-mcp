"""MCP tools for a transparent preliminary eligibility check."""
from __future__ import annotations
from typing import Any
from src.schemas.profile import YouthProfile
from src.services.eligibility_checker import EligibilityChecker
from src.services.follow_up_question_generator import FollowUpQuestionGenerator
from src.services.requirement_extractor import RequirementExtractor

def register_eligibility_tools(mcp: Any, extractor: RequirementExtractor, checker: EligibilityChecker, questions: FollowUpQuestionGenerator) -> None:
    @mcp.tool(
        name="check_policy_eligibility",
        description="""Use when the user asks whether they can apply for a particular policy: '나도 받을 수 있어?', '조건이 되나?', '내 상황에서 신청 가능해?'. profile must be the complete object returned by extract_youth_profile or build_youth_profile. policy must be the single policy object returned by get_youth_policy_detail or search_youth_policies. Never invent profile facts. The result is a preliminary likelihood only, not an official eligibility decision."""
    )
    def check_policy_eligibility(profile: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
        """Pass an already-known profile and policy to the eligibility services."""
        result = checker.check(YouthProfile(**profile), extractor.extract(policy))
        payload = result.to_dict()
        if result.missing_information:
            payload["follow_up_questions"] = questions.generate(result.missing_information)
        return payload
