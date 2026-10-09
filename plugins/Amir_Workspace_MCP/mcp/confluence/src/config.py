from __future__ import annotations

import os

DEFAULT_BASE = "https://confluence-dc.paloaltonetworks.com"
TOKEN_NAMES = ("CONFLUENCE_API_TOKEN", "CONFLUENCE_PAT", "CONFLUENCE_PERSONAL_TOKEN")


class MissingConfigError(RuntimeError):
    pass


def get_base_url() -> str:
    return (os.environ.get("CONFLUENCE_BASE_URL") or DEFAULT_BASE).rstrip("/")


def get_token() -> str:
    for name in TOKEN_NAMES:
        value = (os.environ.get(name) or "").strip()
        if value:
            return value
    raise MissingConfigError(
        "Confluence token not found. Set CONFLUENCE_API_TOKEN in the palo workspace "
        "(venv --var palo --add CONFLUENCE_API_TOKEN ...) or export it before starting the agent."
    )
