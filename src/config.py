"""Runtime configuration for the Youth Wallet MCP server."""
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    """Environment-backed settings. API keys are never returned by tools."""
    youth_center_api_key: str | None = os.getenv("YOUTH_CENTER_API_KEY")
    mcp_server_name: str = os.getenv("MCP_SERVER_NAME", "youth-wallet")
    mcp_host: str = os.getenv("MCP_HOST", "0.0.0.0")
    mcp_port: int = int(os.getenv("MCP_PORT", "8000"))
    mcp_transport: str = os.getenv("MCP_TRANSPORT", "stdio")

settings = Settings()
