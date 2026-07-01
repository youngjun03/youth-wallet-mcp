"""Youth Wallet MCP server entry point."""
from __future__ import annotations

import logging

try:
    from fastmcp import FastMCP
except ImportError:  # pragma: no cover - compatibility with the MCP Python SDK package
    from mcp.server.fastmcp import FastMCP
from src.clients.youth_wallet_client import YouthWalletClient
from src.config import settings
from src.services.application_checklist_builder import ApplicationChecklistBuilder
from src.services.eligibility_checker import EligibilityChecker
from src.services.follow_up_question_generator import FollowUpQuestionGenerator
from src.services.policy_comparator import PolicyComparator
from src.services.policy_detail_service import PolicyDetailService
from src.services.policy_search_service import PolicySearchService
from src.services.profile_parser import ProfileParser
from src.services.requirement_extractor import RequirementExtractor
from src.tools.checklist import register_checklist_tools
from src.tools.compare_tools import register_compare_tools
from src.tools.eligibility_tools import register_eligibility_tools
from src.tools.policy_search_tools import register_policy_search_tools
from src.tools.profile_tools import register_profile_tools

logger = logging.getLogger(__name__)

SERVER_INSTRUCTIONS = """
Youth Wallet helps Korean youth find public policies, structure user profiles,
check preliminary eligibility, compare policies, and prepare application checklists.
Use policy search/detail tools for factual policy data, then use profile and
eligibility tools only with facts explicitly provided by the user.
"""

def _create_fastmcp() -> FastMCP:
    """Create FastMCP across SDK versions."""
    try:
        return FastMCP(settings.mcp_server_name, instructions=SERVER_INSTRUCTIONS)
    except TypeError:
        return FastMCP(settings.mcp_server_name)

def create_server() -> FastMCP:
    """Create and wire the MCP server without exposing configuration secrets."""
    mcp = _create_fastmcp()
    client = YouthWalletClient(settings.youth_center_api_key) if settings.youth_center_api_key else None
    search_service = PolicySearchService(client)
    register_profile_tools(mcp, ProfileParser())
    register_policy_search_tools(mcp, search_service, PolicyDetailService(search_service))
    register_eligibility_tools(mcp, RequirementExtractor(), EligibilityChecker(), FollowUpQuestionGenerator())
    register_compare_tools(mcp, PolicyComparator())
    register_checklist_tools(mcp, ApplicationChecklistBuilder())
    return mcp

mcp = create_server()

def main() -> None:
    """Run the MCP server using environment-configured transport."""
    logging.basicConfig(level=logging.INFO)
    transport = settings.mcp_transport

    if transport == "stdio":
        logger.info("Starting %s MCP server over stdio", settings.mcp_server_name)
        mcp.run()
        return

    logger.info(
        "Starting %s MCP server over %s on %s:%s",
        settings.mcp_server_name,
        transport,
        settings.mcp_host,
        settings.mcp_port,
    )
    mcp.run(transport=transport, host=settings.mcp_host, port=settings.mcp_port)

if __name__ == "__main__":
    main()
