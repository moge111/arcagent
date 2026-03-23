"""Configuration loading with YAML + env var resolution."""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class DiscordConfig:
    bot_token: str = ""
    command_prefix: str = "/"


@dataclass
class DashboardConfig:
    host: str = "127.0.0.1"
    port: int = 8080
    auth_token: str = ""


@dataclass
class SkillLimits:
    max_candidates_per_root: int = 300
    max_skills_in_prompt: int = 150
    max_skills_prompt_chars: int = 30_000
    max_skill_file_bytes: int = 256 * 1024


@dataclass
class SkillConfigEntry:
    enabled: bool = True
    env: dict[str, str] = field(default_factory=dict)
    api_key: str = ""


@dataclass
class SkillsConfig:
    dirs: list[str] = field(default_factory=lambda: ["./skills"])
    limits: SkillLimits = field(default_factory=SkillLimits)
    entries: dict[str, SkillConfigEntry] = field(default_factory=dict)


@dataclass
class ClaudeConfig:
    cli_path: str | None = None
    system_prompt_append: str = ""
    max_conversation_ttl: int = 3600


@dataclass
class AppConfig:
    discord: DiscordConfig = field(default_factory=DiscordConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    skills: SkillsConfig = field(default_factory=SkillsConfig)
    claude: ClaudeConfig = field(default_factory=ClaudeConfig)


def _merge_dict(target: dict, source: dict) -> dict:
    """Deep merge source into target."""
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _merge_dict(target[key], value)
        else:
            target[key] = value
    return target


def _build_discord_config(raw: dict[str, Any]) -> DiscordConfig:
    cfg = DiscordConfig(
        bot_token=raw.get("bot_token", ""),
        command_prefix=raw.get("command_prefix", "/"),
    )
    # Env var override
    cfg.bot_token = os.environ.get("ARCAGENT_DISCORD_TOKEN", cfg.bot_token)
    return cfg


def _build_dashboard_config(raw: dict[str, Any]) -> DashboardConfig:
    cfg = DashboardConfig(
        host=raw.get("host", "127.0.0.1"),
        port=int(raw.get("port", 8080)),
        auth_token=raw.get("auth_token", ""),
    )
    cfg.auth_token = os.environ.get("ARCAGENT_DASHBOARD_TOKEN", cfg.auth_token)
    if not cfg.auth_token:
        cfg.auth_token = secrets.token_urlsafe(32)
    return cfg


def _build_skills_config(raw: dict[str, Any]) -> SkillsConfig:
    limits_raw = raw.get("limits", {})
    limits = SkillLimits(
        max_candidates_per_root=limits_raw.get("max_candidates_per_root", 300),
        max_skills_in_prompt=limits_raw.get("max_skills_in_prompt", 150),
        max_skills_prompt_chars=limits_raw.get("max_skills_prompt_chars", 30_000),
        max_skill_file_bytes=limits_raw.get("max_skill_file_bytes", 256 * 1024),
    )

    entries: dict[str, SkillConfigEntry] = {}
    for name, entry_raw in raw.get("entries", {}).items():
        if isinstance(entry_raw, dict):
            entries[name] = SkillConfigEntry(
                enabled=entry_raw.get("enabled", True),
                env=entry_raw.get("env", {}),
                api_key=entry_raw.get("api_key", ""),
            )

    return SkillsConfig(
        dirs=raw.get("dirs", ["./skills"]),
        limits=limits,
        entries=entries,
    )


def _build_claude_config(raw: dict[str, Any]) -> ClaudeConfig:
    cfg = ClaudeConfig(
        cli_path=raw.get("cli_path"),
        system_prompt_append=raw.get("system_prompt_append", ""),
        max_conversation_ttl=int(raw.get("max_conversation_ttl", 3600)),
    )
    cli_env = os.environ.get("ARCAGENT_CLAUDE_CLI_PATH")
    if cli_env:
        cfg.cli_path = cli_env
    return cfg


def load_config(config_path: str | Path = "config.yaml") -> AppConfig:
    """Load configuration from YAML file with env var overrides."""
    config_path = Path(config_path)
    raw: dict[str, Any] = {}

    if config_path.exists():
        with open(config_path) as f:
            raw = yaml.safe_load(f) or {}

    return AppConfig(
        discord=_build_discord_config(raw.get("discord", {})),
        dashboard=_build_dashboard_config(raw.get("dashboard", {})),
        skills=_build_skills_config(raw.get("skills", {})),
        claude=_build_claude_config(raw.get("claude", {})),
    )
