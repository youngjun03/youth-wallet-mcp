#####################################
# FastMCP 청년정책 검색 Tool 등록 파일 #
#####################################

from typing import Annotated, Literal

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from services.policy_search_service import PolicyAPIService

# 정책 검색에 사용할 수 있는 키워드 목록
PolicyKeyword = Literal[
    "대출",
    "보조금",
    "바우처",
    "금리혜택",
    "교육지원",
    "맞춤형상담서비스",
    "인턴",
    "벤처",
    "중소기업",
    "청년가장",
    "장기미취업청년",
    "공공임대주택",
    "신용회복",
    "육아",
    "출산",
    "해외진출",
    "주거지원",
]

def register_search_policy_tool(mcp: FastMCP) -> None:
    """
    search_youth_policies MCP tool을 FastMCP 서버에 등록하는 함수

    server.py에서 이 함수를 호출하면,
    search_youth_policies tool이 MCP 서버에 추가됨
    """

    @mcp.tool(
        name="search_youth_policies",
        description=(
            "Search youth policies from Youth Center(온통청년) by keyword, "
            "policy name, description keyword, region code, and policy category. "
            "Use this tool when the user wants to find Korean youth policies."
        ),
        annotations=ToolAnnotations(
            title="Search Youth Policies",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        ),
    )

    def search_youth_policies(
        keyword: Annotated[
            PolicyKeyword | None,
            Field(
                default=None,
                description=(
                    "Policy keyword. Maps to the Youth Center API field plcyKywdNm. "
                    "Choose exactly one value from the allowed Youth Center keywords when possible. "
                    "Allowed values: 대출, 보조금, 바우처, 금리혜택, 교육지원, 맞춤형상담서비스, "
                    "인턴, 벤처, 중소기업, 청년가장, 장기미취업청년, 공공임대주택, 신용회복, "
                    "육아, 출산, 해외진출, 주거지원. "
                    "Infer the closest keyword from the user's natural language request. "
                    "For example, 월세, 전세, 임대, 집, 주택, 자취, 보증금 -> 주거지원. "
                    "학원, 강의, 공부, 교육, 수업 -> 교육지원. "
                    "취업 경험, 현장실습, 일경험 -> 인턴. "
                    "창업, 스타트업 -> 벤처. "
                    "대출, 돈 빌리기 -> 대출. "
                    "이자, 금리 -> 금리혜택. "
                    "아이, 양육 -> 육아. "
                    "출산, 임신 -> 출산. "
                    "If no clear keyword can be inferred, leave this as null."
                ),
            ),
        ] = None,
        policy_name: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Policy name search term. Maps to the Youth Center API field plcyNm. "
                    "Use this when the user mentions a specific policy name or partial name. "
                    "Example: '드림', '청년도약계좌', '월세지원'."
                ),
            ),
        ] = None,
        description_keyword: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Keyword to search inside the policy description. "
                    "Maps to the Youth Center API field plcyExplnCn. "
                    "Use this when the user describes what the policy is about."
                ),
            ),
        ] = None,
        region_code: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Five-digit legal district code. Maps to the Youth Center API field zipCd. "
                    "Only use this if the exact code is known. "
                    "Example: '11000' for Seoul, '11680' for Gangnam-gu."
                ),
            ),
        ] = None,
        category_major: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Major policy category name. Maps to the Youth Center API field lclsfNm. "
                    "Example: '일자리', '주거', '교육', '복지문화'."
                ),
            ),
        ] = None,
        category_middle: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "Middle policy category name. Maps to the Youth Center API field mclsfNm. "
                    "Use this only when the user clearly specifies a middle category."
                ),
            ),
        ] = None,
        page: Annotated[
            int,
            Field(
                default=1,
                description="Page number. Maps to the Youth Center API field pageNum.",
                ge=1,
            ),
        ] = 1,
        page_size: Annotated[
            int,
            Field(
                default=5,
                description="Number of policies per page. Maps to the Youth Center API field pageSize.",
                ge=1,
                le=20,
            ),
        ] = 5,
    ) -> dict:
        """
        청년정책을 검색하는 MCP tool입니다.

        LLM은 사용자의 자연어 요청을 보고
        keyword, policy_name, description_keyword 등 적절한 파라미터에 값을 넣습니다.

        실제 API 호출은 PolicyAPIService가 담당합니다.
        """

        service = PolicyAPIService()

        result = service.search_youth_policies(
            keyword=keyword,
            policy_name=policy_name,
            description_keyword=description_keyword,
            region_code=region_code,
            category_major=category_major,
            category_middle=category_middle,
            page=page,
            page_size=page_size,
        )

        return result