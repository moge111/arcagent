"""Format agent responses for Discord (markdown, embeds, files, truncation)."""

from __future__ import annotations

import io
import os
import re

import discord

from ..core.message_types import AgentResponse

DISCORD_MAX_MESSAGE = 2000
DISCORD_MAX_EMBED = 4096


def truncate(text: str, limit: int = DISCORD_MAX_MESSAGE, suffix: str = "\n...(truncated)") -> str:
    if len(text) <= limit:
        return text
    return text[: limit - len(suffix)] + suffix


def split_message(text: str, limit: int = DISCORD_MAX_MESSAGE) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break

        split_idx = text.rfind("\n", 0, limit)
        if split_idx == -1 or split_idx < limit // 2:
            split_idx = limit

        chunks.append(text[:split_idx])
        text = text[split_idx:].lstrip("\n")

    return chunks


def format_response(response: AgentResponse) -> list[str]:
    if not response.text:
        return ["*(No response)*"]
    return split_message(response.text)


def extract_file_paths(text: str) -> list[str]:
    """Extract file paths mentioned in the response that exist on disk."""
    # Look for common file path patterns
    patterns = [
        r'/(?:home|tmp|var|root)/[\w/.+\-]+\.(?:png|jpg|jpeg|gif|svg|pdf|csv|txt|json|py|sh|log)',
    ]
    paths = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if os.path.isfile(match):
                paths.append(match)
    return paths


def make_file_attachment(filepath: str) -> discord.File | None:
    """Create a Discord file attachment from a server file path."""
    if not os.path.isfile(filepath):
        return None
    try:
        filesize = os.path.getsize(filepath)
        if filesize > 8_000_000:  # Discord 8MB limit
            return None
        return discord.File(filepath, filename=os.path.basename(filepath))
    except (OSError, PermissionError):
        return None


def make_status_embed(
    active_sessions: int,
    skills_count: int,
    tools_count: int,
) -> discord.Embed:
    embed = discord.Embed(
        title="Terry Status",
        color=discord.Color.green(),
    )
    embed.add_field(name="Active Sessions", value=str(active_sessions), inline=True)
    embed.add_field(name="Skills Loaded", value=str(skills_count), inline=True)
    embed.add_field(name="Tools Available", value=str(tools_count), inline=True)
    return embed


def make_skills_embed(skills: list[dict]) -> discord.Embed:
    embed = discord.Embed(
        title="Available Skills",
        color=discord.Color.blue(),
    )

    for skill in skills[:25]:
        status = "Enabled" if skill["enabled"] else "Disabled"
        embed.add_field(
            name=f"{skill['name']} [{status}]",
            value=skill.get("description", "No description") or "No description",
            inline=False,
        )

    if not skills:
        embed.description = "No skills loaded."

    return embed


def make_tool_use_message(tool_name: str) -> str:
    return f"*Using tool: `{tool_name}`...*"
