
#################################
# 청년정책 신청 가능성 판단 서비스 #
#################################

import re
from datetime import date, datetime

from services.policy_detail_service import PolicyDetailService


class PolicyEligibilityService:
    """
    사용자 조건과 정책 조건을 비교해서 신청 가능성을 예비 판단하는 서비스입니다.

    주의:
    온통청년 API의 일부 조건은 자연어 설명문으로 제공되기 때문에
    이 서비스의 결과는 '최종 확정'이 아니라 '예비 판단'입니다.
    """

    def __init__(self):
        self.policy_detail_service = PolicyDetailService()

    def _normalize_text(self, value) -> str:
        """
        비교를 쉽게 하기 위해 값을 문자열로 변환하고 공백을 정리합니다.
        """

        if value is None:
            return ""

        return str(value).strip()

    def _to_int(self, value) -> int | None:
        """
        문자열 또는 숫자를 int로 변환합니다.
        변환할 수 없으면 None을 반환합니다.
        """

        if value is None:
            return None

        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _calculate_age_from_birth_date(
        self,
        birth_date: str | None,
    ) -> int | None:
        """
        생년월일을 기준으로 만 나이를 계산합니다.

        birth_date 형식:
            YYYY-MM-DD
        """

        if birth_date is None:
            return None

        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
        except ValueError:
            return None

        today = date.today()

        age = today.year - birth.year

        # 생일이 아직 지나지 않았으면 1살 빼기
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1

        return age

    def _contains_no_limit_text(self, text: str) -> bool:
        """
        제한 없음으로 볼 수 있는 표현이 있는지 확인합니다.
        """

        no_limit_words = [
            "제한없음",
            "제한 없음",
            "무관",
            "해당없음",
            "해당 없음",
            "없음",
            "전국",
        ]

        for word in no_limit_words:
            if word in text:
                return True

        return False

    def _extract_age_condition_from_text(
        self,
        text: str,
    ) -> tuple[int | None, int | None]:
        """
        정책 설명문에서 만 나이 조건을 간단히 추출합니다.

        예:
            "만 19세 이상 만 34세 이하"
            -> min_age=19, max_age=34
        """

        min_age = None
        max_age = None

        min_match = re.search(r"만\s*(\d+)\s*세\s*이상", text)
        max_match = re.search(r"만\s*(\d+)\s*세\s*이하", text)

        if min_match:
            min_age = int(min_match.group(1))

        if max_match:
            max_age = int(max_match.group(1))

        return min_age, max_age

    def _check_age(
        self,
        user_age: int | None,
        policy: dict,
        raw_policy: dict,
    ) -> dict:
        """
        사용자 만 나이와 정책 나이 조건을 비교합니다.
        """

        if user_age is None:
            return {
                "name": "age",
                "status": "not_checked",
                "message": "사용자 나이가 제공되지 않아 나이 조건을 판단하지 않았습니다.",
            }

        min_age = self._to_int(policy.get("min_age"))
        max_age = self._to_int(policy.get("max_age"))

        # 상세 필드에 나이가 없으면 설명문에서 추출 시도
        if min_age is None and max_age is None:
            target_text = (
                self._normalize_text(policy.get("support_target"))
                + " "
                + self._normalize_text(policy.get("summary"))
                + " "
                + self._normalize_text(raw_policy.get("sprtTrgtCn"))
            )

            min_age, max_age = self._extract_age_condition_from_text(target_text)

        # 정책 나이 조건 자체를 못 찾은 경우
        if min_age is None and max_age is None:
            return {
                "name": "age",
                "status": "unknown",
                "message": "정책의 나이 조건을 명확히 찾지 못했습니다.",
                "user_value": user_age,
            }

        if min_age is not None and user_age < min_age:
            return {
                "name": "age",
                "status": "failed",
                "message": f"정책은 만 {min_age}세 이상을 요구하지만 사용자는 만 {user_age}세입니다.",
                "user_value": user_age,
                "policy_min_age": min_age,
                "policy_max_age": max_age,
            }

        if max_age is not None and user_age > max_age:
            return {
                "name": "age",
                "status": "failed",
                "message": f"정책은 만 {max_age}세 이하를 요구하지만 사용자는 만 {user_age}세입니다.",
                "user_value": user_age,
                "policy_min_age": min_age,
                "policy_max_age": max_age,
            }

        return {
            "name": "age",
            "status": "passed",
            "message": "나이 조건을 만족하는 것으로 보입니다.",
            "user_value": user_age,
            "policy_min_age": min_age,
            "policy_max_age": max_age,
        }

    def _check_region(
        self,
        residence_region_code: str | None,
        raw_policy: dict,
    ) -> dict:
        """
        사용자 거주지 코드와 정책 지역 조건을 비교합니다.
        """

        if residence_region_code is None:
            return {
                "name": "residence_region",
                "status": "not_checked",
                "message": "사용자 거주지 코드가 제공되지 않아 지역 조건을 판단하지 않았습니다.",
            }

        residence_region_code = self._normalize_text(residence_region_code)

        # API에서 지역 조건이 들어올 수 있는 후보 필드들
        region_text = " ".join(
            [
                self._normalize_text(raw_policy.get("zipCd")),
                self._normalize_text(raw_policy.get("rgonCd")),
                self._normalize_text(raw_policy.get("regionCd")),
                self._normalize_text(raw_policy.get("sprtTrgtCn")),
                self._normalize_text(raw_policy.get("plcySprtCn")),
                self._normalize_text(raw_policy.get("sprvsnInstCdNm")),
                self._normalize_text(raw_policy.get("operInstCdNm")),
            ]
        )

        if not region_text.strip():
            return {
                "name": "residence_region",
                "status": "unknown",
                "message": "정책의 지역 조건을 명확히 찾지 못했습니다.",
                "user_value": residence_region_code,
            }

        if self._contains_no_limit_text(region_text):
            return {
                "name": "residence_region",
                "status": "passed",
                "message": "지역 제한이 없거나 전국 단위 정책으로 보입니다.",
                "user_value": residence_region_code,
            }

        # 완전 코드 포함 여부 확인
        if residence_region_code in region_text:
            return {
                "name": "residence_region",
                "status": "passed",
                "message": "사용자 거주지 코드가 정책 지역 조건에 포함됩니다.",
                "user_value": residence_region_code,
            }

        # 광역 코드 비교
        # 예: 11000과 11680은 앞 두 자리가 11로 같으므로 서울 계열로 볼 수 있음
        if len(residence_region_code) >= 2:
            region_prefix = residence_region_code[:2]

            if region_prefix in region_text:
                return {
                    "name": "residence_region",
                    "status": "passed",
                    "message": "사용자 거주지와 정책 지역 조건의 광역 코드가 일치하는 것으로 보입니다.",
                    "user_value": residence_region_code,
                }

        return {
            "name": "residence_region",
            "status": "unknown",
            "message": "지역 조건이 존재하지만 코드만으로는 일치 여부를 확정하기 어렵습니다.",
            "user_value": residence_region_code,
            "policy_region_text": region_text,
        }

    def _check_income(
        self,
        income_level: int | None,
        monthly_income: int | None,
        policy: dict,
    ) -> dict:
        """
        사용자 소득 정보와 정책 소득 조건을 비교합니다.

        income_level:
            소득분위

        monthly_income:
            월소득. 단위는 원으로 가정합니다.
        """

        if income_level is None and monthly_income is None:
            return {
                "name": "income",
                "status": "not_checked",
                "message": "소득 정보가 제공되지 않아 소득 조건을 판단하지 않았습니다.",
            }

        income_text = self._normalize_text(policy.get("income_condition"))

        if not income_text:
            return {
                "name": "income",
                "status": "unknown",
                "message": "정책의 소득 조건을 명확히 찾지 못했습니다.",
                "user_income_level": income_level,
                "user_monthly_income": monthly_income,
            }

        if self._contains_no_limit_text(income_text):
            return {
                "name": "income",
                "status": "passed",
                "message": "소득 제한이 없거나 무관한 정책으로 보입니다.",
                "user_income_level": income_level,
                "user_monthly_income": monthly_income,
                "policy_income_text": income_text,
            }

        # 예: "5분위 이하"
        if income_level is not None:
            match = re.search(r"(\d+)\s*분위\s*이하", income_text)

            if match:
                max_income_level = int(match.group(1))

                if income_level <= max_income_level:
                    return {
                        "name": "income",
                        "status": "passed",
                        "message": f"정책은 {max_income_level}분위 이하를 요구하고 사용자는 {income_level}분위입니다.",
                        "user_income_level": income_level,
                        "policy_income_text": income_text,
                    }

                return {
                    "name": "income",
                    "status": "failed",
                    "message": f"정책은 {max_income_level}분위 이하를 요구하지만 사용자는 {income_level}분위입니다.",
                    "user_income_level": income_level,
                    "policy_income_text": income_text,
                }

        # 예: "300만원 이하"
        if monthly_income is not None:
            match = re.search(r"(\d+)\s*만\s*원\s*이하", income_text)

            if match:
                max_monthly_income = int(match.group(1)) * 10000

                if monthly_income <= max_monthly_income:
                    return {
                        "name": "income",
                        "status": "passed",
                        "message": f"정책은 월 {max_monthly_income:,}원 이하를 요구하고 사용자는 월 {monthly_income:,}원입니다.",
                        "user_monthly_income": monthly_income,
                        "policy_income_text": income_text,
                    }

                return {
                    "name": "income",
                    "status": "failed",
                    "message": f"정책은 월 {max_monthly_income:,}원 이하를 요구하지만 사용자는 월 {monthly_income:,}원입니다.",
                    "user_monthly_income": monthly_income,
                    "policy_income_text": income_text,
                }

        return {
            "name": "income",
            "status": "unknown",
            "message": "소득 조건이 존재하지만 자동으로 확정 판단하기 어렵습니다.",
            "user_income_level": income_level,
            "user_monthly_income": monthly_income,
            "policy_income_text": income_text,
        }

    def _check_text_condition(
        self,
        name: str,
        user_value: str | None,
        policy_text: str,
        label: str,
    ) -> dict:
        """
        취업상태, 학력, 전공, 특화조건처럼 텍스트 기반으로 비교하는 공통 함수입니다.
        """

        if user_value is None:
            return {
                "name": name,
                "status": "not_checked",
                "message": f"사용자의 {label} 정보가 제공되지 않아 판단하지 않았습니다.",
            }

        user_value = self._normalize_text(user_value)
        policy_text = self._normalize_text(policy_text)

        if not policy_text:
            return {
                "name": name,
                "status": "unknown",
                "message": f"정책의 {label} 조건을 명확히 찾지 못했습니다.",
                "user_value": user_value,
            }

        if self._contains_no_limit_text(policy_text):
            return {
                "name": name,
                "status": "passed",
                "message": f"{label} 제한이 없거나 무관한 정책으로 보입니다.",
                "user_value": user_value,
                "policy_text": policy_text,
            }

        if user_value in policy_text:
            return {
                "name": name,
                "status": "passed",
                "message": f"사용자의 {label} 정보가 정책 조건에 포함됩니다.",
                "user_value": user_value,
                "policy_text": policy_text,
            }

        return {
            "name": name,
            "status": "unknown",
            "message": f"{label} 조건이 존재하지만 자동으로 확정 판단하기 어렵습니다.",
            "user_value": user_value,
            "policy_text": policy_text,
        }

    def check_policy_eligibility(
        self,
        policy_id: str,
        birth_date: str | None = None,
        age: int | None = None,
        residence_region_code: str | None = None,
        income_level: int | None = None,
        monthly_income: int | None = None,
        marriage_status: str | None = None,
        job_code: str | None = None,
        school_code: str | None = None,
        major_code: str | None = None,
        special_condition_code: str | None = None,
    ) -> dict:
        """
        사용자 조건과 정책 조건을 비교하여 신청 가능성을 예비 판단합니다.
        """

        # 1. 정책 상세 정보 조회
        detail_result = self.policy_detail_service.get_policy_detail_by_id(
            policy_id=policy_id,
        )

        if not detail_result.get("success"):
            return {
                "success": False,
                "message": "정책 정보를 조회하지 못해 신청 가능성을 판단할 수 없습니다.",
                "policy_id": policy_id,
                "eligibility": "unknown",
                "checks": [],
            }

        policy = detail_result["policy"]
        raw_policy = policy.get("raw", {})

        # 2. age가 없고 birth_date가 있으면 생년월일로 만 나이 계산
        user_age = age

        if user_age is None:
            user_age = self._calculate_age_from_birth_date(
                birth_date=birth_date,
            )

        # 3. 조건별 판단
        checks = []

        checks.append(
            self._check_age(
                user_age=user_age,
                policy=policy,
                raw_policy=raw_policy,
            )
        )

        checks.append(
            self._check_region(
                residence_region_code=residence_region_code,
                raw_policy=raw_policy,
            )
        )

        checks.append(
            self._check_income(
                income_level=income_level,
                monthly_income=monthly_income,
                policy=policy,
            )
        )

        checks.append(
            self._check_text_condition(
                name="marriage_status",
                user_value=marriage_status,
                policy_text=self._normalize_text(raw_policy.get("mrgSttsCdNm")),
                label="결혼 상태",
            )
        )

        checks.append(
            self._check_text_condition(
                name="job",
                user_value=job_code,
                policy_text=(
                    self._normalize_text(policy.get("employment_condition"))
                    + " "
                    + self._normalize_text(raw_policy.get("jobCd"))
                    + " "
                    + self._normalize_text(raw_policy.get("jobCdNm"))
                ),
                label="취업 상태",
            )
        )

        checks.append(
            self._check_text_condition(
                name="school",
                user_value=school_code,
                policy_text=(
                    self._normalize_text(policy.get("education_condition"))
                    + " "
                    + self._normalize_text(raw_policy.get("schoolCd"))
                    + " "
                    + self._normalize_text(raw_policy.get("schoolCdNm"))
                ),
                label="학력",
            )
        )

        checks.append(
            self._check_text_condition(
                name="major",
                user_value=major_code,
                policy_text=(
                    self._normalize_text(raw_policy.get("majrCd"))
                    + " "
                    + self._normalize_text(raw_policy.get("majrCdNm"))
                ),
                label="전공",
            )
        )

        checks.append(
            self._check_text_condition(
                name="special_condition",
                user_value=special_condition_code,
                policy_text=(
                    self._normalize_text(policy.get("special_condition"))
                    + " "
                    + self._normalize_text(raw_policy.get("sBizCd"))
                    + " "
                    + self._normalize_text(raw_policy.get("sBizCdNm"))
                ),
                label="특화 조건",
            )
        )

        # 4. 최종 상태 결정
        failed_checks = [
            check for check in checks
            if check["status"] == "failed"
        ]

        unknown_checks = [
            check for check in checks
            if check["status"] == "unknown"
        ]

        passed_checks = [
            check for check in checks
            if check["status"] == "passed"
        ]

        if failed_checks:
            eligibility = "unlikely"
            message = "일부 조건을 만족하지 못해 신청이 어려울 가능성이 있습니다."
        elif unknown_checks:
            eligibility = "needs_review"
            message = "확정 판단이 어려운 조건이 있어 추가 확인이 필요합니다."
        else:
            eligibility = "likely"
            message = "제공된 정보 기준으로는 신청 가능성이 있어 보입니다."

        return {
            "success": True,
            "message": message,
            "policy_id": policy_id,
            "policy": {
                "title": policy.get("title"),
                "summary": policy.get("summary"),
                "support_target": policy.get("support_target"),
                "income_condition": policy.get("income_condition"),
                "application_period": policy.get("application_period"),
                "application_url": policy.get("application_url"),
            },
            "user_profile": {
                "birth_date": birth_date,
                "age": user_age,
                "residence_region_code": residence_region_code,
                "income_level": income_level,
                "monthly_income": monthly_income,
                "marriage_status": marriage_status,
                "job_code": job_code,
                "school_code": school_code,
                "major_code": major_code,
                "special_condition_code": special_condition_code,
            },
            "eligibility": eligibility,
            "summary": {
                "passed_count": len(passed_checks),
                "failed_count": len(failed_checks),
                "unknown_count": len(unknown_checks),
            },
            "checks": checks,
            "notice": "이 결과는 API 정보와 사용자가 제공한 정보를 기반으로 한 예비 판단입니다. 실제 신청 가능 여부는 정책 공고문과 운영기관 확인이 필요합니다.",
        }