from __future__ import annotations

import os

DEFAULT_BASE = "https://jira-dc.paloaltonetworks.com"
TOKEN_NAMES = ("JIRA_TOKEN", "JIRA_API_TOKEN", "JIRA_PAT")


class MissingConfigError(RuntimeError):
    pass


def get_base_url() -> str:
    return (os.environ.get("JIRA_BASE_URL") or DEFAULT_BASE).rstrip("/")


def get_token() -> str:
    for name in TOKEN_NAMES:
        value = (os.environ.get(name) or "").strip()
        if value:
            return value
    raise MissingConfigError(
        "Jira token not found. Set JIRA_TOKEN in the palo workspace or export it before starting the agent."
    )
