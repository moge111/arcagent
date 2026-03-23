"""Credential storage with secure file permissions.

Pattern from NemoClaw: credentials stored in ~/.arcagent/credentials.json
with directory mode 0o700 and file mode 0o600. Environment variables
take precedence over stored credentials.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

CREDS_DIR = Path.home() / ".arcagent"
CREDS_FILE = CREDS_DIR / "credentials.json"


def _ensure_creds_dir() -> None:
    """Create credentials directory with restrictive permissions."""
    if not CREDS_DIR.exists():
        CREDS_DIR.mkdir(mode=0o700, parents=True)
    else:
        # Ensure permissions are correct
        CREDS_DIR.chmod(0o700)


def _load_creds_file() -> dict[str, str]:
    """Load credentials from file."""
    if not CREDS_FILE.exists():
        return {}
    with open(CREDS_FILE) as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def _save_creds_file(creds: dict[str, str]) -> None:
    """Save credentials to file with restrictive permissions."""
    _ensure_creds_dir()
    with open(CREDS_FILE, "w") as f:
        json.dump(creds, f, indent=2)
    CREDS_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600


def save_credential(key: str, value: str) -> None:
    """Store a credential. File is created with mode 0o600."""
    creds = _load_creds_file()
    creds[key] = value
    _save_creds_file(creds)


def get_credential(key: str, env_var: str | None = None) -> str | None:
    """Get a credential. Environment variable takes precedence over stored value."""
    if env_var:
        env_value = os.environ.get(env_var)
        if env_value:
            return env_value

    creds = _load_creds_file()
    return creds.get(key)


def load_credentials() -> dict[str, str]:
    """Load all stored credentials."""
    return _load_creds_file()


def delete_credential(key: str) -> bool:
    """Remove a credential. Returns True if it existed."""
    creds = _load_creds_file()
    if key in creds:
        del creds[key]
        _save_creds_file(creds)
        return True
    return False
