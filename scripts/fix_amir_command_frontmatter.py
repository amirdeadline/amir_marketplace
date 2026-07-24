#!/usr/bin/env python3
"""Ensure packed amir commands have valid YAML frontmatter with quoted amir: names."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"E:\PC3_Shared\Plugins\amir_marketplace\plugins\amir\commands")


def extract_body(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return re.sub(r"(?m)^#\s+/?.+\n+", "", text, count=1).lstrip("\n")


def first_sentence(body: str) -> str:
    line = ""
    for raw in body.splitlines():
        s = raw.strip()
        if not s or s.startswith("#") or s.startswith("```"):
            continue
        if s.startswith("##"):
            continue
        line = s
        break
    line = line.replace('"', "'")
    if len(line) > 140:
        line = line[:137] + "..."
    return line or "amir command"


def main() -> None:
    for p in sorted(ROOT.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        stem = p.stem
        name = f"amir:{stem}"
        body = extract_body(text)
        # Keep a clean H1
        body = re.sub(r"(?m)^#\s+/?.+\n*", "", body, count=1).lstrip("\n")
        desc = first_sentence(body)
        out = (
            f"---\n"
            f'name: "{name}"\n'
            f'description: "{desc}"\n'
            f"---\n\n"
            f"# /{name}\n\n"
            f"{body}"
        )
        if not out.endswith("\n"):
            out += "\n"
        p.write_text(out, encoding="utf-8")
        print("fixed", p.name)

    # litellm mcp path fix if present
    mcp = Path(r"E:\PC3_Shared\Plugins\amir_marketplace\plugins\amir-litellm\mcp.json")
    if mcp.exists():
        t = mcp.read_text(encoding="utf-8")
        t = t.replace("/plugins/local/litellm/", "/plugins/local/amir-litellm/")
        mcp.write_text(t, encoding="utf-8")


if __name__ == "__main__":
    main()
