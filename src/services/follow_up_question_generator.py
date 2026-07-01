from __future__ import annotations

class FollowUpQuestionGenerator:
    def generate(self, missing_information: list[str]) -> list[str]:
        prompts = {"만 나이": "현재 만 나이가 어떻게 되나요?", "거주 지역": "현재 주민등록상 거주 지역이 어디인가요?"}
        return [prompts.get(item, f"{item} 정보를 알려주세요.") for item in missing_information]
