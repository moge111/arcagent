"""Input validation and sanitization.

Patterns from NemoClaw (validateName, path traversal prevention)
and OpenClaw (isPathInside).
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

# RFC 1123 label: lowercase alphanumeric + hyphens, 1-63 chars
_RFC1123_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
MAX_SKILL_NAME_LENGTH = 63


def sanitize_input(text: str, max_length: int = 10_000) -> str:
    """Strip control characters and enforce max length.

    Removes null bytes and ASCII control chars (except newline/tab)
    to prevent injection attacks.
    """
    # Remove null bytes
    text = text.replace("\0", "")

    # Remove control characters except newline, tab, carriage return
    cleaned = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat.startswith("C") and ch not in ("\n", "\t", "\r"):
            continue
        cleaned.append(ch)

    result = "".join(cleaned)
    return result[:max_length]


def validate_path_within_root(path: Path, root: Path) -> Path:
    """Ensure a path resolves within the given root directory.

    Resolves symlinks and checks containment. Raises ValueError
    on path traversal attempts.

    Pattern from NemoClaw's isWithinRoot and OpenClaw's isPathInside.
    """
    resolved_path = path.resolve()
    resolved_root = root.resolve()

    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        raise ValueError(
            f"Path '{path}' resolves outside trusted root '{root}'"
        ) from None

    return resolved_path


def validate_skill_name(name: str) -> str:
    """Validate a skill name follows RFC 1123 label rules.

    Pattern from NemoClaw's sandbox name validation.
    """
    if not name or len(name) > MAX_SKILL_NAME_LENGTH:
        raise ValueError(
            f"Skill name must be 1-{MAX_SKILL_NAME_LENGTH} characters, got {len(name)}"
        )

    if not _RFC1123_PATTERN.match(name):
        raise ValueError(
            f"Skill name '{name}' must be lowercase alphanumeric with hyphens, "
            "starting and ending with alphanumeric"
        )

    return name
