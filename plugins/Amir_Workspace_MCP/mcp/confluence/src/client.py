from __future__ import annotations

from typing import Any

import httpx

from config import get_base_url, get_token


class ConfluenceError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(f"Confluence HTTP {status}: {message}")
        self.status = status
        self.message = message


class ConfluenceClient:
    def __init__(self) -> None:
        self._base = get_base_url()
        self._http = httpx.Client(
            base_url=f"{self._base}/rest/api",
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
            raise ConfluenceError(r.status_code, (r.text or "")[:400])
        return r.json()

    def search_cql(self, cql: str, limit: int = 25) -> list[dict[str, Any]]:
        data = self._get("/content/search", {"cql": cql, "limit": min(max(limit, 1), 50)})
        return list(data.get("results") or [])

    def get_page(self, page_id: str, expand: str = "body.storage,version,space") -> dict[str, Any]:
        return self._get(f"/content/{page_id}", {"expand": expand})

    def get_children(self, page_id: str, limit: int = 25, start: int = 0) -> dict[str, Any]:
        return self._get(f"/content/{page_id}/child/page", {"limit": limit, "start": start})

    def get_comments(self, page_id: str, limit: int = 25) -> list[dict[str, Any]]:
        data = self._get(
            "/content/search",
            {"cql": f"type=comment AND container={page_id}", "limit": min(max(limit, 1), 50)},
        )
        return list(data.get("results") or [])
