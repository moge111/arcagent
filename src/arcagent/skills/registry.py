"""Runtime skill registry with enable/disable and per-skill config."""

from __future__ import annotations

import logging

from ..config import SkillConfigEntry
from .types import SkillEntry

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Manages loaded skills with enable/disable support.

    Per-skill configuration (enabled, env vars, API keys) is applied
    from the config file's skills.entries section.
    """

    def __init__(
        self,
        entries: list[SkillEntry],
        config_entries: dict[str, SkillConfigEntry] | None = None,
    ) -> None:
        self._skills: dict[str, SkillEntry] = {}
        config_entries = config_entries or {}

        for entry in entries:
            name = entry.metadata.name

            # Apply config overrides
            if name in config_entries:
                cfg = config_entries[name]
                entry.enabled = cfg.enabled
                if cfg.env:
                    entry.metadata.env_vars.update(cfg.env)
            else:
                entry.enabled = True

            self._skills[name] = entry

    def get(self, name: str) -> SkillEntry | None:
        return self._skills.get(name)

    def get_all(self) -> list[SkillEntry]:
        return list(self._skills.values())

    def get_enabled(self) -> list[SkillEntry]:
        return [s for s in self._skills.values() if s.enabled]

    def enable(self, name: str) -> bool:
        skill = self._skills.get(name)
        if skill:
            skill.enabled = True
            logger.info("Enabled skill: %s", name)
            return True
        return False

    def disable(self, name: str) -> bool:
        skill = self._skills.get(name)
        if skill:
            skill.enabled = False
            logger.info("Disabled skill: %s", name)
            return True
        return False

    def toggle(self, name: str) -> bool | None:
        """Toggle skill enabled state. Returns new state or None if not found."""
        skill = self._skills.get(name)
        if skill is None:
            return None
        skill.enabled = not skill.enabled
        logger.info("%s skill: %s", "Enabled" if skill.enabled else "Disabled", name)
        return skill.enabled

    def list_skills(self) -> list[dict]:
        """Return skill summaries for API/dashboard use."""
        return [
            {
                "name": s.metadata.name,
                "description": s.metadata.description,
                "enabled": s.enabled,
                "allowed_tools": s.metadata.allowed_tools,
                "path": str(s.file_path),
            }
            for s in self._skills.values()
        ]
