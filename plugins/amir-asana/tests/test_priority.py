"""Unit tests for task priority ranking."""

from datetime import date

from asana_connector.priority import sort_tasks_by_importance


def _task(name: str, due_on: str | None = None, priority: str | None = None) -> dict:
    custom_fields = []
    if priority:
        custom_fields.append(
            {
                "name": "Priority",
                "display_value": priority,
                "enum_value": {"name": priority},
            }
        )
    return {"name": name, "due_on": due_on, "custom_fields": custom_fields}


def test_high_overdue_beats_low_due_today():
    today = date(2026, 6, 2)
    tasks = [
        _task("Low today", due_on="2026-06-02", priority="Low"),
        _task("High overdue", due_on="2026-06-01", priority="High"),
    ]
    ranked = sort_tasks_by_importance(tasks, today=today)
    assert ranked[0]["name"] == "High overdue"


def test_priority_before_due_when_same_tier():
    today = date(2026, 6, 2)
    tasks = [
        _task("Medium", due_on="2026-06-02", priority="Medium"),
        _task("High", due_on="2026-06-02", priority="High"),
    ]
    ranked = sort_tasks_by_importance(tasks, today=today)
    assert ranked[0]["name"] == "High"


def test_no_priority_sorts_by_due():
    today = date(2026, 6, 2)
    tasks = [
        _task("Later", due_on="2026-06-10"),
        _task("Overdue", due_on="2026-06-01"),
    ]
    ranked = sort_tasks_by_importance(tasks, today=today)
    assert ranked[0]["name"] == "Overdue"
