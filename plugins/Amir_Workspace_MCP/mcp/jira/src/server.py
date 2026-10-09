from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.fastmcp import FastMCP

from client import JiraClient, JiraError
from config import MissingConfigError

mcp = FastMCP("Palo Jira (personal token)")
_client: JiraClient | None = None


def client() -> JiraClient:
    global _client
    if _client is None:
        _client = JiraClient()
    return _client


def _issue_line(fields: dict, key: str) -> str:
    summary = (fields.get("summary") or "(no summary)").strip()
    status = ((fields.get("status") or {}).get("name") or "?") if isinstance(fields.get("status"), dict) else "?"
    return f"- **{key}** {summary} · status: {status}"


@mcp.tool()
def jira_search(jql: str, max_results: int = 20) -> str:
    """Run a JQL query and return matching issues."""
    try:
        data = client().search(jql, max_results=max_results)
        issues = list(data.get("issues") or [])
        if not issues:
            return "No issues matched."
        lines = [f"Total: {data.get('total', len(issues))}"]
        for item in issues:
            key = item.get("key") or "?"
            fields = item.get("fields") or {}
            lines.append(_issue_line(fields, key))
        return "\n".join(lines)
    except MissingConfigError as e:
        return f"⚠️ {e}"
    except JiraError as e:
        return f"⚠️ {e}"


@mcp.tool()
def jira_get_issue(issue_key: str) -> str:
    """Fetch one issue by key (e.g. PROJ-123)."""
    try:
        data = client().get_issue(issue_key.strip().upper())
        fields = data.get("fields") or {}
        summary = fields.get("summary") or "(no summary)"
        status = ((fields.get("status") or {}).get("name") or "?") if isinstance(fields.get("status"), dict) else "?"
        desc = fields.get("description") or ""
        if isinstance(desc, dict):
            desc = str(desc)
        body = (desc or "")[:8000]
        return f"# {issue_key}\n**{summary}**\nstatus: {status}\n\n{body}"
    except MissingConfigError as e:
        return f"⚠️ {e}"
    except JiraError as e:
        return f"⚠️ {e}"


@mcp.tool()
def jira_list_projects(max_results: int = 30) -> str:
    """List Jira projects visible to the token."""
    try:
        projects = client().list_projects(max_results=max_results)
        if not projects:
            return "No projects returned."
        lines = []
        for p in projects:
            key = p.get("key") or "?"
            name = p.get("name") or "?"
            lines.append(f"- **{key}** {name}")
        return "\n".join(lines)
    except MissingConfigError as e:
        return f"⚠️ {e}"
    except JiraError as e:
        return f"⚠️ {e}"


if __name__ == "__main__":
    mcp.run()
