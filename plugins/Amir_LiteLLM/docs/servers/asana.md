# Asana MCP Server

The **asana** server exposes Asana work-management (workspaces, organizations, teams, projects, and tasks) through the Palo Alto MCP gateway. It lets an agent list and search Asana objects and create or update tasks. All tools are namespaced `mcp__mcp-gateway__asana__<tool>` and reached over the gateway from the `claude-code` client.

## Authentication

- **Credential (by name):** Asana Personal Access Token — referenced as **`ASANA_PAT`**.
- **How it is supplied:**
  - **Gateway environment (default):** the gateway reads the token from the `ASANA_PAT` environment variable when no per-call token is given.
  - **Per-call passthrough (optional):** every tool accepts an optional `asana_token` argument that overrides the environment token for that single call.
- **Access path:** `claude-code` → `mcp-gateway` (`https://api.mcp.pan.dev`) → `asana` upstream server. The gateway may perform an auth handshake on the first call in a session.
- **Secret handling:** refer to the credential by name only. Never paste, print, or invent the token value in tool calls, docs, or logs.

## Tools

### mcp__mcp-gateway__asana__get_workspaces

- **What it does:** Lists all accessible Asana workspaces, or finds a specific one by name or GID.
- **Details:** Returns `gid`, `name`, and `is_organization` for each workspace. Read-only. This is the usual starting point because most other tools need a `workspace_gid`. Uses the `ASANA_PAT` env token unless `asana_token` is passed.
- **Key parameters:**
  - `workspace_name` — string — no — case-insensitive partial match; returns the first matching workspace.
  - `workspace_gid` — string — no — fetch one specific workspace by GID.
  - `limit` — integer — no — max results (default 50, max 100).
  - `asana_token` — string — no — per-call token override.
- **Usage:** Call with no arguments to enumerate workspaces, e.g. `{}`. Use this first to obtain a `workspace_gid` for the other tools.

### mcp__mcp-gateway__asana__get_teams

- **What it does:** Lists teams in an Asana organization, or finds a specific team by name or GID.
- **Details:** Teams exist only in Asana **organizations**, not personal workspaces. Requires an organization workspace context (`workspace_gid` or `workspace_name`). Read-only.
- **Key parameters:**
  - `workspace_gid` — string — required unless `workspace_name` — the organization GID.
  - `workspace_name` — string — no — find the organization by name instead of GID.
  - `team_name` — string — no — search for a team by name (partial match).
  - `team_gid` — string — no — fetch one specific team by GID.
  - `limit` — integer — no — max results (default 50, max 100).
  - `asana_token` — string — no — per-call token override.
- **Usage:** `{"workspace_gid": "12345", "team_name": "Platform"}` to find a team within an org.

### mcp__mcp-gateway__asana__get_projects

- **What it does:** Lists projects in a workspace, or finds a specific project by name or GID.
- **Details:** Read-only. Can filter by archived status. With neither `project_name` nor `project_gid`, lists all projects in the workspace.
- **Key parameters:**
  - `workspace_gid` — string — required unless `workspace_name` — workspace to list projects from.
  - `workspace_name` — string — no — find the workspace by name instead of GID.
  - `project_name` — string — no — search for a project by name (partial match).
  - `project_gid` — string — no — fetch one specific project by GID.
  - `archived` — boolean — no — filter by archived status (true/false).
  - `limit` — integer — no — max results (default 50, max 100).
  - `asana_token` — string — no — per-call token override.
- **Usage:** `{"workspace_gid": "12345"}` to list all projects, or add `project_name` to search.

### mcp__mcp-gateway__asana__get_project_tasks

- **What it does:** Lists all tasks in a given Asana project.
- **Details:** Read-only. Locate the project by `project_gid`, or by `project_name` together with `workspace_gid`/`workspace_name`. Can restrict to tasks completed since a timestamp. Returns tasks with `gid`, `name`, and `resource_type`.
- **Key parameters:**
  - `project_gid` — string — required unless `project_name` given — project to read tasks from.
  - `project_name` — string — no — find the project by name; requires `workspace_gid` or `workspace_name`.
  - `workspace_gid` — string — no — required when using `project_name`.
  - `workspace_name` — string — no — alternative to `workspace_gid` when using `project_name`.
  - `completed_since` — string — no — ISO 8601 timestamp; only return tasks completed since this time.
  - `limit` — integer — no — max results (default 50, max 100).
  - `asana_token` — string — no — per-call token override.
- **Usage:** `{"project_gid": "67890", "limit": 100}` to page through a project's tasks.

### mcp__mcp-gateway__asana__search_tasks

- **What it does:** Searches tasks by text across a workspace, or retrieves the full detail of one task by GID.
- **Details:** Read-only. When `task_gid` is provided, returns the full details of that single task; otherwise performs a text search over task names/descriptions with optional filters (assignee, project, completion state).
- **Key parameters:**
  - `workspace_gid` — string — required unless `workspace_name` — workspace to search in.
  - `workspace_name` — string — no — find the workspace by name instead of GID.
  - `query` — string — no — text to match in task names and descriptions.
  - `task_gid` — string — no — retrieve full details for one specific task (bypasses search).
  - `assignee_gid` — string — no — filter by assignee user GID.
  - `project_gid` — string — no — filter by project GID.
  - `project_name` — string — no — filter by project name; requires `workspace_gid`/`workspace_name`.
  - `completed` — boolean — no — filter by completion status.
  - `limit` — integer — no — max results (default 25, max 100).
  - `asana_token` — string — no — per-call token override.
- **Usage:** `{"workspace_gid": "12345", "query": "onboarding"}` to search, or `{"task_gid": "111", "workspace_gid": "12345"}` to fetch one task's full detail.

### mcp__mcp-gateway__asana__create_task

- **What it does:** Creates a new task in a workspace.
- **Details:** **State-changing write — approval-gated in practice.** Optionally adds the task to projects, assigns it, and sets dates. Returns the created task's details including `gid` and `permalink_url`.
- **Key parameters:**
  - `workspace_gid` — string — required — workspace to create the task in.
  - `name` — string — required — task title.
  - `projects` — list of strings — no — project GIDs to add the task to.
  - `notes` — string — no — plain-text description.
  - `due_on` — string — no — due date in `YYYY-MM-DD` format.
  - `start_on` — string — no — start date in `YYYY-MM-DD` format.
  - `assignee` — string — no — user GID to assign, or `'me'` for the authenticated user.
  - `asana_token` — string — no — per-call token override.
- **Usage:** `{"workspace_gid": "12345", "name": "Draft report", "assignee": "me", "due_on": "2026-10-15"}`. Requires owner approval before invoking.

### mcp__mcp-gateway__asana__update_task

- **What it does:** Updates fields of an existing task.
- **Details:** **State-changing write — approval-gated in practice.** Only the fields you provide are changed. Sentinel values: pass an empty string `""` to clear a date field, and the string `'null'` to unassign. Returns the updated task details.
- **Key parameters:**
  - `task_gid` — string — required — the task to update.
  - `name` — string — no — new title.
  - `notes` — string — no — new plain-text description.
  - `due_on` — string — no — new due date `YYYY-MM-DD`, or `""` to clear.
  - `start_on` — string — no — new start date `YYYY-MM-DD`, or `""` to clear.
  - `assignee` — string — no — new assignee GID, or `'null'` to unassign.
  - `completed` — boolean — no — mark the task complete (true) or incomplete (false).
  - `asana_token` — string — no — per-call token override.
- **Usage:** `{"task_gid": "222", "completed": true}` to close a task, or `{"task_gid": "222", "due_on": ""}` to clear its due date. Requires owner approval before invoking.
