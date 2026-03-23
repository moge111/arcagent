"""Agent engine: wraps Claude CLI for AI interactions.

Provides two modes:
1. SDK mode: Uses claude-agent-sdk for rich multi-turn conversations with tool support
2. CLI mode: Falls back to `claude --print` subprocess for simple, reliable queries

Auth is delegated to the `claude` CLI — no token management here.
"""

from __future__ import annotations

import asyncio
import logging
import shutil

from .conversation import ConversationManager
from .message_types import AgentResponse, ConversationMessage, MessageRole, ToolUse

logger = logging.getLogger(__name__)


class AgentEngine:
    """Core agent engine wrapping Claude CLI.

    Uses `claude --print` for reliable one-shot queries, and attempts
    the SDK streaming mode for multi-turn conversations.
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
        """Update the system prompt (e.g., after skills reload)."""
        self._system_prompt = prompt

    async def one_shot(self, prompt: str) -> AgentResponse:
        """Send a one-shot query using `claude --print` subprocess.

        This is the most reliable method — proven to work on headless VPS.
        """
        cmd = [self._cli_path, "--print"]

        if self._system_prompt:
            cmd.extend(["--system-prompt", self._system_prompt])

        cmd.extend(["--permission-mode", "acceptEdits"])
        cmd.extend(["--max-turns", "3"])
        cmd.append(prompt)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=120
            )

            if proc.returncode != 0:
                error_msg = stderr.decode().strip() if stderr else f"exit code {proc.returncode}"
                logger.error("Claude CLI failed: %s", error_msg)
                raise RuntimeError(f"Claude CLI error: {error_msg}")

            text = stdout.decode().strip()
            return AgentResponse(text=text)

        except asyncio.TimeoutError:
            logger.error("Claude CLI timed out after 120s")
            raise RuntimeError("Claude took too long to respond")

    async def send_message(
        self, conversation_id: str, message: str
    ) -> AgentResponse:
        """Send a message in a conversation.

        For now, uses one-shot mode with conversation history prepended.
        Each message includes prior context for continuity.
        """
        conv = self._conversations.get_or_create(conversation_id)
        conv.add_message(ConversationMessage(
            role=MessageRole.USER, content=message
        ))

        # Build context from conversation history
        history_parts: list[str] = []
        # Include last 10 messages for context
        recent = conv.messages[-10:]
        if len(recent) > 1:  # More than just the current message
            history_parts.append("Previous conversation:")
            for msg in recent[:-1]:  # Exclude current message
                role = "User" if msg.role == MessageRole.USER else "Assistant"
                history_parts.append(f"{role}: {msg.content}")
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
        """Close a conversation session and cleanup."""
        self._conversations.remove(conversation_id)

    async def close_all(self) -> None:
        """Close all active sessions."""
        # Clear all conversation state
        for conv in self._conversations.list_active():
            self._conversations.remove(conv.conversation_id)
