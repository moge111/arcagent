"""Persistent memory — saves conversation history and notes to disk.

Conversations are saved as JSON files in the data directory.
Also supports a key-value memory store for long-term facts.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path("/home/jarvis/arcagent/data")
CONVERSATIONS_DIR = DATA_DIR / "conversations"
MEMORY_FILE = DATA_DIR / "memory.json"


def _ensure_dirs() -> None:
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)


def save_conversation(conversation_id: str, messages: list[dict]) -> None:
    """Save conversation messages to disk."""
    _ensure_dirs()
    filepath = CONVERSATIONS_DIR / f"{conversation_id}.json"
    data = {
        "conversation_id": conversation_id,
        "updated_at": time.time(),
        "messages": messages,
    }
    filepath.write_text(json.dumps(data, indent=2))


def load_conversation(conversation_id: str) -> list[dict] | None:
    """Load conversation messages from disk."""
    filepath = CONVERSATIONS_DIR / f"{conversation_id}.json"
    if not filepath.exists():
        return None
    try:
        data = json.loads(filepath.read_text())
        return data.get("messages", [])
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to load conversation %s: %s", conversation_id, e)
        return None


def list_conversations(limit: int = 20) -> list[dict]:
    """List recent conversations."""
    _ensure_dirs()
    convos = []
    for filepath in sorted(CONVERSATIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        try:
            data = json.loads(filepath.read_text())
            convos.append({
                "conversation_id": data.get("conversation_id", filepath.stem),
                "updated_at": data.get("updated_at", 0),
                "message_count": len(data.get("messages", [])),
            })
        except (json.JSONDecodeError, OSError):
            continue
    return convos


# --- Long-term memory (key-value store) ---

def _load_memory_store() -> dict[str, str]:
    if not MEMORY_FILE.exists():
        return {}
    try:
        return json.loads(MEMORY_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_memory_store(store: dict[str, str]) -> None:
    _ensure_dirs()
    MEMORY_FILE.write_text(json.dumps(store, indent=2))


def remember(key: str, value: str) -> None:
    """Store a fact in long-term memory."""
    store = _load_memory_store()
    store[key] = value
    _save_memory_store(store)
    logger.info("Remembered: %s", key)


def recall(key: str) -> str | None:
    """Recall a fact from long-term memory."""
    store = _load_memory_store()
    return store.get(key)


def recall_all() -> dict[str, str]:
    """Recall all facts from long-term memory."""
    return _load_memory_store()


def forget(key: str) -> bool:
    """Forget a fact from long-term memory."""
    store = _load_memory_store()
    if key in store:
        del store[key]
        _save_memory_store(store)
        return True
    return False
