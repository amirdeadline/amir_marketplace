---
name: asana-complete-task
description: >
  Complete (mark done) or remove one or more Asana tasks. Use when the user says
  "complete task", "mark done", "mark as complete", "remove task", "finish task",
  "close task", or provides a list of tasks to mark complete. "Remove" always means
  complete (reversible) — never delete. Requires one explicit confirmation for a batch.
---

# Complete / Remove Asana Task(s)

**Goal:** Find the target task(s), confirm with the user, then call `complete_task`
for each. Report the count of successes and failures.

## Steps

1. **Identify the task(s).**
   - GID provided → use directly.
   - Name provided → call `search_tasks(text=<name>)`, pick the best match.
   - Multiple names → resolve each independently; collect all GIDs.

2. **Show what will be completed** (fetch with `get_task` if needed):
   ```
   About to complete 2 task(s):
   ⬜ `1215253075355059` P0-01 GCP lab platform (due: 2026-03-15)
   ⬜ `1215253075355061` P0-03 Repo structure (due: 2026-03-25)

   Confirm? (yes / no)
   ```
   One confirmation covers the entire batch.

3. On "yes": call `complete_task(task_gid)` for each task in sequence.

4. Report results:
   ```
   ✅ Completed 2/2 tasks.
   ```
   List any failures with the error message.

5. Remind the user: "To reopen a task, say **reopen task <name or GID>**
   (uses `update_task(completed=False)`)."

## Guardrails

- **Never delete tasks.** "Remove" = complete (reversible via `update_task(completed=False)`).
- Always show the task list and get one explicit confirmation before acting.
- Do not complete tasks the user didn't explicitly name or select.
- If a search returns ambiguous results, ask the user to pick rather than guessing.
