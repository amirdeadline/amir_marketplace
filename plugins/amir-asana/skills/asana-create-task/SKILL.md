---
name: asana-create-task
description: >
  Create one or more new Asana tasks. Use when the user says "create a task",
  "add a task", "new task", "add to Asana", "create tasks for ...", or provides
  a list of items to track. Confirms before creating; never invents due dates.
---

# Create Asana Task(s)

**Goal:** Parse the user's request into one or more tasks, confirm the details,
then call `create_task` for each. Report the GID and permalink of each created task.

## Steps

1. Parse the request for one or more task items. Each item may include:
   - **Name** (required)
   - **Notes / description** (optional)
   - **Due date** in YYYY-MM-DD (optional — do NOT invent one if not mentioned)
   - **Project name** (optional)
   - **Section name** (optional — requires project; use `list_project_sections` to verify)
   - **Parent task** (optional — for subtasks/checklist items under an existing task)
   - **Tags** (optional — use `list_tags` to verify names; set `create_missing_tags=True` to create new tags)

2. If a project name is mentioned, call `list_projects` to find the matching GID.
   If a section name is mentioned, call `list_project_sections(project_gid)` to confirm
   the section exists (or pass `section_name` directly to `create_task`).
   If multiple projects match, ask the user to choose. If no match, offer to create
   the task without a project.

3. Show the parsed task(s) for confirmation:

```
**About to create:**
1. "P2-07 Snapshot restore test" · project: Prisma SD-WAN Lab · section: Backlog · due: 2026-07-10
2. "Export PDF diagram" · subtask of: Planning and Discovery
3. "Write release notes" · no project · no due date

**Confirm? (yes / edit / cancel)**
```

4. On "yes":
   - Top-level tasks → `create_task(name=..., project_gid=..., section_name=..., tag_names=[...], create_missing_tags=True)`
   - Subtasks → `create_subtask(parent_task_gid=..., name=..., tag_names=[...])` or `create_task(..., parent_task_gid=...)`
5. Report each result:
   - ✅ Created: **<name>** — GID `<gid>` · [Open](<permalink_url>)
   - ⚠️ Failed: **<name>** — <error message>

## Guardrails

- Never invent a due date that was not provided by the user.
- Always confirm before creating (no silent creation).
- "assign to me" is the default — only override if user explicitly says otherwise.
- If the user provides a project by name that doesn't exist, tell them rather than
  guessing a project GID.
