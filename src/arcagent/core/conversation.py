"""Per-conversation state management with TTL-based cleanup."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field

from .message_types import ConversationMessage


@dataclass
class ConversationState:
    """Tracks state for a single conversation session."""
    conversation_id: str
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    messages: list[ConversationMessage] = field(default_factory=list)
    active_skills: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def touch(self) -> None:
        """Update last active timestamp."""
        self.last_active = time.time()

    def is_expired(self, ttl: int) -> bool:
        """Check if conversation has exceeded TTL (seconds)."""
        return (time.time() - self.last_active) > ttl

    def add_message(self, message: ConversationMessage) -> None:
        self.messages.append(message)
        self.touch()


class ConversationManager:
    """Manages multiple conversation sessions with auto-cleanup."""

    def __init__(self, ttl: int = 3600) -> None:
        self._conversations: dict[str, ConversationState] = {}
        self._ttl = ttl
        self._cleanup_task: asyncio.Task | None = None

    def get(self, conversation_id: str) -> ConversationState | None:
        conv = self._conversations.get(conversation_id)
        if conv and conv.is_expired(self._ttl):
            self.remove(conversation_id)
            return None
        return conv

    def create(self, conversation_id: str) -> ConversationState:
        state = ConversationState(conversation_id=conversation_id)
        self._conversations[conversation_id] = state
        return state

    def get_or_create(self, conversation_id: str) -> ConversationState:
        existing = self.get(conversation_id)
        if existing:
            return existing
        return self.create(conversation_id)

    def remove(self, conversation_id: str) -> None:
        self._conversations.pop(conversation_id, None)

    def list_active(self) -> list[ConversationState]:
        self._cleanup_expired()
        return list(self._conversations.values())

    def _cleanup_expired(self) -> None:
        expired = [
            cid for cid, state in self._conversations.items()
            if state.is_expired(self._ttl)
        ]
        for cid in expired:
            self._conversations.pop(cid, None)

    async def start_cleanup_loop(self, interval: int = 300) -> None:
        """Run periodic cleanup of expired conversations."""
        while True:
            self._cleanup_expired()
            await asyncio.sleep(interval)

    @property
    def active_count(self) -> int:
        self._cleanup_expired()
        return len(self._conversations)
