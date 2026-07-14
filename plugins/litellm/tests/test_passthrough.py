"""Passthrough host restriction tests (mocked HTTP)."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))

import litellm_mcp as m  # noqa: E402


def test_passthrough_refuses_other_host():
    with patch.object(
        m,
        "_client_params",
        return_value=(
            "https://llm.example.com",
            "sk-abcxyz1234",
            "m",
            False,
            {},
        ),
    ):
        out = m.llm_request("GET", "https://evil.example.com/v1/models")
    assert out["ok"] is False
    assert "refused" in out["error"].lower()


def test_passthrough_same_host_ok():
    fake_resp = MagicMock()
    fake_resp.is_success = True
    fake_resp.status_code = 200
    fake_resp.text = '{"ok":true}'
    fake_resp.json.return_value = {"ok": True}

    fake_client = MagicMock()
    fake_client.__enter__.return_value = fake_client
    fake_client.request.return_value = fake_resp

    with patch.object(
        m,
        "_client_params",
        return_value=(
            "https://llm.example.com",
            "sk-abcxyz1234",
            "m",
            False,
            {},
        ),
    ), patch("httpx.Client", return_value=fake_client):
        out = m.llm_request("GET", "/health")
    assert out["ok"] is True
