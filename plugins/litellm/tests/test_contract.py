"""Unit tests for LiteLLM env contract — no real network."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))

from litellm_contract import (  # noqa: E402
    build_session_environ,
    load_contract,
    mask_key,
    strip_secrets,
)


def test_mask_key():
    assert mask_key("sk-abcdefghij1234") == "sk-****1234"
    assert "abcdefgh" not in mask_key("sk-abcdefghij1234")


def test_missing_required():
    r = load_contract({})
    assert not r.ok
    assert any("LiteLLM_ANTHROPIC_BASE_URL" in e for e in r.errors)
    assert any("LiteLLM_ANTHROPIC_API_KEY" in e for e in r.errors)


def test_maps_auth_token_and_api_key():
    env = {
        "LiteLLM_ANTHROPIC_BASE_URL": "https://llm.example.com",
        "LiteLLM_ANTHROPIC_API_KEY": "sk-testkeyVALUE99",
        "LiteLLM_ANTHROPIC_MODEL": "claude-sonnet",
    }
    r = load_contract(env)
    assert r.ok
    assert r.mapped_env["ANTHROPIC_BASE_URL"] == "https://llm.example.com"
    assert r.mapped_env["ANTHROPIC_AUTH_TOKEN"] == "sk-testkeyVALUE99"
    assert r.mapped_env["ANTHROPIC_API_KEY"] == "sk-testkeyVALUE99"
    assert r.mapped_env["ANTHROPIC_MODEL"] == "claude-sonnet"
    assert not any(k.startswith("LiteLLM_") for k in r.mapped_env)
    assert r.summary["ANTHROPIC_AUTH_TOKEN"] == "sk-****UE99"
    assert "VALUE99" not in r.summary["ANTHROPIC_AUTH_TOKEN"] or r.summary[
        "ANTHROPIC_AUTH_TOKEN"
    ].startswith("sk-****")


def test_proxy_disabled_ignores_proxy_vars():
    env = {
        "LiteLLM_ANTHROPIC_BASE_URL": "https://llm.example.com",
        "LiteLLM_ANTHROPIC_API_KEY": "sk-abcxyz1234",
        "LiteLLM_PROXY_enabled": "0",
        "LiteLLM_ALL_PROXY": "socks5h://127.0.0.1:1080",
    }
    r = load_contract(env)
    assert r.ok
    assert "ALL_PROXY" not in r.mapped_env
    assert r.proxy_enabled is False


def test_proxy_enabled_maps_socks():
    env = {
        "LiteLLM_ANTHROPIC_BASE_URL": "https://llm.example.com",
        "LiteLLM_ANTHROPIC_API_KEY": "sk-abcxyz1234",
        "LiteLLM_PROXY_enabled": "1",
        "LiteLLM_ALL_PROXY": "socks5h://127.0.0.1:1080",
    }
    r = load_contract(env)
    assert r.ok
    assert r.mapped_env["ALL_PROXY"] == "socks5h://127.0.0.1:1080"


def test_session_env_strips_litellm_prefix():
    mapped = {
        "ANTHROPIC_BASE_URL": "https://llm.example.com",
        "ANTHROPIC_AUTH_TOKEN": "sk-abcxyz1234",
        "ANTHROPIC_API_KEY": "sk-abcxyz1234",
    }
    base = {"PATH": "C:\\Windows", "LiteLLM_ANTHROPIC_API_KEY": "sk-SHOULD-GO"}
    out = build_session_environ(mapped, base)
    assert "LiteLLM_ANTHROPIC_API_KEY" not in out
    assert out["ANTHROPIC_AUTH_TOKEN"] == "sk-abcxyz1234"


def test_strip_secrets_grep_safe():
    payload = {"token": "sk-supersecretKEY99", "nested": {"authorization": "Bearer sk-zzzzYYYY"}}
    cleaned = strip_secrets(payload)
    blob = str(cleaned)
    assert "supersecret" not in blob
    assert re.search(r"sk-\*\*\*\*", blob)
