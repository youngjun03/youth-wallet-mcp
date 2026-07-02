# 적합도 판단
########################################
# FastMCP 청년정책 신청 가능성 판단 Tool #
########################################

from typing import Annotated

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from services.policy_eligibility_service import PolicyEligibilityService


def register_policy_eligibility_tool(mcp: FastMCP) -> None:
    """
    check_policy_eligibility MCP tool을 FastMCP 서버에 등록합니다.
    """

    @mcp.tool(
        name="check_policy_eligibility",
        description=(
            "Check preliminary eligibility for a specific Korean youth policy from Youth Center(온통청년). "
            "Compare the user's profile conditions with the policy conditions. "
            "Use this tool when the user asks whether they can apply for a specific youth policy."
        ),
        annotations=ToolAnnotations(
            title="Check Policy Eligibility",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        ),
    )
    def check_policy_eligibility(
        policy_id: Annotated[
            str,
            Field(
                description=(
                    "Policy ID to check. Maps to the Youth Center API field plcyNo. "
                    "This is required. If the user only provides a policy name, "
                    "first use get_youth_policy_detail to find the policy ID."
                ),
                min_length=1,
            ),
        ],
        birth_date: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "User's birth date in YYYY-MM-DD format. "
                    "Used to calculate Korean legal age. "
                    "Example: '2001-03-15'."
                ),
            ),
        ] = None,
        age: Annotated[
            int | None,
            Field(
                default=None,
                description=(
                    "User's age in full years. If birth_date is provided, age can be omitted. "
                    "If both birth_date and age are provided, age is used directly."
                ),
                ge=0,
                le=120,
            ),
        ] = None,
        residence_region_code: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "User's resident registration region code. "
                    "Maps to regional eligibility conditions. "
                    "Example: '11000' for Seoul."
                ),
            ),
        ] = None,
        income_level: Annotated[
            int | None,
            Field(
                default=None,
                description=(
                    "User's income level. Usually means income percentile group or income bracket. "
                    "Example: 5 means 5th income level."
                ),
                ge=1,
                le=10,
            ),
        ] = None,
        monthly_income: Annotated[
            int | None,
            Field(
                default=None,
                description=(
                    "User's monthly income in KRW. "
                    "Example: 2500000 means 2,500,000 KRW per month."
                ),
                ge=0,
            ),
        ] = None,
        marriage_status: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "User's marriage status. "
                    "Example: '미혼', '기혼'."
                ),
            ),
        ] = None,
        job_code: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "User's employment status code or name. "
                    "Example: '미취업', '재직자', '자영업자', '구직자'."
                ),
            ),
        ] = None,
        school_code: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "User's education status code or name. "
                    "Example: '고졸', '대학생', '대졸', '재학생', '졸업생'."
                ),
            ),
        ] = None,
        major_code: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "User's major condition code or name. "
                    "Use this only when the policy requires a specific major."
                ),
            ),
        ] = None,
        special_condition_code: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "User's special condition code or name. "
                    "Example: '장기미취업청년', '청년가장', '취약계층'."
                ),
            ),
        ] = None,
    ) -> dict:
        """
        사용자 조건과 정책 조건을 비교해서 신청 가능성을 예비 판단합니다.
        """

        service = PolicyEligibilityService()

        return service.check_policy_eligibility(
            policy_id=policy_id,
            birth_date=birth_date,
            age=age,
            residence_region_code=residence_region_code,
            income_level=income_level,
            monthly_income=monthly_income,
            marriage_status=marriage_status,
            job_code=job_code,
            school_code=school_code,
            major_code=major_code,
            special_condition_code=special_condition_code,
        )