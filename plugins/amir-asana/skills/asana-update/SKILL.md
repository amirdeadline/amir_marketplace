---
name: amir-asana-update
description: >
  Sync Asana from an asana_tasks.md backlog file. Use when the user says
  "/asana_update", "asana update", "sync asana_tasks.md", or provides a path to
  an asana_tasks.md-style markdown backlog. Creates/updates main tasks, subtasks,
  comments, due dates, completion, sections, and tags. Asks for project and section
  if missing from the file.
---

# Asana Update — sync from `asana_tasks.md`

**Goal:** Read a structured backlog markdown file, confirm scope, then sync all
**Main task** blocks to Asana (parent tasks in a project section + subtasks + comments).

## Trigger

- `/asana_update <path-to-asana_tasks.md>`
- "Update Asana from this backlog file: …"
- User attaches or pastes `asana_tasks.md`

## Expected markdown format

The file MUST contain (or you MUST collect from the user):

| Field | Required |
|-------|----------|
| **Asana project** | Yes — in header table OR ask user |
| **Asana section** | Yes — in header table OR ask user |

Each main block:

```markdown
### Main task: Title Here

**Phase target:** 2026-06-04 · **Phase status:** In progress

| Subtask | Due | Status | Notes |
|---------|-----|--------|-------|
| Do something | 2026-06-10 | Done | optional notes |
| Next step | 2026-06-15 | Open | |

**Comments**

- **2026-06-04** `[tag]` — Comment text here.
```

**Status rules:** `Done` → complete subtask; `Open` or `In progress` → leave open.

## Workflow

### Phase 1 — Read file

1. Read the path the user gave (absolute or workspace-relative).
2. Parse header for **Asana project** and **Asana section**.
3. If either is missing, **ask the user** before continuing:
   - "Which Asana project should I use?"
   - "Which section within that project?"
4. Count main tasks and subtasks; note **Program deadline** if present.

### Phase 2 — Resolve Asana targets

5. `get_me` — confirm token works.
6. `list_projects` — resolve project name → `project_gid`.
7. `list_project_sections(project_gid)` — resolve section name → `section_gid`.
8. If names are ambiguous, list candidates and ask the user to pick.

### Phase 3 — Propose (always confirm before write)

9. Show a summary:

```
**Asana update plan (confirm to apply):**
Project: SASE COE Activities (`1211947877816998`)
Section: Prisma SDWAN S&O (`1215000616630571`)
Main tasks: 8 · Subtasks: 105

1. Discovery & Planning — 24 subtasks, 6 comments
2. Maturity Assessment — 12 subtasks, 13 comments
...

Apply full sync? (yes / no / limit N)
```

10. Wait for explicit **yes** (or "limit 3" etc.) before writing.

### Phase 4 — Apply

**Preferred (full file, fast):** run the sync script:

```powershell
cd e:\PC3_Shared\Palo\asana\Amir_Asana_Claude
.\.venv\Scripts\python.exe scripts\sync_asana_tasks_md.py "<absolute-path-to-md>"
```

Optional overrides:

```powershell
.\.venv\Scripts\python.exe scripts\sync_asana_tasks_md.py "<path>" --project "Name" --section "Name"
.\.venv\Scripts\python.exe scripts\sync_asana_tasks_md.py "<path>" --limit 3
.\.venv\Scripts\python.exe scripts\sync_asana_tasks_md.py "<path>" --dry-run
```

**Alternative (MCP-only, smaller batches):** for each main task:

1. Find or create parent: `create_task(name=..., project_gid=..., section_name=..., due_on=phase_target)`
   - Or match existing via `search_tasks` / `list_section_tasks(section_gid, include_completed=True)`
2. For each subtask row: `create_subtask(parent_task_gid=..., name=..., due_on=..., completed=...)`
   - Or `update_task` if subtask already exists (match by name)
3. Add comments: `add_comment(parent_gid, text=...)`
4. Tags: `update_task(..., add_tag_names=[...], create_missing_tags=True)`

Use `list_section_tasks(..., include_completed=True)` — completed parents are hidden by default.

### Phase 5 — Report

11. Print per main task: title, GID, permalink, subtasks created/updated, comments added.
12. List any errors without stopping the whole run (script collects errors per task).
13. Optionally suggest updating **Last synced** date in the markdown file (ask first).

## Guardrails

- Never sync without project + section (from file or user).
- Never delete tasks or subtasks — only create, update, complete, comment, tag.
- Do not invent due dates or statuses not in the markdown table.
- Idempotent: re-running should skip duplicate comments (same sync prefix + body).
- Legacy subtasks in Asana with different names are left untouched (not deleted).

## Related tools

| Tool | Use |
|------|-----|
| `list_project_sections` | Resolve section GID |
| `list_section_tasks` | Inspect section; use `include_completed=True` |
| `create_task` | New parent in section |
| `create_subtask` | Checklist items |
| `update_task` | Due date, complete, tags, move section |
| `add_comment` | Phase comments on parent |
| `list_tags` | Discover tag names |
