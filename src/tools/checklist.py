"""MCP tool for turning a selected policy into application preparation steps."""
from __future__ import annotations
from typing import Any
from src.services.application_checklist_builder import ApplicationChecklistBuilder

def register_checklist_tools(mcp: Any, builder: ApplicationChecklistBuilder) -> None:
    @mcp.tool(
        name="build_policy_application_checklist",
        description="""Use when the user has selected a specific policy and asks what to prepare, how to apply, required documents, or a to-do list. policy must be one complete policy object from get_youth_policy_detail or search_youth_policies, not just its ID or title. additional_items is optional and only for user-stated requirements already known. This organizes a checklist; it never claims a document is officially required unless it appears in policy data."""
    )
    def build_policy_application_checklist(policy: dict[str, Any], additional_items: list[str] | None = None) -> dict[str, Any]:
        """Bridge one selected policy to the checklist builder."""
        return builder.build(policy, additional_items).to_dict()
