"""Unit tests for AsanaClient — all HTTP is mocked with respx (no live calls)."""

import httpx
import pytest
import respx

from asana_connector.client import AsanaClient, AsanaError

BASE = "https://app.asana.com/api/1.0"


@respx.mock
def test_me_unwraps_data_envelope():
    respx.get(f"{BASE}/users/me").mock(
        return_value=httpx.Response(
            200, json={"data": {"gid": "1", "name": "Amir", "workspaces": []}}
        )
    )
    with AsanaClient(token="x") as c:
        me = c.me()
    assert me["name"] == "Amir"


@respx.mock
def test_get_all_follows_offset_pagination():
    respx.get(f"{BASE}/tasks").mock(
        side_effect=[
            httpx.Response(
                200,
                json={"data": [{"gid": "1"}], "next_page": {"offset": "abc"}},
            ),
            httpx.Response(200, json={"data": [{"gid": "2"}], "next_page": None}),
        ]
    )
    with AsanaClient(token="x") as c:
        items = c.get_all("/tasks")
    assert [i["gid"] for i in items] == ["1", "2"]


@respx.mock
def test_error_payload_is_unwrapped():
    respx.get(f"{BASE}/users/me").mock(
        return_value=httpx.Response(
            401, json={"errors": [{"message": "Not Authorized"}]}
        )
    )
    with AsanaClient(token="x") as c:
        with pytest.raises(AsanaError) as excinfo:
            c.me()
    assert excinfo.value.status == 401
    assert "Not Authorized" in excinfo.value.message


@respx.mock
def test_default_workspace_gid():
    respx.get(f"{BASE}/users/me").mock(
        return_value=httpx.Response(
            200,
            json={"data": {"gid": "1", "workspaces": [{"gid": "ws_9", "name": "W"}]}},
        )
    )
    with AsanaClient(token="x") as c:
        assert c.default_workspace_gid() == "ws_9"


@respx.mock
def test_list_sections():
    respx.get(f"{BASE}/projects/p1/sections").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {"gid": "s1", "name": "Backlog"},
                    {"gid": "s2", "name": "In Progress"},
                ],
                "next_page": None,
            },
        )
    )
    with AsanaClient(token="x") as c:
        sections = c.list_sections("p1")
    assert [s["gid"] for s in sections] == ["s1", "s2"]


@respx.mock
def test_add_task_to_section():
    route = respx.post(f"{BASE}/sections/s1/addTask").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    with AsanaClient(token="x") as c:
        c.add_task_to_section("t1", "s1")
    assert route.called
    body = route.calls.last.request.content.decode()
    assert "t1" in body


@respx.mock
def test_create_subtask():
    respx.post(f"{BASE}/tasks/parent1/subtasks").mock(
        return_value=httpx.Response(
            200,
            json={"data": {"gid": "sub1", "name": "Child", "permalink_url": "https://x"}},
        )
    )
    with AsanaClient(token="x") as c:
        task = c.create_subtask("parent1", {"name": "Child"})
    assert task["gid"] == "sub1"


@respx.mock
def test_list_tags():
    respx.get(f"{BASE}/workspaces/ws1/tags").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [{"gid": "tag1", "name": "blocked"}],
                "next_page": None,
            },
        )
    )
    with AsanaClient(token="x") as c:
        tags = c.list_tags("ws1")
    assert tags[0]["name"] == "blocked"


@respx.mock
def test_resolve_tag_gids_by_name():
    respx.get(f"{BASE}/workspaces/ws1/tags").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [{"gid": "tag1", "name": "Lab"}],
                "next_page": None,
            },
        )
    )
    with AsanaClient(token="x") as c:
        gids = c.resolve_tag_gids("ws1", tag_names=["lab"])
    assert gids == ["tag1"]


@respx.mock
def test_apply_task_tags():
    respx.get(f"{BASE}/workspaces/ws1/tags").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [{"gid": "tag1", "name": "sync"}],
                "next_page": None,
            },
        )
    )
    respx.get(f"{BASE}/tasks/t1").mock(
        return_value=httpx.Response(
            200, json={"data": {"gid": "t1", "tags": []}}
        )
    )
    add_route = respx.post(f"{BASE}/tasks/t1/addTag").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    with AsanaClient(token="x") as c:
        added, removed = c.apply_task_tags(
            "t1", "ws1", add_tag_names=["sync"]
        )
    assert added == ["tag1"]
    assert removed == []
    assert add_route.called
