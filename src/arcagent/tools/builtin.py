"""Built-in tools for ArcAgent."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Any

import httpx
from claude_agent_sdk import tool

from ..security.network import validate_url


@tool("current_time", "Get the current UTC date and time", {})
async def current_time(args: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {"content": [{"type": "text", "text": f"Current UTC time: {now}"}]}


@tool(
    "web_fetch",
    "Fetch content from a URL and return the text. Use for web searches, reading articles, APIs, etc.",
    {"url": str},
)
async def web_fetch(args: dict[str, Any]) -> dict[str, Any]:
    url = args.get("url", "")
    if not url:
        return {"content": [{"type": "text", "text": "Error: 'url' parameter is required"}], "isError": True}

    try:
        validated_url = validate_url(url)
    except ValueError as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(validated_url, headers={"User-Agent": "ArcAgent/1.0"})
            response.raise_for_status()
            text = response.text[:100_000]
            return {"content": [{"type": "text", "text": text}]}
    except httpx.HTTPError as e:
        return {"content": [{"type": "text", "text": f"HTTP error: {e}"}], "isError": True}


@tool(
    "shell_exec",
    "Execute a shell command on the server and return the output. Use for system tasks, file management, running scripts, checking server status, etc.",
    {"command": str},
)
async def shell_exec(args: dict[str, Any]) -> dict[str, Any]:
    command = args.get("command", "")
    if not command:
        return {"content": [{"type": "text", "text": "Error: 'command' parameter is required"}], "isError": True}

    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.path.expanduser("~"),
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)

        output_parts = []
        if stdout:
            output_parts.append(f"stdout:\n{stdout.decode(errors='replace')[:50_000]}")
        if stderr:
            output_parts.append(f"stderr:\n{stderr.decode(errors='replace')[:10_000]}")
        if not output_parts:
            output_parts.append("(no output)")

        output_parts.append(f"\nexit code: {proc.returncode}")
        result = "\n".join(output_parts)

        return {"content": [{"type": "text", "text": result}]}
    except asyncio.TimeoutError:
        return {"content": [{"type": "text", "text": "Error: command timed out after 60 seconds"}], "isError": True}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}


@tool(
    "read_file",
    "Read the contents of a file from the server filesystem.",
    {"path": str},
)
async def read_file(args: dict[str, Any]) -> dict[str, Any]:
    path = args.get("path", "")
    if not path:
        return {"content": [{"type": "text", "text": "Error: 'path' parameter is required"}], "isError": True}

    path = os.path.expanduser(path)
    try:
        with open(path, "r", errors="replace") as f:
            content = f.read(200_000)  # 200KB limit
        return {"content": [{"type": "text", "text": content}]}
    except FileNotFoundError:
        return {"content": [{"type": "text", "text": f"File not found: {path}"}], "isError": True}
    except PermissionError:
        return {"content": [{"type": "text", "text": f"Permission denied: {path}"}], "isError": True}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error reading file: {e}"}], "isError": True}


@tool(
    "write_file",
    "Write content to a file on the server filesystem. Creates the file if it doesn't exist.",
    {"path": str, "content": str},
)
async def write_file(args: dict[str, Any]) -> dict[str, Any]:
    path = args.get("path", "")
    content = args.get("content", "")
    if not path:
        return {"content": [{"type": "text", "text": "Error: 'path' parameter is required"}], "isError": True}

    path = os.path.expanduser(path)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return {"content": [{"type": "text", "text": f"Written {len(content)} bytes to {path}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error writing file: {e}"}], "isError": True}


@tool(
    "memory_remember",
    "Store a fact or note in long-term memory that persists across conversations.",
    {"key": str, "value": str},
)
async def memory_remember(args: dict[str, Any]) -> dict[str, Any]:
    from ..core.memory import remember
    key = args.get("key", "")
    value = args.get("value", "")
    if not key or not value:
        return {"content": [{"type": "text", "text": "Error: both 'key' and 'value' are required"}], "isError": True}
    remember(key, value)
    return {"content": [{"type": "text", "text": f"Remembered: {key} = {value}"}]}


@tool(
    "memory_recall",
    "Recall a fact from long-term memory by key, or recall all stored facts if no key given.",
    {"key": str},
)
async def memory_recall(args: dict[str, Any]) -> dict[str, Any]:
    from ..core.memory import recall, recall_all
    key = args.get("key", "")
    if key:
        value = recall(key)
        if value is None:
            return {"content": [{"type": "text", "text": f"No memory found for key: {key}"}]}
        return {"content": [{"type": "text", "text": f"{key} = {value}"}]}
    else:
        all_memories = recall_all()
        if not all_memories:
            return {"content": [{"type": "text", "text": "No memories stored."}]}
        lines = [f"- {k}: {v}" for k, v in all_memories.items()]
        return {"content": [{"type": "text", "text": "Stored memories:\n" + "\n".join(lines)}]}


def register_builtin_tools(registry) -> None:
    """Register all built-in tools with the registry."""
    registry.register(current_time)
    registry.register(web_fetch)
    registry.register(shell_exec)
    registry.register(read_file)
    registry.register(write_file)
    registry.register(memory_remember)
    registry.register(memory_recall)
