"""Typed message dataclasses for internal agent communication."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ToolUse:
    """A tool invocation by the agent."""
    tool_name: str
    tool_input: dict
    tool_use_id: str
    result: str | None = None


@dataclass
class AgentResponse:
    """Parsed response from the agent engine."""
    text: str
    tool_uses: list[ToolUse] = field(default_factory=list)
    conversation_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentError:
    """Error from the agent engine."""
    message: str
    code: str = "unknown"
    conversation_id: str = ""


@dataclass
class ConversationMessage:
    """A single message in conversation history."""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
