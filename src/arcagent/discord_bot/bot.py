"""Discord bot lifecycle and event routing."""

from __future__ import annotations

import logging

import discord
from discord.ext import commands

from ..config import AppConfig
from ..core.engine import AgentEngine
from ..skills.registry import SkillRegistry
from .commands import register_commands
from .handlers import handle_any_message

logger = logging.getLogger(__name__)


class ArcAgentBot(commands.Bot):
    """ArcAgent Discord bot.

    Provides slash commands (/ask, /chat, /skills, /status)
    and handles messages in conversation threads.
    """

    def __init__(
        self,
        engine: AgentEngine,
        skill_registry: SkillRegistry,
        config: AppConfig,
        tool_registry=None,
    ) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True

        super().__init__(
            command_prefix=config.discord.command_prefix,
            intents=intents,
        )

        self.engine = engine
        self.skill_registry = skill_registry
        self.tool_registry = tool_registry
        self.config = config
        self.active_threads: set[int] = set()

    async def setup_hook(self) -> None:
        """Register slash commands on startup."""
        register_commands(self)
        await self.tree.sync()
        logger.info("Slash commands synced")

    async def on_ready(self) -> None:
        logger.info("ArcAgent bot connected as %s (ID: %s)", self.user, self.user.id)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/ask",
            )
        )

    async def on_message(self, message: discord.Message) -> None:
        # Ignore own messages
        if message.author == self.user:
            return

        # Ignore empty messages
        content = message.content.strip()
        if not content:
            return

        # Respond to all messages
        from .handlers import handle_any_message
        await handle_any_message(self, message)

        # Process prefix commands (if any)
        await self.process_commands(message)
