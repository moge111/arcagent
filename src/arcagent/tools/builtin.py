"""Built-in tools for ArcAgent."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx
from claude_agent_sdk import tool

from ..security.network import validate_url


@tool("current_time", "Get the current UTC date and time", {})
async def current_time(args: dict[str, Any]) -> dict[str, Any]:
    """Return current UTC timestamp."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "content": [{"type": "text", "text": f"Current UTC time: {now}"}]
    }


@tool(
    "web_fetch",
    "Fetch content from a URL. Returns the text content of the page.",
    {"url": str},
)
async def web_fetch(args: dict[str, Any]) -> dict[str, Any]:
    """Fetch a URL with SSRF protection."""
    url = args.get("url", "")
    if not url:
        return {
            "content": [{"type": "text", "text": "Error: 'url' parameter is required"}],
            "isError": True,
        }

    try:
        validated_url = validate_url(url)
    except ValueError as e:
        return {
            "content": [{"type": "text", "text": f"Error: {e}"}],
            "isError": True,
        }

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(validated_url)
            response.raise_for_status()
            # Limit response size to 100KB
            text = response.text[:100_000]
            return {
                "content": [{"type": "text", "text": text}]
            }
    except httpx.HTTPError as e:
        return {
            "content": [{"type": "text", "text": f"HTTP error: {e}"}],
            "isError": True,
        }


def register_builtin_tools(registry) -> None:
    """Register all built-in tools with the registry."""
    registry.register(current_time)
    registry.register(web_fetch)
