"""Amir Asana Connector — an MCP server exposing Asana operations as tools.

Run directly (stdio transport):
    python src/asana_connector/server.py
"""

from __future__ import annotations

import functools
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from asana_connector.client import (  # noqa: E402
    TASK_OPT_FIELDS,
    AsanaClient,
    AsanaError,
)
from asana_connector.config import MissingTokenError  # noqa: E402
from asana_connector.priority import (  # noqa: E402
    format_priority_badge,
    sort_tasks_by_importance,
)

mcp = FastMCP("Amir Asana Connector")

_client: AsanaClient | None = None


def client() -> AsanaClient:
    global _client
    if _client is None:
        _client = AsanaClient()
    return _client


def _guard(fn):
    """Wrap a tool so credential / API errors come back as readable text."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        try:
            return fn(*args, **kwargs)
        except MissingTokenError as exc:
            return f"⚠️ {exc}"
        except AsanaError as exc:
            return f"⚠️ Asana error ({exc.status}): {exc.message}"

    return wrapper


def _fmt_task_line(task: dict[str, Any]) -> str:
    done = "✅" if task.get("completed") else "⬜"
    name = task.get("name") or "(untitled)"
    gid = task.get("gid", "?")
    due = task.get("due_on") or task.get("due_at") or "no due date"
    projects = ", ".join(p.get("name", "") for p in task.get("projects") or [])
    suffix = f" · {projects}" if projects else ""
    return f"{done} `{gid}`  **{name}**  (due: {due}){suffix}"


def _fmt_priority_task_line(task: dict[str, Any], index: int) -> str:
    badge = format_priority_badge(task)
    name = task.get("name") or "(untitled)"
    gid = task.get("gid", "?")
    due = task.get("due_on") or task.get("due_at") or "no due date"
    projects = ", ".join(p.get("name", "") for p in task.get("projects") or [])
    proj_suffix = f" · {projects}" if projects else ""
    return f"{index}. {badge} **{name}** (due: {due}){proj_suffix} — `{gid}`"


def _resolve_workspace(workspace_gid: str | None) -> str:
    return workspace_gid or client().default_workspace_gid()


def _resolve_section(
    project_gid: str,
    *,
    section_gid: str | None = None,
    section_name: str | None = None,
) -> str:
    if section_gid:
        return section_gid
    if not section_name:
        raise AsanaError(400, "Provide section_gid or section_name")

    sections = client().list_sections(project_gid)
    needle = section_name.strip().casefold()
    matches = [
        s for s in sections if (s.get("name") or "").strip().casefold() == needle
    ]
    if len(matches) == 1:
        return matches[0]["gid"]
    if not matches:
        names = ", ".join(s.get("name", "?") for s in sections) or "(none)"
        raise AsanaError(
            404,
            f"Section '{section_name}' not found in project {project_gid}. "
            f"Available: {names}",
        )
    dupes = ", ".join(f"'{s.get('name')}'" for s in matches)
    raise AsanaError(400, f"Ambiguous section name '{section_name}': {dupes}")


def _build_subtask_data(
    name: str,
    *,
    notes: str | None = None,
    due_on: str | None = None,
    assign_to_me: bool = True,
    completed: bool = False,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {"name": name}
    if notes:
        data["notes"] = notes
    if due_on:
        data["due_on"] = due_on
    if assign_to_me:
        data["assignee"] = "me"
    if completed:
        data["completed"] = True
    if tags:
        data["tags"] = tags
    return data


def _resolve_task_tags(
    workspace_gid: str | None,
    *,
    tag_gids: list[str] | None = None,
    tag_names: list[str] | None = None,
    create_missing: bool = False,
) -> list[str]:
    if not tag_gids and not tag_names:
        return []
    ws = _resolve_workspace(workspace_gid)
    return client().resolve_tag_gids(
        ws,
        tag_gids=tag_gids,
        tag_names=tag_names,
        create_missing=create_missing,
    )


def _fetch_my_open_tasks(workspace_gid: str | None = None) -> list[dict[str, Any]]:
    c = client()
    params: dict[str, Any] = {
        "opt_fields": TASK_OPT_FIELDS,
        "limit": 100,
        "completed_since": "now",
        "assignee": "me",
        "workspace": _resolve_workspace(workspace_gid),
    }
    tasks = c.get_all("/tasks", params=params)
    return [t for t in tasks if not t.get("completed")]


@mcp.tool()
@_guard
def get_me() -> str:
    """Show the authenticated Asana user and their workspaces.

    Use this first to confirm the token works and to discover workspace GIDs.
    """
    me = client().me()
    lines = [
        f"**{me.get('name')}** ({me.get('email')})",
        f"User GID: `{me.get('gid')}`",
        "",
        "**Workspaces:**",
    ]
    for ws in me.get("workspaces") or []:
        lines.append(f"- {ws.get('name')} — `{ws.get('gid')}`")
    return "\n".join(lines)


@mcp.tool()
@_guard
def list_workspaces() -> str:
    """List all workspaces (and organizations) the user can access."""
    workspaces = client().get_all("/workspaces")
    if not workspaces:
        return "No workspaces found."
    return "\n".join(
        f"- {w.get('name')} — `{w.get('gid')}`" for w in workspaces
    )


@mcp.tool()
@_guard
def list_my_tasks(
    workspace_gid: str | None = None,
    include_completed: bool = False,
    project_gid: str | None = None,
    completed_since: str | None = None,
) -> str:
    """List tasks assigned to the current user.

    Args:
        workspace_gid: Workspace to search. Defaults to the user's first workspace.
        include_completed: Include completed tasks (default: only incomplete).
        project_gid: If given, list that project's tasks instead of by-assignee.
        completed_since: ISO-8601 date/time (e.g. "2026-05-30" or
            "2026-05-30T00:00:00Z"). Returns incomplete tasks PLUS tasks completed
            at/after this time — useful for "what did I finish recently" reports.
            Combine with include_completed=True and filter the result by `completed`.
    """
    c = client()
    params: dict[str, Any] = {"opt_fields": TASK_OPT_FIELDS, "limit": 100}

    if completed_since:
        params["completed_since"] = completed_since
    elif not include_completed:
        params["completed_since"] = "now"

    if project_gid:
        path = f"/projects/{project_gid}/tasks"
    else:
        path = "/tasks"
        params["assignee"] = "me"
        params["workspace"] = _resolve_workspace(workspace_gid)

    tasks = c.get_all(path, params=params)
    if not tasks:
        return "No matching tasks. 🎉"

    open_tasks = [t for t in tasks if not t.get("completed")]
    header = f"**{len(tasks)} task(s)** ({len(open_tasks)} open):\n"
    return header + "\n".join(_fmt_task_line(t) for t in tasks)


@mcp.tool()
@_guard
def list_priority_tasks_today(workspace_gid: str | None = None) -> str:
    """List all open tasks assigned to you, sorted by importance for today.

    Sort order: Asana Priority custom field (High → Medium → Low), then due-date
    urgency (overdue → due today → this week → later → no date), then name.

    Args:
        workspace_gid: Workspace to search. Defaults to the user's first workspace.
    """
    tasks = _fetch_my_open_tasks(workspace_gid)
    if not tasks:
        return "No open tasks assigned to you. 🎉"

    ranked = sort_tasks_by_importance(tasks)
    lines = [
        f"**{len(ranked)} open task(s)** — sorted by Priority, then due date:\n",
        "_Sort: [Priority field] → due urgency → name. [—] = no Priority field._\n",
    ]
    for i, task in enumerate(ranked, start=1):
        lines.append(_fmt_priority_task_line(task, i))

    lines.append("\n**Focus now (top 3):**")
    for task in ranked[:3]:
        lines.append(f"- {format_priority_badge(task)} **{task.get('name')}**")

    return "\n".join(lines)


@mcp.tool()
@_guard
def get_task(task_gid: str) -> str:
    """Show full detail for one task: notes, status, subtasks, and comments."""
    c = client()
    task = c.get(f"/tasks/{task_gid}", opt_fields=TASK_OPT_FIELDS)
    subtasks = c.get_all(
        f"/tasks/{task_gid}/subtasks",
        params={"opt_fields": "name,completed"},
        max_items=100,
    )
    stories = c.get_all(
        f"/tasks/{task_gid}/stories",
        params={"opt_fields": "text,created_by.name,created_at,type"},
        max_items=100,
    )

    lines = [
        f"# {task.get('name')}",
        f"GID: `{task.get('gid')}`  ·  "
        f"{'✅ completed' if task.get('completed') else '⬜ open'}",
        f"Due: {task.get('due_on') or task.get('due_at') or '—'}",
        f"Assignee: {(task.get('assignee') or {}).get('name', '—')}",
        f"Link: {task.get('permalink_url', '—')}",
    ]
    tags = task.get("tags") or []
    if tags:
        tag_names = ", ".join(t.get("name", "?") for t in tags)
        lines.append(f"Tags: {tag_names}")
    if task.get("notes"):
        lines += ["", "**Notes:**", task["notes"]]

    if subtasks:
        lines += ["", "**Subtasks:**"]
        for s in subtasks:
            mark = "✅" if s.get("completed") else "⬜"
            lines.append(f"- {mark} `{s.get('gid')}` {s.get('name')}")

    comments = [s for s in stories if s.get("type") == "comment"]
    if comments:
        lines += ["", "**Comments:**"]
        for s in comments:
            who = (s.get("created_by") or {}).get("name", "someone")
            lines.append(f"- _{who}_: {s.get('text')}")

    return "\n".join(lines)


@mcp.tool()
@_guard
def create_task(
    name: str,
    workspace_gid: str | None = None,
    project_gid: str | None = None,
    notes: str | None = None,
    due_on: str | None = None,
    assign_to_me: bool = True,
    section_gid: str | None = None,
    section_name: str | None = None,
    parent_task_gid: str | None = None,
    tag_gids: list[str] | None = None,
    tag_names: list[str] | None = None,
    create_missing_tags: bool = False,
) -> str:
    """Create a new task or subtask.

    Args:
        name: Task title (required).
        workspace_gid: Workspace for the task. Defaults to the first workspace.
        project_gid: Optional project to add the task to (required with section_*).
        notes: Optional description body.
        due_on: Optional due date as YYYY-MM-DD.
        assign_to_me: Assign the task to the current user (default True).
        section_gid: Place the new task in this section (requires project_gid).
        section_name: Resolve section by name within project_gid (requires project_gid).
        parent_task_gid: Create as a subtask under this parent (mutually exclusive
            with section_gid/section_name).
        tag_gids: Tag GIDs to apply at create time.
        tag_names: Resolve workspace tag names to GIDs (set create_missing_tags to
            create tags that do not exist yet).
        create_missing_tags: Create workspace tags named in tag_names when missing.
    """
    c = client()
    ws = _resolve_workspace(workspace_gid)
    resolved_tags = _resolve_task_tags(
        ws,
        tag_gids=tag_gids,
        tag_names=tag_names,
        create_missing=create_missing_tags,
    )

    if parent_task_gid and (section_gid or section_name):
        return (
            "⚠️ Cannot set section on a subtask — use parent_task_gid alone, "
            "or create a top-level task with section_gid/section_name."
        )

    if parent_task_gid:
        data = _build_subtask_data(
            name,
            notes=notes,
            due_on=due_on,
            assign_to_me=assign_to_me,
            tags=resolved_tags or None,
        )
        task = c.create_subtask(parent_task_gid, data)
        tag_line = ""
        if tag_names or tag_gids:
            tag_line = f"\nTags: {', '.join(tag_names or tag_gids or [])}"
        return (
            f"Created subtask `{task.get('gid')}` under `{parent_task_gid}` — "
            f"**{task.get('name')}**{tag_line}\n{task.get('permalink_url', '')}"
        )

    if (section_gid or section_name) and not project_gid:
        return "⚠️ section_gid or section_name requires project_gid."

    data: dict[str, Any] = {"name": name}
    if project_gid:
        data["projects"] = [project_gid]
    else:
        data["workspace"] = _resolve_workspace(workspace_gid)
    if notes:
        data["notes"] = notes
    if due_on:
        data["due_on"] = due_on
    if assign_to_me:
        data["assignee"] = "me"
    if resolved_tags:
        data["tags"] = resolved_tags

    task = c.post("/tasks", data=data)
    lines = [
        f"Created task `{task.get('gid')}` — **{task.get('name')}**",
        task.get("permalink_url", ""),
    ]
    if tag_names or tag_gids:
        lines.append(f"Tags: {', '.join(tag_names or tag_gids or [])}")

    if project_gid and (section_gid or section_name):
        resolved = _resolve_section(
            project_gid, section_gid=section_gid, section_name=section_name
        )
        c.add_task_to_section(task["gid"], resolved)
        label = section_name or section_gid
        lines.append(f"Placed in section: **{label}** (`{resolved}`)")

    return "\n".join(lines)


@mcp.tool()
@_guard
def update_task(
    task_gid: str,
    name: str | None = None,
    notes: str | None = None,
    completed: bool | None = None,
    due_on: str | None = None,
    assignee: str | None = None,
    project_gid: str | None = None,
    section_gid: str | None = None,
    section_name: str | None = None,
    workspace_gid: str | None = None,
    add_tag_gids: list[str] | None = None,
    add_tag_names: list[str] | None = None,
    remove_tag_gids: list[str] | None = None,
    remove_tag_names: list[str] | None = None,
    create_missing_tags: bool = False,
) -> str:
    """Update fields on an existing task. Only provided fields change.

    Args:
        task_gid: The task to update.
        name: New title.
        notes: New description body.
        completed: Mark complete (True) or reopen (False).
        due_on: New due date as YYYY-MM-DD (empty string clears it).
        assignee: User GID or "me" to reassign.
        project_gid: Required when moving the task to a section by name or gid.
        section_gid: Move task into this section (requires project_gid).
        section_name: Resolve section by name within project_gid.
        workspace_gid: Workspace for tag name resolution (defaults to first workspace).
        add_tag_gids: Tag GIDs to add to the task.
        add_tag_names: Tag names to add (resolved in workspace).
        remove_tag_gids: Tag GIDs to remove from the task.
        remove_tag_names: Tag names to remove (resolved in workspace).
        create_missing_tags: Create workspace tags in add_tag_names when missing.
    """
    c = client()
    ws = _resolve_workspace(workspace_gid)
    data: dict[str, Any] = {}
    if name is not None:
        data["name"] = name
    if notes is not None:
        data["notes"] = notes
    if completed is not None:
        data["completed"] = completed
    if due_on is not None:
        data["due_on"] = due_on or None
    if assignee is not None:
        data["assignee"] = assignee

    moving_section = bool(section_gid or section_name)
    if moving_section and not project_gid:
        return "⚠️ section_gid or section_name requires project_gid."

    tag_changes = bool(
        add_tag_gids or add_tag_names or remove_tag_gids or remove_tag_names
    )
    if not data and not moving_section and not tag_changes:
        return "Nothing to update — provide at least one field."

    task: dict[str, Any] | None = None
    if data:
        task = c.put(f"/tasks/{task_gid}", data=data)

    section_label: str | None = None
    if moving_section:
        resolved = _resolve_section(
            project_gid, section_gid=section_gid, section_name=section_name
        )
        c.add_task_to_section(task_gid, resolved)
        section_label = section_name or section_gid

    tag_summary: str | None = None
    if tag_changes:
        added, removed = c.apply_task_tags(
            task_gid,
            ws,
            add_tag_gids=add_tag_gids,
            add_tag_names=add_tag_names,
            remove_tag_gids=remove_tag_gids,
            remove_tag_names=remove_tag_names,
            create_missing=create_missing_tags,
        )
        parts: list[str] = []
        if add_tag_names or add_tag_gids:
            parts.append(f"added: {', '.join(add_tag_names or add_tag_gids or [])}")
        if remove_tag_names or remove_tag_gids:
            parts.append(
                f"removed: {', '.join(remove_tag_names or remove_tag_gids or [])}"
            )
        if parts:
            tag_summary = "; ".join(parts)
        elif added or removed:
            tag_summary = f"added {len(added)} tag(s), removed {len(removed)} tag(s)"

    if task is None:
        task = c.get(f"/tasks/{task_gid}", opt_fields="name,completed")

    result = (
        f"Updated task `{task.get('gid')}` — **{task.get('name')}** "
        f"({'✅ completed' if task.get('completed') else '⬜ open'})"
    )
    if section_label:
        result += f"\nMoved to section: **{section_label}**"
    if tag_summary:
        result += f"\nTags: {tag_summary}"
    return result


@mcp.tool()
@_guard
def complete_task(task_gid: str) -> str:
    """Mark a task as completed (convenience wrapper around update_task)."""
    task = client().put(f"/tasks/{task_gid}", data={"completed": True})
    return f"✅ Completed `{task.get('gid')}` — **{task.get('name')}**"


@mcp.tool()
@_guard
def add_comment(task_gid: str, text: str) -> str:
    """Add a comment (story) to a task."""
    story = client().post(f"/tasks/{task_gid}/stories", data={"text": text})
    return f"Added comment to `{task_gid}` (story `{story.get('gid')}`)."


@mcp.tool()
@_guard
def list_projects(workspace_gid: str | None = None) -> str:
    """List projects in a workspace (defaults to the first workspace)."""
    ws = _resolve_workspace(workspace_gid)
    projects = client().get_all(
        "/projects", params={"workspace": ws, "opt_fields": "name,archived"}
    )
    active = [p for p in projects if not p.get("archived")]
    if not active:
        return "No active projects found."
    return "\n".join(f"- {p.get('name')} — `{p.get('gid')}`" for p in active)


@mcp.tool()
@_guard
def list_project_tasks(project_gid: str, include_completed: bool = False) -> str:
    """List all tasks in a given project."""
    params: dict[str, Any] = {"opt_fields": TASK_OPT_FIELDS}
    if not include_completed:
        params["completed_since"] = "now"
    tasks = client().get_all(f"/projects/{project_gid}/tasks", params=params)
    if not tasks:
        return "No tasks in this project."
    return f"**{len(tasks)} task(s):**\n" + "\n".join(
        _fmt_task_line(t) for t in tasks
    )


@mcp.tool()
@_guard
def search_tasks(text: str, workspace_gid: str | None = None) -> str:
    """Find tasks by name using Asana typeahead (works on all plans).

    Args:
        text: The text to match against task names.
        workspace_gid: Workspace to search (defaults to the first workspace).
    """
    ws = _resolve_workspace(workspace_gid)
    results = client().get(
        f"/workspaces/{ws}/typeahead",
        resource_type="task",
        query=text,
        count=20,
        opt_fields="name,completed,due_on",
    )
    if not results:
        return f"No tasks matching '{text}'."
    return f"**Matches for '{text}':**\n" + "\n".join(
        _fmt_task_line(t) for t in results
    )


@mcp.tool()
@_guard
def list_project_sections(project_gid: str) -> str:
    """List sections in a project (names and GIDs).

    Args:
        project_gid: The project to list sections for.
    """
    sections = client().list_sections(project_gid)
    if not sections:
        return "No sections in this project."
    return "\n".join(
        f"- {s.get('name')} — `{s.get('gid')}`" for s in sections
    )


@mcp.tool()
@_guard
def list_section_tasks(
    section_gid: str,
    include_completed: bool = False,
    assignee_me: bool = False,
) -> str:
    """List tasks in a project section.

    Args:
        section_gid: The section to list tasks from.
        include_completed: Include completed tasks (default: only incomplete).
            Set True when locating a parent task that may already be marked done.
        assignee_me: If True, only tasks assigned to the current user.
    """
    params: dict[str, Any] = {"opt_fields": TASK_OPT_FIELDS}
    if not include_completed:
        params["completed_since"] = "now"
    tasks = client().get_all(f"/sections/{section_gid}/tasks", params=params)

    if assignee_me:
        me_gid = client().me()["gid"]
        tasks = [
            t
            for t in tasks
            if (t.get("assignee") or {}).get("gid") == me_gid
        ]

    if not tasks:
        return "No matching tasks in this section."
    open_tasks = [t for t in tasks if not t.get("completed")]
    header = f"**{len(tasks)} task(s)** ({len(open_tasks)} open):\n"
    return header + "\n".join(_fmt_task_line(t) for t in tasks)


@mcp.tool()
@_guard
def add_task_to_section(task_gid: str, section_gid: str) -> str:
    """Move an existing task into a project section.

    The task must already belong to the project that contains the section.

    Args:
        task_gid: Task to move.
        section_gid: Target section GID (from list_project_sections).
    """
    client().add_task_to_section(task_gid, section_gid)
    return f"Moved task `{task_gid}` to section `{section_gid}`."


@mcp.tool()
@_guard
def create_subtask(
    parent_task_gid: str,
    name: str,
    notes: str | None = None,
    due_on: str | None = None,
    assign_to_me: bool = True,
    completed: bool = False,
    tag_gids: list[str] | None = None,
    tag_names: list[str] | None = None,
    create_missing_tags: bool = False,
    workspace_gid: str | None = None,
) -> str:
    """Create a subtask under an existing parent task.

    Args:
        parent_task_gid: Parent task GID.
        name: Subtask title (required).
        notes: Optional description.
        due_on: Optional due date as YYYY-MM-DD.
        assign_to_me: Assign to current user (default True).
        completed: Create already completed (default False).
        tag_gids: Tag GIDs to apply at create time.
        tag_names: Resolve workspace tag names to GIDs.
        create_missing_tags: Create workspace tags in tag_names when missing.
        workspace_gid: Workspace for tag resolution (defaults to first workspace).
    """
    ws = _resolve_workspace(workspace_gid)
    resolved_tags = _resolve_task_tags(
        ws,
        tag_gids=tag_gids,
        tag_names=tag_names,
        create_missing=create_missing_tags,
    )
    data = _build_subtask_data(
        name,
        notes=notes,
        due_on=due_on,
        assign_to_me=assign_to_me,
        completed=completed,
        tags=resolved_tags or None,
    )
    task = client().create_subtask(parent_task_gid, data)
    tag_line = ""
    if tag_names or tag_gids:
        tag_line = f"\nTags: {', '.join(tag_names or tag_gids or [])}"
    return (
        f"Created subtask `{task.get('gid')}` under `{parent_task_gid}` — "
        f"**{task.get('name')}**{tag_line}\n{task.get('permalink_url', '')}"
    )


@mcp.tool()
@_guard
def list_tags(workspace_gid: str | None = None) -> str:
    """List tags in a workspace (names and GIDs).

    Args:
        workspace_gid: Workspace to list tags from. Defaults to the first workspace.
    """
    ws = _resolve_workspace(workspace_gid)
    tags = client().list_tags(ws)
    if not tags:
        return "No tags in this workspace."
    return "\n".join(f"- {t.get('name')} — `{t.get('gid')}`" for t in tags)


if __name__ == "__main__":
    mcp.run()
