---
name: amir-asana-review-tasks
description: >
  Review all of Amir's Asana tasks. Use when the user says "review my tasks",
  "show all my tasks", "what's on my plate", "task overview", "what do I have",
  "asana summary", or asks for a full task sweep. Read-only — proposes actions
  but does not apply them.
---

# Asana Task Review

**Goal:** Produce a full, prioritised sweep of all active tasks grouped by urgency.
This skill is read-only — propose actions, but do not apply any changes.

## Steps

1. Call `get_me` to confirm the connected user and note all workspace GIDs.
2. Call `list_my_tasks` for each workspace (omit workspace_gid to auto-resolve).
3. Classify each task into one of four buckets using today's date:
   - **🔴 Overdue** — `due_on` is in the past
   - **🟡 Due soon** — `due_on` is within the next 3 days (inclusive)
   - **🟢 Upcoming** — `due_on` is 4+ days away
   - **⬜ No due date** — `due_on` is null
4. Within each bucket, sort by `due_on` ascending (nulls last).
5. Render a Markdown table for each bucket: Task | Project | Due | GID
6. After the tables, provide a brief prioritised recommendation:
   - Name the top 3 most urgent items.
   - Flag any tasks that appear stale (modified_at > 30 days ago, no due date).
   - Suggest any obvious quick wins (tasks with "simple" or short names).
7. Close with: "To update tasks, say **update task** or **complete task**."

## Guardrails

- Do NOT call `update_task`, `complete_task`, or `add_comment`.
- Do NOT invent due dates.
- If there are zero tasks, say so clearly rather than showing empty tables.
