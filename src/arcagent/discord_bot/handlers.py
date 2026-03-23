"""Message handlers — route thread messages to the agent engine."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord

from .formatters import format_response, make_tool_use_message

if TYPE_CHECKING:
    from .bot import ArcAgentBot

logger = logging.getLogger(__name__)


async def handle_thread_message(bot: ArcAgentBot, message: discord.Message) -> None:
    """Handle a message in an active conversation thread."""
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Only handle messages in tracked threads
    if message.channel.id not in bot.active_threads:
        return

    conversation_id = str(message.channel.id)
    content = message.content.strip()
    if not content:
        return

    # Show typing indicator
    async with message.channel.typing():
        try:
            response = await bot.engine.send_message(conversation_id, content)

            # Send tool use notifications
            for tool_use in response.tool_uses:
                await message.channel.send(make_tool_use_message(tool_use.tool_name))

            # Send response chunks
            chunks = format_response(response)
            for chunk in chunks:
                await message.channel.send(chunk)

        except Exception as e:
            logger.error("Error handling thread message: %s", e)
            await message.channel.send(f"Error: {e}")


async def handle_any_message(bot: ArcAgentBot, message: discord.Message) -> None:
    """Handle any message — respond to everything."""
    content = message.content.strip()

    # Strip bot mention if present
    if bot.user:
        content = content.replace(f"<@{bot.user.id}>", "").strip()

    if not content:
        return

    # Use channel ID as conversation ID for continuity per channel
    conversation_id = str(message.channel.id)

    async with message.channel.typing():
        try:
            response = await bot.engine.send_message(conversation_id, content)
            chunks = format_response(response)
            await message.reply(chunks[0])
            for chunk in chunks[1:]:
                await message.channel.send(chunk)
        except Exception as e:
            logger.error("Error handling message: %s", e)
            await message.reply(f"Error: {e}")
