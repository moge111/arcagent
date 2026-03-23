"""Dashboard API endpoints."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone

from fastapi import APIRouter

from ..config import AppConfig
from ..core.engine import AgentEngine
from ..skills.registry import SkillRegistry

_start_time = time.time()

# Simple in-memory log buffer
_log_buffer: deque[dict] = deque(maxlen=200)


def add_log(level: str, message: str, source: str = "system") -> None:
    """Add an entry to the log buffer."""
    _log_buffer.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
        "source": source,
    })


def create_router(
    engine: AgentEngine,
    skill_registry: SkillRegistry,
    tool_registry,
    config: AppConfig,
) -> APIRouter:
    router = APIRouter()

    @router.get("/status")
    async def get_status():
        uptime = int(time.time() - _start_time)
        return {
            "status": "running",
            "uptime_seconds": uptime,
            "active_sessions": engine.conversations.active_count,
            "skills_loaded": len(skill_registry.get_all()),
            "skills_enabled": len(skill_registry.get_enabled()),
            "tools_available": len(tool_registry.list_tools()) if tool_registry else 0,
        }

    @router.get("/logs")
    async def get_logs(limit: int = 50):
        logs = list(_log_buffer)[-limit:]
        return {"logs": logs}

    @router.get("/skills")
    async def get_skills():
        return {"skills": skill_registry.list_skills()}

    @router.post("/skills/{name}/toggle")
    async def toggle_skill(name: str):
        result = skill_registry.toggle(name)
        if result is None:
            return {"error": f"Skill '{name}' not found"}, 404
        add_log("info", f"Skill '{name}' {'enabled' if result else 'disabled'}", "dashboard")
        return {"name": name, "enabled": result}

    @router.get("/tools")
    async def get_tools():
        tools = tool_registry.list_tools() if tool_registry else []
        return {"tools": tools}

    @router.get("/conversations")
    async def get_conversations():
        convos = engine.conversations.list_active()
        return {
            "conversations": [
                {
                    "id": c.conversation_id,
                    "created_at": c.created_at,
                    "last_active": c.last_active,
                    "message_count": len(c.messages),
                }
                for c in convos
            ]
        }

    @router.get("/config")
    async def get_config():
        """Return sanitized config (no tokens/secrets)."""
        return {
            "discord": {
                "command_prefix": config.discord.command_prefix,
                "bot_connected": bool(config.discord.bot_token),
            },
            "dashboard": {
                "host": config.dashboard.host,
                "port": config.dashboard.port,
            },
            "skills": {
                "dirs": config.skills.dirs,
                "limits": {
                    "max_candidates_per_root": config.skills.limits.max_candidates_per_root,
                    "max_skills_in_prompt": config.skills.limits.max_skills_in_prompt,
                    "max_skills_prompt_chars": config.skills.limits.max_skills_prompt_chars,
                },
            },
            "claude": {
                "max_conversation_ttl": config.claude.max_conversation_ttl,
            },
        }

    return router
