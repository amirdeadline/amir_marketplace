---
name: amir-asana-daily-triage
description: >
  Triage the day's Asana tasks and apply updates after confirmation. Use when
  the user says "triage my tasks", "triage my day", "clean up my tasks", or
  "reschedule overdue tasks". Unlike standup, this skill APPLIES proposed changes
  after one explicit confirmation.
---

# Asana Daily Triage

**Goal:** Review active tasks, propose a concrete action plan (reschedule, complete,
comment), then apply ALL proposed changes after a single explicit user confirmation.

## Steps

### Phase 1 — Gather (read-only)

1. Call `list_priority_tasks_today` or `list_my_tasks()` to get all active tasks.
2. Classify into:
   - **Overdue** (`due_on` < today)
   - **Due today** (`due_on` == today)
   - **Due this week** (`due_on` within 7 days)
   - **Later / no date**

### Phase 2 — Propose

3. For each task, suggest ONE concrete action:
   - *Reschedule* — propose a new `due_on` (don't invent random dates; use end-of-week
     or end-of-month as sensible defaults and explain the choice).
   - *Complete* — if the task appears done or irrelevant based on its name/notes.
   - *Add comment* — if clarification or a status note would help.
   - *No change* — if the task is correctly scheduled and actively in progress.
4. Present the full proposal as a numbered list. Example:

```
**Proposed changes (confirm to apply):**
1. ✏️ Reschedule "Environment Build" → 2026-06-07 (end of this week)
2. ✅ Complete "LAB Architecture" (already marked done in name)
3. 💬 Add comment to "P2-03 Underlay validation": "Carrying over — blocked on VyOS build"
4. — No change: "Follow Up with Product Team" (due today, keep)
```

5. Ask: **"Apply all N changes? (yes / no / edit)"**
   - "yes" → proceed to Phase 3.
   - "no" → stop, make no changes.
   - "edit" → let the user modify individual items, then re-confirm.

### Phase 3 — Apply (only after explicit "yes")

6. Execute each proposed change in order:
   - Reschedule → `update_task(task_gid, due_on=<new_date>)`
   - Complete → `complete_task(task_gid)`
   - Comment → `add_comment(task_gid, text=<proposed_text>)`
7. Report results: "Applied 3/4 changes. 1 skipped (API error — see below)."

## Guardrails

- Never apply any change before the user says "yes" (or equivalent confirmation).
- Do NOT delete tasks. "Remove" means `complete_task`, which is reversible.
- Do NOT invent due dates that are unreasonably far out or in the past.
- One confirmation covers the entire batch — don't ask per-item.
