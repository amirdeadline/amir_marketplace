---
name: asana_update_task
description: >
  Update a single Asana task. Use when the user says "update task", "change task",
  "rename task", "set due date", "reschedule", "change notes", "add notes to task",
  "reassign task", or provides a task name/GID and a change to make.
---

# Update Asana Task

**Goal:** Find the target task, show the user what will change, apply the update,
and confirm success.

## Steps

1. **Identify the task.**
   - If the user provides a GID directly → use it.
   - If the user provides a name or partial name → call `search_tasks(text=<name>)`.
   - If multiple results, show them and ask the user to pick one.

2. **Fetch current state** with `get_task(task_gid)` and display it to the user.

3. **Parse the requested change(s):**
   - Name change → `name=<new_name>`
   - Notes / description → `notes=<text>`
   - Due date → `due_on=<YYYY-MM-DD>`. If user says "clear due date", pass `due_on=""`.
   - Complete / reopen → use `complete_task` or `update_task(completed=False)`.
   - Comment → use `add_comment` (not `update_task`).

4. **Confirm** the proposed change:
   ```
   Update "P2-03 Underlay validation":
   - due_on: 2026-06-21 → 2026-06-28
   Proceed? (yes / no)
   ```

5. On "yes", call `update_task(task_gid, <fields>)` (or `complete_task` / `add_comment`).

6. Show the updated task summary.

## Guardrails

- Dates must be YYYY-MM-DD. If user gives a relative date ("next Friday"), compute
  the correct absolute date before calling the tool.
- Empty string `""` for `due_on` clears the date — don't pass `None` directly.
- Always confirm before writing (unless the user's original request was unambiguous
  AND a single field is being changed — use judgment).
- Never update `completed` via `update_task` for simple completions; use `complete_task`
  for clarity. Use `update_task(completed=False)` to reopen.
