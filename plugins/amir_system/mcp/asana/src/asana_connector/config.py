"""Configuration / credential loading for the Asana connector.

Token resolution order (first non-placeholder wins):
    1. ASANA_ACCESS_TOKEN environment variable
    2. a .env file at the project root (ASANA_ACCESS_TOKEN=...)
    3. the project CLAUDE.md file, line:  ASANA_ACCESS_TOKEN: <token>
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"
ENV_FILE = PROJECT_ROOT / ".env"

ENV_VAR = "ASANA_ACCESS_TOKEN"
ASANA_BASE_URL = "https://app.asana.com/api/1.0"

_PLACEHOLDERS = {"", "PASTE_YOUR_TOKEN_HERE", "your-token-here", "changeme"}

load_dotenv(ENV_FILE, override=False)


class MissingTokenError(RuntimeError):
    """Raised when no usable Asana token can be found."""


def _read_token_from_env_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(f"{ENV_VAR}="):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            return value or None
    return None


def _read_token_from_claude_md(path: Path) -> str | None:
    if not path.is_file():
        return None
    pattern = re.compile(rf"^\s*{ENV_VAR}\s*[:=]\s*(\S+)\s*$", re.MULTILINE)
    match = pattern.search(path.read_text(encoding="utf-8"))
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return None


def get_token() -> str:
    """Return the Asana PAT, or raise MissingTokenError with guidance."""
    candidates = [
        os.environ.get(ENV_VAR),
        _read_token_from_env_file(ENV_FILE),
        _read_token_from_claude_md(CLAUDE_MD),
    ]
    for token in candidates:
        if token and token not in _PLACEHOLDERS:
            return token

    raise MissingTokenError(
        "No Asana access token found.\n"
        f"Paste your Personal Access Token into:\n  {CLAUDE_MD}\n"
        f"on the line:\n  {ENV_VAR}: <your token>\n"
        f"(or set the {ENV_VAR} environment variable / a .env file)."
    )


def get_base_url() -> str:
    """Allow overriding the API base URL (useful for tests/mocks)."""
    return os.environ.get("ASANA_BASE_URL", ASANA_BASE_URL)
