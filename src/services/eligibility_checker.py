from __future__ import annotations
from src.schemas.eligibility import EligibilityResult
from src.schemas.profile import YouthProfile
from src.schemas.requirements import PolicyRequirements

class EligibilityChecker:
    def check(self, profile: YouthProfile, requirements: PolicyRequirements) -> EligibilityResult:
        matched, unmet, missing = [], [], []
        if requirements.age_min is not None or requirements.age_max is not None:
            if profile.age is None:
                missing.append("만 나이")
            elif requirements.age_min is not None and profile.age < requirements.age_min:
                unmet.append(f"최소 연령 {requirements.age_min}세")
            elif requirements.age_max is not None and profile.age > requirements.age_max:
                unmet.append(f"최대 연령 {requirements.age_max}세")
            else:
                matched.append("연령")
        if requirements.regions:
            if not profile.region:
                missing.append("거주 지역")
            elif profile.region not in requirements.regions:
                unmet.append("거주 지역")
            else:
                matched.append("거주 지역")
        status = "ineligible" if unmet else "needs_information" if missing else "likely_eligible"
        return EligibilityResult(requirements.policy_id, status, matched, unmet, missing)
