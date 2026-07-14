"""Tests for asana_tasks.md parser."""

from pathlib import Path

from asana_connector.asana_tasks_md import load_and_parse, parse_asana_tasks_md

SAMPLE = """\
# Backlog

| Field | Value |
|-------|-------|
| **Asana project** | Test Project |
| **Asana section** | Sprint A |

### Main task: Alpha

**Phase target:** 2026-06-04 · **Phase status:** In progress

| Subtask | Due | Status | Notes |
|---------|-----|--------|-------|
| First item | 2026-06-05 | Done | note a |
| Second item | 2026-06-06 | Open | |

**Comments**

- **2026-06-04** `[tag]` — Alpha comment one.

---

### Main task: Beta

**Phase target:** 2026-06-10 · **Phase status:** Not started

| Subtask | Due | Status | Notes |
|---------|-----|--------|-------|
| Beta task | 2026-06-12 | In progress | |

**Comments**

- **2026-06-04** — Simple comment.
"""


def test_parse_metadata_and_main_tasks():
    plan = parse_asana_tasks_md(SAMPLE)
    assert plan.metadata.project_name == "Test Project"
    assert plan.metadata.section_name == "Sprint A"
    assert len(plan.main_tasks) == 2

    alpha = plan.main_tasks[0]
    assert alpha.title == "Alpha"
    assert alpha.phase_target == "2026-06-04"
    assert alpha.phase_status == "In progress"
    assert len(alpha.subtasks) == 2
    assert alpha.subtasks[0].name == "First item"
    assert alpha.subtasks[0].status == "Done"
    assert alpha.subtasks[1].status == "Open"
    assert len(alpha.comments) == 1

    beta = plan.main_tasks[1]
    assert beta.title == "Beta"
    assert beta.subtasks[0].status == "In progress"


def test_load_and_parse_file(tmp_path: Path):
    p = tmp_path / "asana_tasks.md"
    p.write_text(SAMPLE, encoding="utf-8")
    plan = load_and_parse(p)
    assert plan.source_path == p
    assert plan.metadata.project_name == "Test Project"
