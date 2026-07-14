"""MCP server tool registration and schema tests."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from asana_connector.server import mcp  # noqa: E402


def test_list_tools_count_and_schemas():
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert len(tools) == 17
    assert "list_priority_tasks_today" in names
    assert "list_my_tasks" in names
    assert "list_project_sections" in names
    assert "list_section_tasks" in names
    assert "add_task_to_section" in names
    assert "create_subtask" in names
    assert "list_tags" in names

    list_my = next(t for t in tools if t.name == "list_my_tasks")
    props = list_my.inputSchema.get("properties", {})
    assert "workspace_gid" in props
    assert "include_completed" in props
    assert "project_gid" in props
    assert "completed_since" in props
    assert "args" not in props
    assert "kwargs" not in props

    priority = next(t for t in tools if t.name == "list_priority_tasks_today")
    pprops = priority.inputSchema.get("properties", {})
    assert "workspace_gid" in pprops

    create = next(t for t in tools if t.name == "create_task")
    cprops = create.inputSchema.get("properties", {})
    assert "section_gid" in cprops
    assert "section_name" in cprops
    assert "parent_task_gid" in cprops

    subtask = next(t for t in tools if t.name == "create_subtask")
    assert "parent_task_gid" in subtask.inputSchema.get("properties", {})
    assert "tag_names" in subtask.inputSchema.get("properties", {})

    update = next(t for t in tools if t.name == "update_task")
    uprops = update.inputSchema.get("properties", {})
    assert "add_tag_names" in uprops
    assert "remove_tag_names" in uprops
