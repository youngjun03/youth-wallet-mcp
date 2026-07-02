#####################################
# FastMCP 청년정책 검색 Tool 등록 파일 #
#####################################

from typing import Annotated, Literal

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from services.policy_search_service import PolicyAPIService
from services.region_code_service import RegionCodeService

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

# 대분류 정책 카테고리 목록
PolicyCategoryMajor = Literal[
    "일자리",
    "주거",
    "교육",
    "복지문화",
    "참여권리",
]

# 중분류 정책 카테고리 목록
PolicyCategoryMiddle = Literal[
    "취업",
    "재직자",
    "창업",
    "주택 및 거주지",
    "기숙사",
    "전월세 및 주거급여 지원",
    "미래역량강화",
    "교육비지원",
    "온라인교육",
    "취약계층 및 금융지원",
    "건강",
    "예술인지원",
    "문화활동",
    "청년참여",
    "정책인프라구축",
    "청년국제교류",
    "권익보호",
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
        region_name: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "User's residential region name in Korean. "
                    "Use this when the user mentions where they live. "
                    "Examples: '서울', '서울특별시', '경기', '경기도', '부산'. "
                    "This value will be converted to the Youth Center API zipCd region code using region_codes.csv. "
                    "If the user does not mention a region, leave this as null."
                ),
            ),
        ] = None,
        category_major: Annotated[
            PolicyCategoryMajor | None,
            Field(
                default=None,
                description=(
                    "Major policy category name. Maps to the Youth Center API field lclsfNm. "
                    "Choose exactly one value from the allowed major categories when possible. "
                    "Allowed values: 일자리, 주거, 교육, 복지문화, 참여권리. "
                    "Infer the closest category from the user's natural language request. "
                    "For example, 취업, 채용, 인턴, 창업, 일경험 -> 일자리. "
                    "월세, 전세, 임대주택, 자취, 보증금 -> 주거. "
                    "강의, 수업, 학원, 자격증, 대학, 장학금 -> 교육. "
                    "문화생활, 건강, 복지, 상담, 생활지원 -> 복지문화. "
                    "정책참여, 권리, 청년위원회, 의견제안 -> 참여권리. "
                    "If no clear major category can be inferred, leave this as null."
                ),
            ),
        ] = None,
        category_middle: Annotated[
            PolicyCategoryMiddle | None,
            Field(
                default=None,
                description=(
                    "Middle policy category name. Maps to the Youth Center API field mclsfNm. "
                    "Choose exactly one value from the allowed middle categories when possible. "
                    "Allowed values: 취업, 재직자, 창업, 주택 및 거주지, 기숙사, "
                    "전월세 및 주거급여 지원, 미래역량강화, 교육비지원, 온라인교육, "
                    "취약계층 및 금융지원, 건강, 예술인지원, 문화활동, 청년참여, "
                    "정책인프라구축, 청년국제교류, 권익보호. "
                    "Infer the closest middle category from the user's natural language request. "
                    "For example, 취업, 채용, 구직, 면접 -> 취업. "
                    "회사원, 직장인, 재직 중, 이직 -> 재직자. "
                    "창업, 스타트업, 사업 -> 창업. "
                    "월세, 전세, 자취, 임대, 보증금, 집 -> 전월세 및 주거급여 지원. "
                    "기숙사, dormitory -> 기숙사. "
                    "주택, 거주지, 공공임대주택 -> 주택 및 거주지. "
                    "자격증, 역량, 스펙, 교육훈련 -> 미래역량강화. "
                    "등록금, 학비, 교육비 -> 교육비지원. "
                    "온라인 강의, 인터넷 강의 -> 온라인교육. "
                    "대출, 금융, 저소득, 취약계층 -> 취약계층 및 금융지원. "
                    "운동, 병원, 마음건강, 심리상담 -> 건강. "
                    "예술인, 창작자, 작가, 음악 -> 예술인지원. "
                    "문화생활, 공연, 영화, 여행 -> 문화활동. "
                    "청년정책 참여, 위원회, 의견제안 -> 청년참여. "
                    "정책 기반, 센터, 플랫폼 -> 정책인프라구축. "
                    "해외, 국제교류, 유학, 글로벌 -> 청년국제교류. "
                    "권리, 노동권, 보호, 피해지원 -> 권익보호. "
                    "If no clear middle category can be inferred, leave this as null."
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
            region_name=region_name,
            category_major=category_major,
            category_middle=category_middle,
            page=page,
            page_size=page_size,
        )

        return result