---
name: asana-standup
description: >
  Generate a daily standup report from Asana. Use when the user says "standup",
  "daily standup", "standup report", "what did I do yesterday", "what's my plan
  for today", "morning report", or "yesterday / today blockers". READ-ONLY —
  makes absolutely no changes to any tasks.
---

# Asana Daily Standup (Read-Only)

**Goal:** Produce a clean standup report: what was completed yesterday, what is
planned today, and any blockers. Makes **no changes** whatsoever.

## Steps

1. Determine yesterday's ISO date (today minus 1 day, format YYYY-MM-DD).
2. Call `list_my_tasks(include_completed=True, completed_since=<yesterday-ISO>)`.
   Filter the result client-side to `completed == true` — these are "done yesterday."
3. Call `list_my_tasks()` (defaults: active tasks only) for "today's plan."
4. From today's plan, identify tasks with `due_on` ≤ today as potential blockers
   or highest-priority items.
5. Render the report in this exact format:

```
## 🟢 Yesterday — Done
- ✅ **<task name>** · <project> (gid: `<gid>`)
  _(no items if none completed yesterday)_

## 🔵 Today — Planned
- ⬜ **<task name>** (due: <due_on>) · <project>
  _(sorted by due_on ascending, then alphabetically)_

## ⚠️ Blockers / Risks
- List any task that is already overdue (due_on < today).
- If none, write "None identified."
```

6. End with a one-line summary count: e.g. "1 completed · 8 planned · 2 overdue."

## Guardrails

- **Absolutely no writes.** Do NOT call `update_task`, `complete_task`, or `add_comment`.
- Do not add or infer due dates.
- If `completed_since` returns tasks you can't confirm as yesterday completions,
  note the uncertainty rather than guessing.
