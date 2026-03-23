"""Agent engine: wraps Claude CLI for AI interactions.

Uses claude --print with full tool access for both one-shot and
conversation modes. Supports shell execution, web fetching, and
persistent memory.
"""

from __future__ import annotations

import asyncio
import json
import logging
import shutil

from .conversation import ConversationManager
from .message_types import AgentResponse, ConversationMessage, MessageRole, ToolUse

logger = logging.getLogger(__name__)


class AgentEngine:
    """Core agent engine wrapping Claude CLI.

    Uses `claude` CLI with tool access for autonomous operation.
    """

    def __init__(
        self,
        system_prompt: str = "",
        mcp_servers: dict | None = None,
        allowed_tools: list[str] | None = None,
        cli_path: str | None = None,
        max_conversation_ttl: int = 3600,
    ) -> None:
        self._system_prompt = system_prompt
        self._mcp_servers = mcp_servers or {}
        self._allowed_tools = allowed_tools or []
        self._cli_path = cli_path or shutil.which("claude") or "claude"
        self._conversations = ConversationManager(ttl=max_conversation_ttl)
        self._lock = asyncio.Lock()

    @property
    def conversations(self) -> ConversationManager:
        return self._conversations

    def update_system_prompt(self, prompt: str) -> None:
        self._system_prompt = prompt

    async def one_shot(self, prompt: str) -> AgentResponse:
        """Send a one-shot query with full tool access."""
        cmd = [self._cli_path, "--print"]

        if self._system_prompt:
            cmd.extend(["--system-prompt", self._system_prompt])

        cmd.extend(["--permission-mode", "bypassPermissions"])
        cmd.extend(["--max-turns", "25"])
        cmd.append(prompt)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=300
            )

            if proc.returncode != 0:
                error_msg = stderr.decode().strip() if stderr else f"exit code {proc.returncode}"
                logger.error("Claude CLI failed: %s", error_msg)
                raise RuntimeError(f"Claude CLI error: {error_msg}")

            text = stdout.decode().strip()
            return AgentResponse(text=text)

        except asyncio.TimeoutError:
            if proc:
                proc.kill()
            logger.error("Claude CLI timed out after 300s")
            raise RuntimeError("Claude took too long to respond")

    async def send_message(
        self, conversation_id: str, message: str
    ) -> AgentResponse:
        """Send a message in a conversation with history context."""
        conv = self._conversations.get_or_create(conversation_id)
        conv.add_message(ConversationMessage(
            role=MessageRole.USER, content=message
        ))

        # Build context from conversation history
        history_parts: list[str] = []
        recent = conv.messages[-10:]
        if len(recent) > 1:
            history_parts.append("Previous conversation:")
            for msg in recent[:-1]:
                role = "User" if msg.role == MessageRole.USER else "Assistant"
                # Truncate long messages in history
                content = msg.content[:500] + "..." if len(msg.content) > 500 else msg.content
                history_parts.append(f"{role}: {content}")
            history_parts.append("")
            history_parts.append(f"Current message: {message}")
            full_prompt = "\n".join(history_parts)
        else:
            full_prompt = message

        response = await self.one_shot(full_prompt)
        response.conversation_id = conversation_id

        conv.add_message(ConversationMessage(
            role=MessageRole.ASSISTANT, content=response.text
        ))

        return response

    async def close_session(self, conversation_id: str) -> None:
        self._conversations.remove(conversation_id)

    async def close_all(self) -> None:
        for conv in self._conversations.list_active():
            self._conversations.remove(conv.conversation_id)
