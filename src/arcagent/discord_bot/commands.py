"""Discord slash commands: /ask, /chat, /skills, /status."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands

from ..core.message_types import AgentError
from .formatters import format_response, make_skills_embed, make_status_embed

if TYPE_CHECKING:
    from .bot import ArcAgentBot

logger = logging.getLogger(__name__)


def register_commands(bot: ArcAgentBot) -> None:
    """Register all slash commands with the bot."""

    @bot.tree.command(name="ask", description="Ask ArcAgent a question (one-shot)")
    @app_commands.describe(prompt="Your question or request")
    async def ask(interaction: discord.Interaction, prompt: str) -> None:
        await interaction.response.defer(thinking=True)

        try:
            response = await bot.engine.one_shot(prompt)
            chunks = format_response(response)
            await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.followup.send(chunk)
        except Exception as e:
            logger.error("Error in /ask: %s", e)
            await interaction.followup.send(f"Error: {e}")

    @bot.tree.command(name="chat", description="Start a persistent conversation thread")
    @app_commands.describe(topic="Topic for the conversation thread")
    async def chat(interaction: discord.Interaction, topic: str = "ArcAgent Chat") -> None:
        await interaction.response.defer()

        try:
            # Create a thread for the conversation
            thread = await interaction.channel.create_thread(
                name=f"ArcAgent: {topic[:80]}",
                type=discord.ChannelType.public_thread,
            )
            conversation_id = str(thread.id)

            # Send initial message in thread
            await thread.send(
                f"Started conversation: **{topic}**\n"
                "Send messages here to chat with ArcAgent. "
                "The conversation will auto-close after inactivity."
            )

            # Track this thread as an active conversation
            bot.active_threads.add(thread.id)

            await interaction.followup.send(
                f"Created conversation thread: {thread.mention}"
            )
        except Exception as e:
            logger.error("Error in /chat: %s", e)
            await interaction.followup.send(f"Error creating thread: {e}")

    @bot.tree.command(name="skills", description="List available skills")
    async def skills(interaction: discord.Interaction) -> None:
        skill_list = bot.skill_registry.list_skills()
        embed = make_skills_embed(skill_list)
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="status", description="Show ArcAgent status")
    async def status(interaction: discord.Interaction) -> None:
        embed = make_status_embed(
            active_sessions=bot.engine.conversations.active_count,
            skills_count=len(bot.skill_registry.get_all()),
            tools_count=len(bot.tool_registry.list_tools()) if bot.tool_registry else 0,
        )
        await interaction.response.send_message(embed=embed)
