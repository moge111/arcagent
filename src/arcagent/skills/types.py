"""Skill data types."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SkillMetadata:
    """Parsed metadata from a SKILL.md frontmatter block."""
    name: str
    description: str
    allowed_tools: list[str] = field(default_factory=list)
    requires_bins: list[str] = field(default_factory=list)
    requires_config: list[str] = field(default_factory=list)
    env_vars: dict[str, str] = field(default_factory=dict)


@dataclass
class SkillEntry:
    """A loaded skill with its metadata and content."""
    metadata: SkillMetadata
    content: str  # SKILL.md body (post-frontmatter)
    file_path: Path  # absolute path to SKILL.md
    base_dir: Path  # parent directory of SKILL.md
    frontmatter_raw: dict = field(default_factory=dict)
    enabled: bool = True
