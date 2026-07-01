########################
# FastMCP 서버 실행 파일 #
########################

from fastmcp import FastMCP

from tools.search_policy_tool import register_search_policy_tool


# MCP 서버 생성
# 주의: PlayMCP 기준상 server name이나 tool name에 kakao를 넣으면 안 됩니다.
mcp = FastMCP("YouthWalletPolicyServer")


# search_youth_policies tool 등록
register_search_policy_tool(mcp)


if __name__ == "__main__":
    # HTTP 방식으로 MCP 서버 실행
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        stateless_http=True,
    )