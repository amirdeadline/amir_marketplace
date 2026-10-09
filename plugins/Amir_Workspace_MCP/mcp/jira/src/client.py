from __future__ import annotations

from typing import Any

import httpx

from config import get_base_url, get_token


class JiraError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(f"Jira HTTP {status}: {message}")
        self.status = status
        self.message = message


class JiraClient:
    def __init__(self) -> None:
        self._http = httpx.Client(
            base_url=f"{get_base_url()}/rest/api/2",
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {get_token()}",
                "Accept": "application/json",
            },
        )

    def close(self) -> None:
        self._http.close()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        r = self._http.get(path, params=params or {})
        if r.status_code >= 400:
            raise JiraError(r.status_code, (r.text or "")[:400])
        return r.json()

    def search(self, jql: str, max_results: int = 25) -> dict[str, Any]:
        return self._get(
            "/search",
            {"jql": jql, "maxResults": min(max(max_results, 1), 50), "fields": "summary,status,assignee,updated,project"},
        )

    def get_issue(self, key: str) -> dict[str, Any]:
        return self._get(f"/issue/{key}", {"fields": "summary,description,status,assignee,reporter,updated,comment,project"})

    def list_projects(self, max_results: int = 50) -> list[dict[str, Any]]:
        cap = min(max(max_results, 1), 50)
        try:
            data = self._get("/project/search", {"maxResults": cap})
            return list(data.get("values") or [])
        except JiraError:
            data = self._get("/project")
            if isinstance(data, list):
                return data[:cap]
            return []
