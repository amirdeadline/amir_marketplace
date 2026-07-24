---
name: asana_sync_from_report
description: >
  Sync Asana from a conversation, status report, or log file. Use when the user
  says "sync Asana from this report", "update tasks from log", "process this status
  update", or attaches/pastes a .log, markdown report, or transcript. Applies
  changes only after one explicit confirmation.
---

# Asana — Sync from Report / Log

**Goal:** Parse a report, log, or conversation transcript into concrete Asana updates
(comments, due-date changes, completions, new tasks), confirm once, then apply.

## Steps

### Phase 1 — Ingest (read-only)

1. Read the attached file or pasted text.
2. Extract structured actions. Each item should include:
   - **Task identifier** — name fragment, ticket ID, or GID if present
   - **Action** — comment / reschedule / complete / create / move_section / create_subtask / add_tags / remove_tags
   - **Payload** — comment text, new `due_on` (YYYY-MM-DD), task name + notes for creates,
     section name for placement, parent task for subtasks

### Phase 2 — Match

3. For each item, resolve the task:
   - GID in source → use directly
   - Name → `search_tasks(text=<name>)`
   - If ambiguous, list candidates and ask the user to pick
4. For creates, resolve project via `list_projects` if a project name is mentioned.
5. For section placement, resolve via `list_project_sections(project_gid)` or pass
   `section_name` to `create_task` / `update_task`.
6. When matching an existing parent in a section, use `list_section_tasks(section_gid,
   include_completed=True)` or `search_tasks` — default section lists hide completed tasks.
7. For subtasks, resolve parent via GID or `search_tasks`, then use `create_subtask`.

### Phase 3 — Propose

5. Render a numbered batch plan:

```
**Proposed Asana updates (confirm to apply):**
1. 💬 Comment on "P2-03" — "Completed underlay validation; see log line 142"
2. ✏️ Reschedule "Environment Build" — due_on: 2026-06-07
3. ✅ Complete "LAB Architecture"
4. ➕ Create "Write release notes" in project X / section Y (no due date)
5. 📂 Move "Environment Build" to section "In Progress"
6. 🔗 Create subtask "Export PDF" under "Planning and Discovery"
```

6. Ask: **"Apply all N changes? (yes / no / edit)"**

### Phase 4 — Apply (only after "yes")

7. Execute in order:
   - Comment → `add_comment(task_gid, text=...)`
   - Reschedule → `update_task(task_gid, due_on=...)`
   - Complete → `complete_task(task_gid)`
   - Create → `create_task(name=..., project_gid=..., section_name=...)`
   - Move to section → `add_task_to_section(task_gid, section_gid)` or
     `update_task(task_gid, project_gid=..., section_name=...)`
   - Subtask → `create_subtask(parent_task_gid=..., name=...)`
   - Add tags → `update_task(task_gid=..., add_tag_names=[...], create_missing_tags=True)`
   - Remove tags → `update_task(task_gid=..., remove_tag_names=[...])`
8. Report: "Applied N/N changes" or list failures with error messages.

## Guardrails

- Never apply before explicit "yes".
- Never delete tasks — "remove" means `complete_task` (reversible).
- Do not invent due dates not implied by the source.
- Quote relevant log lines in comments when useful.
- If the source is ambiguous, ask rather than guess.
