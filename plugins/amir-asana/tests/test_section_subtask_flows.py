"""Server flow tests for section placement and subtask creation."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from asana_connector.server import (  # noqa: E402
    _resolve_section,
    add_task_to_section,
    create_subtask,
    create_task,
)


@pytest.fixture(autouse=True)
def reset_client():
    import asana_connector.server as srv

    srv._client = None
    yield
    srv._client = None


def test_resolve_section_by_name():
    mock_client = MagicMock()
    mock_client.list_sections.return_value = [
        {"gid": "s1", "name": "Prisma SDWAN S&O"},
        {"gid": "s2", "name": "Other"},
    ]
    with patch("asana_connector.server.client", return_value=mock_client):
        gid = _resolve_section("p1", section_name="Prisma SDWAN S&O")
    assert gid == "s1"


def test_create_task_places_in_section():
    mock_client = MagicMock()
    mock_client.post.return_value = {
        "gid": "t1",
        "name": "New task",
        "permalink_url": "https://app.asana.com/0/t1",
    }
    mock_client.list_sections.return_value = [
        {"gid": "s1", "name": "Backlog"},
    ]
    with patch("asana_connector.server.client", return_value=mock_client):
        result = create_task(
            name="New task",
            project_gid="p1",
            section_name="Backlog",
        )
    mock_client.add_task_to_section.assert_called_once_with("t1", "s1")
    assert "Placed in section" in result
    assert "t1" in result


def test_create_task_as_subtask():
    mock_client = MagicMock()
    mock_client.create_subtask.return_value = {
        "gid": "sub1",
        "name": "Checklist item",
        "permalink_url": "https://app.asana.com/0/sub1",
    }
    with patch("asana_connector.server.client", return_value=mock_client):
        result = create_task(
            name="Checklist item",
            parent_task_gid="parent1",
        )
    mock_client.create_subtask.assert_called_once()
    assert "subtask" in result.lower()
    assert "sub1" in result


def test_create_subtask_tool():
    mock_client = MagicMock()
    mock_client.create_subtask.return_value = {
        "gid": "sub2",
        "name": "Step 1",
        "permalink_url": "https://app.asana.com/0/sub2",
    }
    with patch("asana_connector.server.client", return_value=mock_client):
        result = create_subtask(parent_task_gid="p1", name="Step 1")
    assert "sub2" in result
    assert "Step 1" in result


def test_add_task_to_section_tool():
    mock_client = MagicMock()
    with patch("asana_connector.server.client", return_value=mock_client):
        result = add_task_to_section(task_gid="t1", section_gid="s1")
    mock_client.add_task_to_section.assert_called_once_with("t1", "s1")
    assert "Moved task" in result
