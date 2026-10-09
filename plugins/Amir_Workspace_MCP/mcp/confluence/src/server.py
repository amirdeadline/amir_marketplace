from __future__ import annotations

import re
import sys
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.fastmcp import FastMCP

from client import ConfluenceClient, ConfluenceError
from config import MissingConfigError

mcp = FastMCP("Palo Confluence (personal token)")
_client: ConfluenceClient | None = None


def client() -> ConfluenceClient:
    global _client
    if _client is None:
        _client = ConfluenceClient()
    return _client


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    text = unescape(re.sub(r"\s+", " ", text)).strip()
    return text


def _page_line(item: dict) -> str:
    title = (item.get("title") or "(untitled)").strip()
    pid = item.get("id", "?")
    space = ((item.get("space") or {}).get("key") or "?") if isinstance(item.get("space"), dict) else "?"
    return f"- `{pid}` **{title}** (space: {space})"


@mcp.tool()
def confluence_search(query: str, limit: int = 20, use_cql: bool = False) -> str:
    """Search Confluence. Plain query uses siteSearch CQL; set use_cql=true for full CQL."""
    try:
        cql = query if use_cql else f'siteSearch ~ "{query.replace(chr(34), "")}"'
        rows = client().search_cql(cql, limit=limit)
        if not rows:
            return "No results."
        return f"Found {len(rows)} hit(s):\n" + "\n".join(_page_line(r) for r in rows)
    except MissingConfigError as e:
        return f"⚠️ {e}"
    except ConfluenceError as e:
        return f"⚠️ {e}"


@mcp.tool()
def confluence_get_page(page_id: str, include_body: bool = True) -> str:
    """Fetch a page by numeric id."""
    try:
        page = client().get_page(page_id)
        title = page.get("title") or "(untitled)"
        space = ((page.get("space") or {}).get("key") or "?") if isinstance(page.get("space"), dict) else "?"
        ver = ((page.get("version") or {}).get("number")) if isinstance(page.get("version"), dict) else "?"
        lines = [f"# {title}", f"space: {space} · id: {page_id} · version: {ver}"]
        if include_body:
            body = ((page.get("body") or {}).get("storage") or {}).get("value") or ""
            lines.append("\n" + _strip_html(body)[:12000])
        return "\n".join(lines)
    except MissingConfigError as e:
        return f"⚠️ {e}"
    except ConfluenceError as e:
        return f"⚠️ {e}"


@mcp.tool()
def confluence_get_page_children(parent_id: str, limit: int = 25) -> str:
    """List child pages under a parent page id."""
    try:
        data = client().get_children(parent_id, limit=limit)
        rows = list(data.get("results") or [])
        if not rows:
            return "No child pages."
        return "\n".join(_page_line(r) for r in rows)
    except MissingConfigError as e:
        return f"⚠️ {e}"
    except ConfluenceError as e:
        return f"⚠️ {e}"


@mcp.tool()
def confluence_get_comments(page_id: str, limit: int = 20) -> str:
    """List comments on a page (best-effort via CQL)."""
    try:
        rows = client().get_comments(page_id, limit=limit)
        if not rows:
            return "No comments found."
        out = []
        for c in rows:
            title = c.get("title") or "comment"
            out.append(f"- `{c.get('id', '?')}` {title}")
        return "\n".join(out)
    except MissingConfigError as e:
        return f"⚠️ {e}"
    except ConfluenceError as e:
        return f"⚠️ {e}"


if __name__ == "__main__":
    mcp.run()
