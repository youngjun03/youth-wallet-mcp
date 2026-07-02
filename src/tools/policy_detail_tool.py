#####################################
# FastMCP 청년정책 상세 조회 Tool 등록 #
#####################################

from typing import Annotated

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from services.policy_detail_service import PolicyDetailService


def register_policy_detail_tool(mcp: FastMCP) -> None:
    """
    get_youth_policy_detail MCP tool을 FastMCP 서버에 등록합니다.
    """

    @mcp.tool(
        name="get_youth_policy_detail",
        description=(
            "Get detailed information about a specific youth policy from Youth Center(온통청년) "
            "by policy name. Use this tool when the user asks for details, eligibility, "
            "application period, support content, or application method of a specific Korean youth policy."
        ),
        annotations=ToolAnnotations(
            title="Get Youth Policy Detail",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        ),
    )
    def get_youth_policy_detail(
        policy_name: Annotated[
            str,
            Field(
                description=(
                    "Youth policy name or partial policy name mentioned by the user. "
                    "Examples: '청년도약계좌', '청년월세지원', '드림', '청년내일채움공제'. "
                    "The tool searches the policy by name, finds its policy ID, "
                    "and then retrieves detailed policy information."
                ),
                min_length=1,
            ),
        ],
    ) -> dict:
        """
        정책명을 기준으로 청년정책 상세 정보를 조회하는 MCP tool입니다.
        """

        service = PolicyDetailService()

        return service.get_policy_detail_by_name(
            policy_name=policy_name,
        )