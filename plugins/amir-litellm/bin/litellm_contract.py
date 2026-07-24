#!/usr/bin/env python3
"""LiteLLM_* environment contract → session-scoped mapped env (no persistence)."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

PREFIX = "LiteLLM_"

REQUIRED = (
    "LiteLLM_ANTHROPIC_BASE_URL",
    "LiteLLM_ANTHROPIC_API_KEY",
)

OPTIONAL_PASSTHROUGH = (
    "LiteLLM_ANTHROPIC_MODEL",
    "LiteLLM_CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS",
    "LiteLLM_NODE_USE_SYSTEM_CA",
)

PROXY_VARS = (
    "LiteLLM_ALL_PROXY",
    "LiteLLM_HTTPS_PROXY",
    "LiteLLM_HTTP_PROXY",
)


def mask_key(value: str | None) -> str:
    if not value:
        return "(missing)"
    if len(value) <= 4:
        return "sk-****"
    return f"sk-****{value[-4:]}"


def strip_secrets(obj: Any) -> Any:
    """Recursively mask key-like strings in structures for safe logging."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            lk = str(k).lower()
            if any(x in lk for x in ("key", "token", "authorization", "secret", "password")):
                out[k] = mask_key(str(v)) if v is not None else v
            else:
                out[k] = strip_secrets(v)
        return out
    if isinstance(obj, list):
        return [strip_secrets(x) for x in obj]
    if isinstance(obj, str) and re.search(r"\bsk-[A-Za-z0-9_\-]{8,}\b", obj):
        return re.sub(r"\bsk-[A-Za-z0-9_\-]{4,}([A-Za-z0-9_\-]{4})\b", r"sk-****\1", obj)
    return obj


@dataclass
class ContractResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    mapped_env: dict[str, str] = field(default_factory=dict)
    base_url: str = ""
    api_key: str = ""
    model: str | None = None
    proxy_enabled: bool = False
    summary: dict[str, Any] = field(default_factory=dict)


def _truthy(val: str | None) -> bool:
    return (val or "").strip() in {"1", "true", "TRUE", "yes", "YES", "on", "ON"}


def load_contract(environ: dict[str, str] | None = None) -> ContractResult:
    """
    Read LiteLLM_* vars and map to unprefixed session env.

    VERIFIED (docs.litellm.ai): Claude Code static key uses ANTHROPIC_AUTH_TOKEN;
    some tutorials also set ANTHROPIC_API_KEY. We set BOTH to the same value for
    compatibility; AUTH_TOKEN is the Claude Code–documented form.
    """
    env = environ if environ is not None else os.environ
    errors: list[str] = []
    warnings: list[str] = []

    for name in REQUIRED:
        if not (env.get(name) or "").strip():
            errors.append(f"missing required env var: {name}")

    base = (env.get("LiteLLM_ANTHROPIC_BASE_URL") or "").strip().rstrip("/")
    key = (env.get("LiteLLM_ANTHROPIC_API_KEY") or "").strip()
    model = (env.get("LiteLLM_ANTHROPIC_MODEL") or "").strip() or None

    if base:
        parsed = urlparse(base)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            errors.append("LiteLLM_ANTHROPIC_BASE_URL is not a well-formed http(s) URL")

    mapped: dict[str, str] = {}
    if base and key and not errors:
        mapped["ANTHROPIC_BASE_URL"] = base
        # Primary for Claude Code + LiteLLM (docs.litellm.ai tutorials/claude_responses_api)
        mapped["ANTHROPIC_AUTH_TOKEN"] = key
        # Compatibility with tutorials that use ANTHROPIC_API_KEY
        mapped["ANTHROPIC_API_KEY"] = key
        if model:
            mapped["ANTHROPIC_MODEL"] = model

        for src in OPTIONAL_PASSTHROUGH:
            if src == "LiteLLM_ANTHROPIC_MODEL":
                continue
            val = (env.get(src) or "").strip()
            if val:
                mapped[src.removeprefix(PREFIX)] = val

        proxy_enabled = _truthy(env.get("LiteLLM_PROXY_enabled"))
        if proxy_enabled:
            for src in PROXY_VARS:
                val = (env.get(src) or "").strip()
                if val:
                    mapped[src.removeprefix(PREFIX)] = val
            if not any(mapped.get(k) for k in ("ALL_PROXY", "HTTPS_PROXY", "HTTP_PROXY")):
                warnings.append(
                    "LiteLLM_PROXY_enabled=1 but no LiteLLM_ALL_PROXY / HTTPS_PROXY / HTTP_PROXY set"
                )
    else:
        proxy_enabled = False

    # Ensure LiteLLM_ originals are NOT in mapped session env
    for k in list(mapped):
        if k.startswith(PREFIX):
            del mapped[k]
            errors.append(f"internal error: refused to map {PREFIX}* into session")

    summary = {
        "ANTHROPIC_BASE_URL": base or "(missing)",
        "ANTHROPIC_AUTH_TOKEN": mask_key(key),
        "ANTHROPIC_API_KEY": mask_key(key),
        "ANTHROPIC_MODEL": model or "(unset)",
        "PROXY_enabled": proxy_enabled,
        "ALL_PROXY": mapped.get("ALL_PROXY", "(ignored)") if proxy_enabled else "(disabled)",
    }

    return ContractResult(
        ok=not errors,
        errors=errors,
        warnings=warnings,
        mapped_env=mapped,
        base_url=base,
        api_key=key,
        model=model,
        proxy_enabled=proxy_enabled,
        summary=summary,
    )


def build_session_environ(
    mapped: dict[str, str],
    base: dict[str, str] | None = None,
) -> dict[str, str]:
    """Merge mapped vars into a copy of the environment; strip LiteLLM_* keys."""
    out = dict(base if base is not None else os.environ)
    for k in list(out):
        if k.startswith(PREFIX):
            del out[k]
    out.update(mapped)
    return out
