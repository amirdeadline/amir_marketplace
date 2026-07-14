#!/usr/bin/env python3
"""
litellm-claude — launch Claude Code routed through the org LiteLLM proxy.

Session-scoped env only. Never writes settings files. Never prints full keys.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# Allow running as script from bin/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from litellm_contract import (  # noqa: E402
    build_session_environ,
    load_contract,
    mask_key,
    strip_secrets,
)


def diagnose_http_error(exc: BaseException, base_url: str, proxy_enabled: bool) -> str:
    msg = str(exc)
    tips = [f"preflight failed talking to {base_url}: {msg}"]
    low = msg.lower()
    if "getaddrinfo" in low or "name or service" in low or "nodename" in low:
        tips.append("diagnosis: DNS — host not resolvable (try socks5h:// if PROXY_enabled)")
    elif "connect" in low or "connection refused" in low or "10061" in low:
        tips.append("diagnosis: network/proxy — connection refused or unreachable")
    elif "certificate" in low or "ssl" in low or "tls" in low:
        tips.append(
            "diagnosis: TLS — set LiteLLM_NODE_USE_SYSTEM_CA=1 for corporate interception "
            "(Node) and ensure Python trusts the corporate CA"
        )
    elif "401" in low or "403" in low or "unauthorized" in low:
        tips.append("diagnosis: auth — check LiteLLM_ANTHROPIC_API_KEY permissions")
    elif proxy_enabled:
        tips.append("diagnosis: proxy path enabled — verify LiteLLM_ALL_PROXY socks5h:// URL")
    else:
        tips.append("diagnosis: unknown — check base URL path (no trailing /v1/messages required)")
    return "\n".join(tips)


def preflight_models(base_url: str, api_key: str, proxy_enabled: bool, mapped: dict[str, str]) -> dict[str, Any]:
    """
    GET {base}/v1/models with Bearer auth.
    VERIFIED: OpenAI-compatible LiteLLM proxy exposes /v1/models.
    """
    try:
        import httpx
    except ImportError as e:
        raise RuntimeError(
            "httpx not installed. pip install -r requirements.txt (include httpx[socks])"
        ) from e

    url = f"{base_url.rstrip('/')}/v1/models"
    proxies = None
    if proxy_enabled:
        # honor socks5h / http proxy from mapped env
        proxy_url = mapped.get("ALL_PROXY") or mapped.get("HTTPS_PROXY") or mapped.get("HTTP_PROXY")
        if proxy_url:
            proxies = proxy_url

    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    try:
        with httpx.Client(timeout=30.0, proxy=proxies, trust_env=False) as client:
            resp = client.get(url, headers=headers)
    except Exception as e:
        raise RuntimeError(diagnose_http_error(e, base_url, proxy_enabled)) from e

    if resp.status_code >= 400:
        raise RuntimeError(
            diagnose_http_error(
                RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}"),
                base_url,
                proxy_enabled,
            )
        )

    data = resp.json()
    models = []
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        for item in data["data"]:
            if isinstance(item, dict) and item.get("id"):
                models.append(item["id"])
    return {"raw": strip_secrets(data), "models": models, "url": url}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="litellm-claude",
        description="Launch Claude Code through LiteLLM (session-scoped env)",
    )
    ap.add_argument("--model", help="Override LiteLLM_ANTHROPIC_MODEL for this session")
    ap.add_argument("--dry-run", action="store_true", help="Validate + preflight only; do not launch")
    ap.add_argument("--json", action="store_true", help="Print masked status as JSON")
    ap.add_argument(
        "claude_args",
        nargs=argparse.REMAINDER,
        help="Args after -- passed to claude (include leading --)",
    )
    args = ap.parse_args(argv)

    contract = load_contract()
    if args.model:
        contract.model = args.model
        if contract.ok:
            contract.mapped_env["ANTHROPIC_MODEL"] = args.model
            contract.summary["ANTHROPIC_MODEL"] = args.model

    if not contract.ok:
        print("REFUSING TO LAUNCH — contract validation failed:", file=sys.stderr)
        for e in contract.errors:
            print(f"  - {e}", file=sys.stderr)
        return 2

    for w in contract.warnings:
        print(f"WARN: {w}", file=sys.stderr)

    try:
        pf = preflight_models(
            contract.base_url,
            contract.api_key,
            contract.proxy_enabled,
            contract.mapped_env,
        )
    except Exception as e:
        print(f"REFUSING TO LAUNCH — {e}", file=sys.stderr)
        return 3

    model_ok = True
    if contract.model and contract.model not in pf["models"]:
        model_ok = False
        print(
            f"WARN: configured model {contract.model!r} not in /v1/models "
            f"({len(pf['models'])} models returned). Launching anyway.",
            file=sys.stderr,
        )

    status = {
        "config": contract.summary,
        "preflight": {
            "models_url": pf["url"],
            "model_count": len(pf["models"]),
            "configured_model_present": model_ok if contract.model else None,
        },
        "session_env_keys": sorted(contract.mapped_env.keys()),
        "contains_LiteLLM_prefix": any(k.startswith("LiteLLM_") for k in contract.mapped_env),
    }

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print("LiteLLM → Claude session (masked):")
        for k, v in contract.summary.items():
            print(f"  {k}={v}")
        print(f"  models_available={len(pf['models'])}")
        print(f"  session_env={','.join(sorted(contract.mapped_env.keys()))}")

    if status["contains_LiteLLM_prefix"]:
        print("REFUSING TO LAUNCH — LiteLLM_ keys leaked into mapped env", file=sys.stderr)
        return 4

    if args.dry_run:
        return 0

    claude = shutil.which("claude")
    if not claude:
        print("REFUSING TO LAUNCH — `claude` not found on PATH", file=sys.stderr)
        return 5

    # Remainder may start with --
    extra = list(args.claude_args or [])
    if extra and extra[0] == "--":
        extra = extra[1:]

    session_env = build_session_environ(contract.mapped_env)
    # Double-check no LiteLLM_ in child env
    leaked = [k for k in session_env if k.startswith("LiteLLM_")]
    if leaked:
        print(f"REFUSING TO LAUNCH — leaked env keys: {leaked}", file=sys.stderr)
        return 4

    print(f"Launching: {claude} {' '.join(extra)}".rstrip())
    try:
        return subprocess.call([claude, *extra], env=session_env)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
