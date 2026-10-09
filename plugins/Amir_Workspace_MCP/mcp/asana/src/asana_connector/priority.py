"""Task importance ranking: Asana Priority custom field + due-date tiers."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

_PRIORITY_LABELS = {
    "high": 0,
    "medium": 1,
    "low": 2,
}


def _parse_due_on(task: dict[str, Any]) -> date | None:
    due = task.get("due_on")
    if not due:
        return None
    try:
        return date.fromisoformat(str(due)[:10])
    except ValueError:
        return None


def priority_label(task: dict[str, Any]) -> str | None:
    """Return the Priority custom field display value, if any."""
    for field in task.get("custom_fields") or []:
        name = (field.get("name") or "").strip().lower()
        if name == "priority":
            enum_val = (field.get("enum_value") or {}).get("name")
            display = field.get("display_value")
            return enum_val or display
    return None


def priority_rank(task: dict[str, Any]) -> int:
    """Lower is more important. Missing Priority field ranks last."""
    label = priority_label(task)
    if not label:
        return 9
    return _PRIORITY_LABELS.get(str(label).strip().lower(), 5)


def due_rank(task: dict[str, Any], today: date | None = None) -> int:
    """Lower is more urgent. Overdue=0, today=1, this week=2, later=3, none=4."""
    today = today or date.today()
    due = _parse_due_on(task)
    if due is None:
        return 4
    if due < today:
        return 0
    if due == today:
        return 1
    if due <= today + timedelta(days=7):
        return 2
    return 3


def sort_tasks_by_importance(
    tasks: list[dict[str, Any]],
    today: date | None = None,
) -> list[dict[str, Any]]:
    """Sort tasks: Priority field first, due-date tier second, name third."""
    today = today or date.today()

    def sort_key(task: dict[str, Any]) -> tuple[int, int, str]:
        name = (task.get("name") or "").lower()
        return (priority_rank(task), due_rank(task, today), name)

    return sorted(tasks, key=sort_key)


def format_priority_badge(task: dict[str, Any]) -> str:
    label = priority_label(task)
    return f"[{label}]" if label else "[—]"
