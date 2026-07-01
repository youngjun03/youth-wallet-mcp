from __future__ import annotations
import re
from src.schemas.policy import Policy
from src.schemas.requirements import PolicyRequirements

class RequirementExtractor:
    def extract(self, policy: Policy | dict) -> PolicyRequirements:
        data = policy.to_dict() if isinstance(policy, Policy) else policy
        text = " ".join([data.get("summary", ""), *data.get("requirements", [])])
        ages = [int(item) for item in re.findall(r"(\d{2})\s*세", text)]
        return PolicyRequirements(
            policy_id=data.get("policy_id", ""),
            age_min=data.get("age_min") or (min(ages) if ages else None),
            age_max=data.get("age_max") or (max(ages) if len(ages) > 1 else None),
            regions=[data["region"]] if data.get("region") else [],
            documents=["신분증", "주민등록초본 또는 등본"] if text else [],
            notes=[text] if text else [],
        )
