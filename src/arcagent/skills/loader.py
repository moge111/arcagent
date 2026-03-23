"""SKILL.md discovery, frontmatter parsing, and loading.

Pattern from OpenClaw's loadSkillEntries in workspace.ts:
- Walk configured directories for SKILL.md files
- Parse YAML frontmatter
- Enforce size and count limits
- Prevent path traversal
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from ..config import SkillLimits
from ..security.validation import validate_path_within_root, validate_skill_name
from .types import SkillEntry, SkillMetadata

logger = logging.getLogger(__name__)


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a SKILL.md file.

    Returns (frontmatter_dict, body_text).
    Frontmatter is delimited by --- at the top of the file.
    """
    if not content.startswith("---"):
        return {}, content

    # Find closing ---
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return {}, content

    frontmatter_str = content[3:end_idx].strip()
    body = content[end_idx + 3:].strip()

    try:
        frontmatter = yaml.safe_load(frontmatter_str) or {}
    except yaml.YAMLError as e:
        logger.warning("Failed to parse SKILL.md frontmatter: %s", e)
        return {}, content

    if not isinstance(frontmatter, dict):
        return {}, content

    return frontmatter, body


def _extract_metadata(frontmatter: dict) -> SkillMetadata:
    """Extract SkillMetadata from parsed frontmatter."""
    name = str(frontmatter.get("name", ""))
    description = str(frontmatter.get("description", ""))

    allowed_tools = frontmatter.get("allowed-tools", [])
    if isinstance(allowed_tools, str):
        allowed_tools = [allowed_tools]

    # OpenClaw-compatible nested metadata
    meta = frontmatter.get("metadata", {})
    openclaw_meta = meta.get("openclaw", {}) if isinstance(meta, dict) else {}
    requires = openclaw_meta.get("requires", {}) if isinstance(openclaw_meta, dict) else {}

    requires_bins = requires.get("bins", []) if isinstance(requires, dict) else []
    requires_config = requires.get("config", []) if isinstance(requires, dict) else []

    return SkillMetadata(
        name=name,
        description=description,
        allowed_tools=allowed_tools,
        requires_bins=requires_bins if isinstance(requires_bins, list) else [],
        requires_config=requires_config if isinstance(requires_config, list) else [],
    )


def _load_skill_from_dir(skill_dir: Path, root: Path, limits: SkillLimits) -> SkillEntry | None:
    """Load a single skill from a directory containing SKILL.md."""
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return None

    # Path traversal prevention
    try:
        validate_path_within_root(skill_file, root)
    except ValueError as e:
        logger.warning("Skipping skill at %s: %s", skill_dir, e)
        return None

    # Size limit
    try:
        size = skill_file.stat().st_size
    except OSError:
        return None

    if size > limits.max_skill_file_bytes:
        logger.warning(
            "Skipping skill at %s: file size %d exceeds limit %d",
            skill_dir, size, limits.max_skill_file_bytes,
        )
        return None

    try:
        content = skill_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("Failed to read %s: %s", skill_file, e)
        return None

    frontmatter, body = parse_frontmatter(content)
    metadata = _extract_metadata(frontmatter)

    if not metadata.name:
        # Fall back to directory name
        metadata.name = skill_dir.name

    # Validate skill name
    try:
        validate_skill_name(metadata.name)
    except ValueError as e:
        logger.warning("Skipping skill at %s: %s", skill_dir, e)
        return None

    return SkillEntry(
        metadata=metadata,
        content=body,
        file_path=skill_file.resolve(),
        base_dir=skill_dir.resolve(),
        frontmatter_raw=frontmatter,
    )


def load_skills(
    skills_dirs: list[Path],
    limits: SkillLimits | None = None,
) -> list[SkillEntry]:
    """Discover and load all skills from configured directories.

    Scans each directory for subdirectories containing SKILL.md files.
    Enforces count and size limits per OpenClaw's pattern.
    """
    if limits is None:
        limits = SkillLimits()

    entries: list[SkillEntry] = []

    for skills_root in skills_dirs:
        skills_root = Path(skills_root).resolve()
        if not skills_root.is_dir():
            logger.debug("Skills directory does not exist: %s", skills_root)
            continue

        candidates = 0
        for item in sorted(skills_root.iterdir()):
            if candidates >= limits.max_candidates_per_root:
                logger.info(
                    "Hit max candidates (%d) for %s",
                    limits.max_candidates_per_root, skills_root,
                )
                break

            if not item.is_dir():
                continue

            candidates += 1
            entry = _load_skill_from_dir(item, skills_root, limits)
            if entry:
                entries.append(entry)

    # Apply global limit
    if len(entries) > limits.max_skills_in_prompt:
        logger.info(
            "Trimming skills from %d to %d (max_skills_in_prompt)",
            len(entries), limits.max_skills_in_prompt,
        )
        entries = entries[:limits.max_skills_in_prompt]

    return entries
