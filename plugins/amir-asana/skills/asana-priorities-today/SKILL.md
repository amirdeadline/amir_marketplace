---
name: asana-priorities-today
description: >
  Show today's most important Asana tasks, fully sorted by priority. Use when the
  user says "most important tasks today", "what should I focus on", "highest priority
  tasks", "show my Asana priorities", or asks the Asana agent what to work on today.
  Read-only unless the user asks to act on a task.
---

# Asana — Today's Priorities

**Goal:** Show every open assigned task, ranked by importance (Asana Priority field,
then due-date urgency). Read-only by default.

## Steps

1. Call `list_priority_tasks_today` (single tool — works across Cursor, Gemini, etc.).
2. Present the **full** ranked list — do not truncate unless the user asks.
3. Add a short **Focus now** callout for the top 3 items (the tool includes this; expand if helpful).
4. Explain sort order briefly: Priority custom field (High → Medium → Low) → overdue → due today → this week → later → no date.
5. If any task shows `[—]`, note that no Priority custom field is set on that task.
6. Offer optional next steps: reschedule, complete, or comment — but do NOT act until asked.

## Guardrails

- Read-only by default — no `update_task`, `complete_task`, or `add_comment` without explicit user request.
- Do not invent due dates or priorities.
- Show all tasks, not just the top few.
