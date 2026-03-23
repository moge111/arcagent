"""Tool registration wrapping claude-agent-sdk's @tool decorator and MCP server builder."""

from __future__ import annotations

import logging
from typing import Any

from claude_agent_sdk import SdkMcpTool, create_sdk_mcp_server

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for agent tools using SDK MCP server pattern."""

    def __init__(self) -> None:
        self._tools: list[SdkMcpTool[Any]] = []

    def register(self, tool: SdkMcpTool[Any]) -> None:
        """Register a tool created with @tool decorator."""
        self._tools.append(tool)
        logger.info("Registered tool: %s", tool.name)

    def build_mcp_server(self):
        """Build an MCP server config from all registered tools.

        Returns McpSdkServerConfig to pass to ClaudeAgentOptions.mcp_servers.
        Returns None if no tools registered.
        """
        if not self._tools:
            return None

        return create_sdk_mcp_server(
            name="arcagent",
            version="1.0.0",
            tools=self._tools,
        )

    def list_tools(self) -> list[dict]:
        """Return tool summaries for API/dashboard."""
        return [
            {"name": t.name, "description": t.description}
            for t in self._tools
        ]
