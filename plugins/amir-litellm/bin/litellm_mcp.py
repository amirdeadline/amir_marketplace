#!/usr/bin/env python3
"""
LiteLLM proxy MCP server — OpenAI-compatible core tools + generic passthrough.

Credentials only from LiteLLM_* env at invocation time. Keys masked in errors.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from litellm_contract import load_contract, mask_key, strip_secrets  # noqa: E402

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # Fallback message for missing deps when Claude starts the server
    print(
        "litellm MCP requires mcp package. pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise

mcp = FastMCP("litellm")


def _client_params() -> tuple[str, str, str | None, bool, dict[str, str]]:
    c = load_contract()
    if not c.ok:
        raise RuntimeError("; ".join(c.errors))
    return c.base_url, c.api_key, c.model, c.proxy_enabled, c.mapped_env


def _proxy_url(mapped: dict[str, str], enabled: bool) -> str | None:
    if not enabled:
        return None
    return mapped.get("ALL_PROXY") or mapped.get("HTTPS_PROXY") or mapped.get("HTTP_PROXY")


def _http(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    import httpx

    base, key, _model, proxy_enabled, mapped = _client_params()
    parsed_base = urlparse(base)
    # path may be absolute under base only
    if path.startswith("http://") or path.startswith("https://"):
        p = urlparse(path)
        if p.netloc != parsed_base.netloc:
            return {
                "ok": False,
                "error": f"passthrough refused: host {p.netloc!r} != configured base host {parsed_base.netloc!r}",
            }
        url = path
    else:
        url = urljoin(base.rstrip("/") + "/", path.lstrip("/"))
        p = urlparse(url)
        if p.netloc != parsed_base.netloc:
            return {
                "ok": False,
                "error": "passthrough refused: resolved URL left configured host",
            }

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    proxy = _proxy_url(mapped, proxy_enabled)
    try:
        with httpx.Client(timeout=120.0, proxy=proxy, trust_env=False) as client:
            resp = client.request(method.upper(), url, headers=headers, json=body, params=params)
    except Exception as e:
        return {"ok": False, "error": str(e), "url": url, "auth": mask_key(key)}

    text = resp.text
    try:
        data: Any = resp.json()
    except Exception:
        data = text[:4000]

    # Mask secrets in payload
    data = strip_secrets(data)
    if not resp.is_success:
        return {
            "ok": False,
            "status": resp.status_code,
            "error": data if isinstance(data, (dict, list, str)) else str(data),
            "url": url,
        }
    return {"ok": True, "status": resp.status_code, "data": data, "url": url}


@mcp.tool()
def llm_chat(
    messages: list[dict[str, Any]],
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    stream: bool = False,
) -> dict[str, Any]:
    """Chat completions via POST /v1/chat/completions (OpenAI-compatible)."""
    if stream:
        return {"ok": False, "error": "stream=true not supported over MCP; use stream=false"}
    _, _, default_model, _, _ = _client_params()
    body: dict[str, Any] = {
        "model": model or default_model or "gpt-4o-mini",
        "messages": messages,
        "stream": False,
    }
    if temperature is not None:
        body["temperature"] = temperature
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    return _http("POST", "/v1/chat/completions", body=body)


@mcp.tool()
def llm_complete(
    prompt: str,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    """Legacy completions via POST /v1/completions."""
    _, _, default_model, _, _ = _client_params()
    body: dict[str, Any] = {
        "model": model or default_model or "gpt-4o-mini",
        "prompt": prompt,
    }
    if temperature is not None:
        body["temperature"] = temperature
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    return _http("POST", "/v1/completions", body=body)


@mcp.tool()
def llm_embeddings(input: str | list[str], model: str | None = None) -> dict[str, Any]:
    """Embeddings via POST /v1/embeddings."""
    _, _, default_model, _, _ = _client_params()
    body = {
        "model": model or default_model or "text-embedding-3-small",
        "input": input,
    }
    return _http("POST", "/v1/embeddings", body=body)


@mcp.tool()
def llm_models() -> dict[str, Any]:
    """List models via GET /v1/models."""
    return _http("GET", "/v1/models")


@mcp.tool()
def llm_health() -> dict[str, Any]:
    """Proxy health via GET /health (VERIFIED: docs.litellm.ai/docs/proxy/health)."""
    return _http("GET", "/health")


@mcp.tool()
def llm_key_info(key: str | None = None) -> dict[str, Any]:
    """
    Key info / spend via GET /key/info (VERIFIED: docs.litellm.ai virtual keys).
    If key omitted, calls /key/info without query (proxy may infer from bearer).
    Forbidden errors returned masked from proxy.
    """
    params = {"key": key} if key else None
    return _http("GET", "/key/info", params=params)


@mcp.tool()
def llm_spend(filters: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Spend listing via GET /spend/keys (VERIFIED: docs.litellm.ai cost tracking).
    Optional filters passed as query params. Permission errors returned from proxy.
    """
    return _http("GET", "/spend/keys", params=filters or None)


@mcp.tool()
def llm_request(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generic passthrough to the configured LiteLLM base URL host only.
    Use for image/moderation/rerank/batch/audio/admin routes your key allows.
    Refuses absolute URLs on other hosts.
    """
    method_u = method.upper().strip()
    if method_u not in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"}:
        return {"ok": False, "error": f"unsupported method {method}"}
    return _http(method_u, path, body=body)


if __name__ == "__main__":
    mcp.run(transport="stdio")
