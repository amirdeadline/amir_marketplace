#!/usr/bin/env python3
"""
Rebrand all amir_marketplace plugins so slash commands/skills show under /amir…

Claude Code / Cursor plugin namespace = plugin.json `name`.
We rename every plugin (except already-prefixed) to amir-<name>, and rewrite
command titles/frontmatter to `/amir-<plugin>:<cmd>` (or `/amir:<cmd>` for the
core harness). Skill frontmatter names get an `amir-` prefix for searchability.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
SOURCES = ROOT.parent  # E:\PC3_Shared\Plugins

# packed dir name -> new plugin name (and preferred source dir name)
RENAMES: dict[str, str] = {
    "prisma": "amir-prisma",
    "litellm": "amir-litellm",
    "paloalto": "amir-paloalto",
    "aws": "amir-aws",
    "azure": "amir-azure",
    "terraform": "amir-terraform",
    "docker": "amir-docker",
    "splunk": "amir-splunk",
    "elastic": "amir-elastic",
    "sentinel": "amir-sentinel",
    "qradar": "amir-qradar",
    "cortex-xdr": "amir-cortex-xdr",
    "ssh-terminal": "amir-ssh",
    "nmap": "amir-nmap",
    "wireshark": "amir-wireshark",
    # already good: amir, amir-asana
}


def rewrite_command_md(path: Path, plugin_name: str) -> None:
    text = path.read_text(encoding="utf-8")
    stem = path.stem  # whoami, plan, …
    slash = f"/{plugin_name}:{stem}"
    # frontmatter name
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end]
            body = text[end + 4 :]
            if re.search(r"(?m)^name:\s*", fm):
                fm = re.sub(r"(?m)^name:\s*.*$", f"name: {plugin_name}:{stem}", fm, count=1)
            else:
                fm = f"name: {plugin_name}:{stem}\n" + fm.lstrip("\n")
            text = f"---{fm}\n---{body}"
    # H1
    text = re.sub(r"(?m)^#\s+/?.+$", f"# {slash}", text, count=1)
    # replace old /plugin: refs lightly
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def rewrite_skill_md(path: Path, plugin_name: str) -> None:
    text = path.read_text(encoding="utf-8")
    # skill dir name
    skill_id = path.parent.name
    new_name = skill_id if skill_id.startswith("amir-") else f"amir-{skill_id}"
    # For core amir plugin, keep short skill names but ensure description mentions amir marketplace
    if plugin_name == "amir":
        new_name = skill_id  # already under /amir: via plugin namespace for commands; skills keep ids
    elif plugin_name == "amir-asana":
        new_name = skill_id if skill_id.startswith("asana-") else f"amir-{skill_id}"
        if not new_name.startswith("amir-") and skill_id.startswith("asana-"):
            new_name = f"amir-{skill_id}"
    else:
        new_name = f"{plugin_name}-{skill_id}" if not skill_id.startswith(plugin_name) else skill_id

    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end]
            body = text[end + 4 :]
            if re.search(r"(?m)^name:\s*", fm):
                fm = re.sub(r"(?m)^name:\s*.*$", f"name: {new_name}", fm, count=1)
            else:
                fm = f"name: {new_name}\n" + fm.lstrip("\n")
            # Ensure description mentions marketplace origin
            if "amir marketplace" not in fm.lower() and "description:" in fm:
                fm = re.sub(
                    r"(?m)^(description:\s*>-\s*\n(?:\s+.+\n)+)",
                    lambda m: m.group(1).rstrip() + " (amir marketplace).\n",
                    fm,
                    count=1,
                )
            text = f"---{fm}\n---{body}"
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def update_manifests(plugin_dir: Path, new_name: str) -> None:
    for rel in [
        ".claude-plugin/plugin.json",
        ".cursor-plugin/plugin.json",
        ".codex-plugin/plugin.json",
    ]:
        p = plugin_dir / rel
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        data["name"] = new_name
        p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def rebrand_tree(plugin_dir: Path, new_name: str) -> None:
    update_manifests(plugin_dir, new_name)
    cmd_dir = plugin_dir / "commands"
    if cmd_dir.is_dir():
        for md in cmd_dir.glob("*.md"):
            rewrite_command_md(md, new_name)
    skills = plugin_dir / "skills"
    if skills.is_dir():
        for skill_md in skills.glob("*/SKILL.md"):
            rewrite_skill_md(skill_md, new_name)


def rename_dir(parent: Path, old: str, new: str) -> Path | None:
    src = parent / old
    dst = parent / new
    if not src.exists():
        return dst if dst.exists() else None
    if dst.exists() and src.resolve() != dst.resolve():
        shutil.rmtree(dst)
    src.rename(dst)
    return dst


def main() -> None:
    # 1) Rename packed plugins
    for old, new in RENAMES.items():
        path = rename_dir(PLUGINS, old, new)
        if path and path.exists():
            rebrand_tree(path, new)
            print(f"packed: {old} -> {new}")

    # 2) Core amir + amir-asana: only rebrand command titles to /amir:… and /amir-asana:…
    for name in ("amir", "amir-asana"):
        d = PLUGINS / name
        if d.exists():
            rebrand_tree(d, name)
            print(f"rebranded commands: {name}")

    # 3) Source trees beside marketplace (same renames)
    for old, new in RENAMES.items():
        path = rename_dir(SOURCES, old, new)
        if path and path.exists():
            rebrand_tree(path, new)
            print(f"source: {old} -> {new}")

    print("done — update catalogs next")


if __name__ == "__main__":
    main()
