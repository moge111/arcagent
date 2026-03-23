"""Format agent responses for Discord (markdown, embeds, truncation)."""

from __future__ import annotations

import discord

from ..core.message_types import AgentResponse

DISCORD_MAX_MESSAGE = 2000
DISCORD_MAX_EMBED = 4096


def truncate(text: str, limit: int = DISCORD_MAX_MESSAGE, suffix: str = "\n...(truncated)") -> str:
    """Truncate text to fit Discord's character limit."""
    if len(text) <= limit:
        return text
    return text[: limit - len(suffix)] + suffix


def split_message(text: str, limit: int = DISCORD_MAX_MESSAGE) -> list[str]:
    """Split a long message into chunks that fit Discord's limit."""
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break

        # Try to split at a newline
        split_idx = text.rfind("\n", 0, limit)
        if split_idx == -1 or split_idx < limit // 2:
            split_idx = limit

        chunks.append(text[:split_idx])
        text = text[split_idx:].lstrip("\n")

    return chunks


def format_response(response: AgentResponse) -> list[str]:
    """Format an AgentResponse into Discord-ready message chunks."""
    if not response.text:
        return ["*(No response)*"]
    return split_message(response.text)


def make_status_embed(
    active_sessions: int,
    skills_count: int,
    tools_count: int,
) -> discord.Embed:
    """Create a status embed for the /status command."""
    embed = discord.Embed(
        title="ArcAgent Status",
        color=discord.Color.green(),
    )
    embed.add_field(name="Active Sessions", value=str(active_sessions), inline=True)
    embed.add_field(name="Skills Loaded", value=str(skills_count), inline=True)
    embed.add_field(name="Tools Available", value=str(tools_count), inline=True)
    return embed


def make_skills_embed(skills: list[dict]) -> discord.Embed:
    """Create an embed listing skills."""
    embed = discord.Embed(
        title="Available Skills",
        color=discord.Color.blue(),
    )

    for skill in skills[:25]:  # Discord embed field limit
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
    """Format a tool use notification."""
    return f"*Using tool: `{tool_name}`...*"
