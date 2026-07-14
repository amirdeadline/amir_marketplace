"""Thin Asana REST client built on httpx."""

from __future__ import annotations

import time
from typing import Any

import httpx

from .config import get_base_url, get_token

TASK_OPT_FIELDS = (
    "name,resource_type,completed,completed_at,due_on,due_at,start_on,"
    "notes,permalink_url,assignee.name,projects.name,parent.name,"
    "num_subtasks,modified_at,created_at,tags.name,"
    "custom_fields.name,custom_fields.display_value,custom_fields.enum_value.name"
)


class AsanaError(RuntimeError):
    """Raised for any non-success Asana API response."""

    def __init__(self, status: int, message: str, payload: Any = None):
        super().__init__(f"Asana API error {status}: {message}")
        self.status = status
        self.message = message
        self.payload = payload


class AsanaClient:
    """Minimal synchronous Asana API client."""

    def __init__(
        self,
        token: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        self._token = token or get_token()
        self._base_url = (base_url or get_base_url()).rstrip("/")
        self._max_retries = max_retries
        self._http = httpx.Client(
            base_url=self._base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/json",
            },
        )

    def __enter__(self) -> "AsanaClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        json_body = {"data": data} if data is not None else None

        attempt = 0
        while True:
            response = self._http.request(
                method, path, params=params, json=json_body
            )

            if response.status_code == 429 and attempt < self._max_retries:
                retry_after = float(response.headers.get("Retry-After", "1"))
                time.sleep(min(retry_after, 30.0))
                attempt += 1
                continue

            if response.status_code >= 400:
                raise self._to_error(response)

            if not response.content:
                return None
            return response.json().get("data")

    @staticmethod
    def _to_error(response: httpx.Response) -> AsanaError:
        message = response.reason_phrase or "request failed"
        payload: Any = None
        try:
            payload = response.json()
            errors = payload.get("errors")
            if errors:
                message = "; ".join(
                    e.get("message", str(e)) for e in errors
                )
        except (ValueError, AttributeError):
            payload = response.text
        return AsanaError(response.status_code, message, payload)

    def get_all(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        page_size: int = 100,
        max_items: int = 1000,
    ) -> list[dict[str, Any]]:
        params = dict(params or {})
        params.setdefault("limit", page_size)
        items: list[dict[str, Any]] = []
        offset: str | None = None

        while True:
            if offset:
                params["offset"] = offset
            response = self._http.get(path, params=params)
            if response.status_code >= 400:
                raise self._to_error(response)
            body = response.json()
            items.extend(body.get("data") or [])
            if len(items) >= max_items:
                return items[:max_items]
            next_page = body.get("next_page")
            offset = next_page.get("offset") if next_page else None
            if not offset:
                return items

    def get(self, path: str, **params: Any) -> Any:
        return self._request("GET", path, params=params or None)

    def post(self, path: str, data: dict[str, Any]) -> Any:
        return self._request("POST", path, data=data)

    def put(self, path: str, data: dict[str, Any]) -> Any:
        return self._request("PUT", path, data=data)

    def me(self) -> dict[str, Any]:
        return self._request("GET", "/users/me")

    def default_workspace_gid(self) -> str:
        me = self.me()
        workspaces = me.get("workspaces") or []
        if not workspaces:
            raise AsanaError(404, "User has no workspaces")
        return workspaces[0]["gid"]

    def list_sections(self, project_gid: str) -> list[dict[str, Any]]:
        return self.get_all(
            f"/projects/{project_gid}/sections",
            params={"opt_fields": "name"},
        )

    def add_task_to_section(self, task_gid: str, section_gid: str) -> None:
        self.post(f"/sections/{section_gid}/addTask", data={"task": task_gid})

    def create_subtask(self, parent_gid: str, data: dict[str, Any]) -> dict[str, Any]:
        return self.post(f"/tasks/{parent_gid}/subtasks", data=data)

    def list_tags(self, workspace_gid: str) -> list[dict[str, Any]]:
        return self.get_all(
            f"/workspaces/{workspace_gid}/tags",
            params={"opt_fields": "name"},
        )

    def create_tag(self, workspace_gid: str, name: str) -> dict[str, Any]:
        return self.post(f"/workspaces/{workspace_gid}/tags", data={"name": name})

    def add_tag_to_task(self, task_gid: str, tag_gid: str) -> None:
        self.post(f"/tasks/{task_gid}/addTag", data={"tag": tag_gid})

    def remove_tag_from_task(self, task_gid: str, tag_gid: str) -> None:
        self.post(f"/tasks/{task_gid}/removeTag", data={"tag": tag_gid})

    def resolve_tag_gids(
        self,
        workspace_gid: str,
        *,
        tag_gids: list[str] | None = None,
        tag_names: list[str] | None = None,
        create_missing: bool = False,
    ) -> list[str]:
        resolved = list(tag_gids or [])
        if not tag_names:
            return resolved

        existing = self.list_tags(workspace_gid)
        by_name = {
            (t.get("name") or "").strip().casefold(): t["gid"]
            for t in existing
            if t.get("gid")
        }

        for raw_name in tag_names:
            name = raw_name.strip()
            if not name:
                continue
            key = name.casefold()
            if key in by_name:
                gid = by_name[key]
                if gid not in resolved:
                    resolved.append(gid)
                continue
            if not create_missing:
                known = ", ".join(t.get("name", "?") for t in existing[:20]) or "(none)"
                raise AsanaError(
                    404,
                    f"Tag '{name}' not found in workspace {workspace_gid}. "
                    f"Known tags (sample): {known}",
                )
            created = self.create_tag(workspace_gid, name)
            gid = created["gid"]
            by_name[key] = gid
            resolved.append(gid)

        return resolved

    def apply_task_tags(
        self,
        task_gid: str,
        workspace_gid: str,
        *,
        add_tag_gids: list[str] | None = None,
        add_tag_names: list[str] | None = None,
        remove_tag_gids: list[str] | None = None,
        remove_tag_names: list[str] | None = None,
        create_missing: bool = False,
    ) -> tuple[list[str], list[str]]:
        """Add/remove tags on a task. Returns (added_gids, removed_gids)."""
        to_add = self.resolve_tag_gids(
            workspace_gid,
            tag_gids=add_tag_gids,
            tag_names=add_tag_names,
            create_missing=create_missing,
        )
        to_remove = self.resolve_tag_gids(
            workspace_gid,
            tag_gids=remove_tag_gids,
            tag_names=remove_tag_names,
            create_missing=False,
        )

        current = self.get(f"/tasks/{task_gid}", opt_fields="tags.gid")
        current_gids = {t["gid"] for t in (current.get("tags") or []) if t.get("gid")}

        added: list[str] = []
        for gid in to_add:
            if gid in current_gids:
                continue
            self.add_tag_to_task(task_gid, gid)
            added.append(gid)
            current_gids.add(gid)

        removed: list[str] = []
        for gid in to_remove:
            if gid not in current_gids:
                continue
            self.remove_tag_from_task(task_gid, gid)
            removed.append(gid)
            current_gids.discard(gid)

        return added, removed
