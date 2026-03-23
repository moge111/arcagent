"""Compile loaded skills into system prompt text.

Pattern from OpenClaw's formatSkillsForPrompt and applySkillsPromptLimits:
- Full format: name, description, file path for each skill
- Compact fallback: name + path only when char budget exceeded
- XML structure for the agent to parse
"""

from __future__ import annotations

from pathlib import Path

from .types import SkillEntry


def _compact_path(path: Path) -> str:
    """Replace $HOME prefix with ~ to save tokens."""
    home = str(Path.home())
    path_str = str(path)
    if path_str.startswith(home):
        return "~" + path_str[len(home):]
    return path_str


def _format_skill_full(entry: SkillEntry) -> str:
    """Format a single skill in full detail."""
    path = _compact_path(entry.file_path)
    lines = [
        "  <skill>",
        f"    <name>{entry.metadata.name}</name>",
        f"    <description>{entry.metadata.description}</description>",
        f"    <location>{path}</location>",
    ]
    if entry.metadata.allowed_tools:
        tools_str = ", ".join(entry.metadata.allowed_tools)
        lines.append(f"    <tools>{tools_str}</tools>")
    lines.append("  </skill>")
    return "\n".join(lines)


def _format_skill_compact(entry: SkillEntry) -> str:
    """Format a single skill in compact mode (name + path only)."""
    path = _compact_path(entry.file_path)
    return f"  <skill><name>{entry.metadata.name}</name><location>{path}</location></skill>"


def compile_skills_prompt(
    entries: list[SkillEntry],
    char_budget: int = 30_000,
) -> str:
    """Compile skills into system prompt XML block.

    Tries full format first. Falls back to compact format if
    the result exceeds the character budget.
    """
    if not entries:
        return ""

    header = (
        "The following skills are available. "
        "Scan the list and read a skill's SKILL.md file if it clearly applies to the user's request.\n\n"
    )

    # Try full format
    full_skills = [_format_skill_full(e) for e in entries]
    full_block = header + "<available_skills>\n" + "\n".join(full_skills) + "\n</available_skills>"

    if len(full_block) <= char_budget:
        return full_block

    # Fall back to compact format
    compact_skills = [_format_skill_compact(e) for e in entries]
    compact_block = header + "<available_skills>\n" + "\n".join(compact_skills) + "\n</available_skills>"

    if len(compact_block) <= char_budget:
        return compact_block

    # Still too long — trim entries until within budget
    trimmed: list[str] = []
    current_len = len(header) + len("<available_skills>\n") + len("\n</available_skills>")

    for skill_line in compact_skills:
        if current_len + len(skill_line) + 1 > char_budget:
            break
        trimmed.append(skill_line)
        current_len += len(skill_line) + 1

    return header + "<available_skills>\n" + "\n".join(trimmed) + "\n</available_skills>"
