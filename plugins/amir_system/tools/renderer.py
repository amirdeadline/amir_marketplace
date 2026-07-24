"""Render per-project outputs from the manifest selection.

Claude Code: a subset marketplace build under .amir/generated/claude/marketplace/ containing only
the selected groups' files, or a fast-path marker when the full amir_project plugin is selected.
Cursor: flat .cursor/commands/amir_<name>.md files, .cursor/rules/amir_*.mdc, and a merge-preserving
.cursor/mcp.json where amir-owned entries carry the "//amir-generated" marker key.

Guarantees: idempotent (re-render is byte-identical), stale amir-generated files are removed,
user files are never touched, --dry-run prints the plan without writing anything.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from catalog import components_by_id, plugin_group_ids
from manifest import selected_project_group_ids
from util import (GENERATED_MARKER_KEY, dump_json, inject_generated_header,
                  is_amir_generated_text, read_json)

CLAUDE_GENERATED_RELPATH = Path(".amir") / "generated" / "claude"
FAST_PATH_MARKER = "FULL_PLUGIN_INSTALL.md"

_TEXT_SUFFIXES = {".md", ".mdc", ".py", ".ps1", ".sh", ".yaml", ".yml", ".toml", ".js",
                  ".mjs", ".cjs", ".ts", ".json", ".txt"}


@dataclass(frozen=True)
class Action:
    op: str  # create | update | keep | delete
    path: str  # project-relative posix path


class RenderPlan:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.desired: dict[str, bytes] = {}  # project-relative posix -> content
        self.notes: list[str] = []
        self.fast_path = False

    def add(self, relpath: Path | str, content: bytes | str) -> None:
        rel = Path(relpath).as_posix()
        self.desired[rel] = content.encode("utf-8") if isinstance(content, str) else content

    def actions(self) -> list[Action]:
        result = []
        for rel in sorted(self.desired):
            target = self.project_root / rel
            if not target.exists():
                result.append(Action("create", rel))
            elif target.read_bytes() != self.desired[rel]:
                result.append(Action("update", rel))
            else:
                result.append(Action("keep", rel))
        for rel in sorted(self._stale_files()):
            result.append(Action("delete", rel))
        return result

    def _owned_candidates(self) -> list[Path]:
        candidates: list[Path] = []
        generated = self.project_root / CLAUDE_GENERATED_RELPATH
        if generated.is_dir():
            candidates.extend(p for p in generated.rglob("*") if p.is_file())
        for pattern, folder in (("amir_*.md", "commands"), ("amir_*.mdc", "rules")):
            directory = self.project_root / ".cursor" / folder
            if directory.is_dir():
                candidates.extend(p for p in sorted(directory.glob(pattern))
                                  if is_amir_generated_text(p))
        return candidates

    def _stale_files(self) -> list[str]:
        stale = []
        for path in self._owned_candidates():
            rel = path.relative_to(self.project_root).as_posix()
            if rel not in self.desired:
                stale.append(rel)
        return stale


def _render_file_content(source: Path) -> bytes:
    raw = source.read_bytes()
    if source.suffix.lower() in _TEXT_SUFFIXES and source.suffix.lower() != ".json":
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw
        return inject_generated_header(text, source).encode("utf-8")
    return raw


def _find_command_file(plugin_root: Path, name: str) -> Path | None:
    commands_root = plugin_root / "commands"
    if not commands_root.is_dir():
        return None
    matches = sorted(commands_root.rglob(f"{name}.md"))
    return matches[0] if matches else None


def _mcp_server_definitions(catalog_root: Path) -> dict:
    """Collect MCP server definitions from both plugins' plugin.json / .mcp.json (defensive)."""
    definitions: dict[str, dict] = {}
    for plugin in ("amir_system", "amir_project"):
        plugin_root = catalog_root / "plugins" / plugin
        for candidate in (plugin_root / ".claude-plugin" / "plugin.json", plugin_root / ".mcp.json"):
            if not candidate.is_file():
                continue
            try:
                data = read_json(candidate)
            except Exception:  # malformed while under construction -- skip, never crash
                continue
            for name, config in (data.get("mcpServers") or {}).items():
                definitions.setdefault(name, config)
    return definitions


def _plan_claude(plan: RenderPlan, manifest_data: dict, catalog: dict, catalog_root: Path,
                 groups: list[str]) -> None:
    byid = components_by_id(catalog)
    project_id = ((manifest_data.get("project") or {}).get("id")) or "project"
    all_groups = plugin_group_ids(catalog, "amir_project")
    base = CLAUDE_GENERATED_RELPATH
    if set(groups) == set(all_groups):
        plan.fast_path = True
        plan.add(base / FAST_PATH_MARKER, inject_generated_header(
            "# Full amir_project selection\n\n"
            "All component groups are selected, so no subset build is rendered.\n"
            "Install the full plugin at project scope instead:\n\n"
            "    claude plugin install amir_project@amir-marketplace --scope project\n",
            Path(FAST_PATH_MARKER)))
        return

    market = base / "marketplace"
    plugin_root = catalog_root / "plugins" / "amir_project"
    plan.add(market / ".claude-plugin" / "marketplace.json", dump_json({
        "name": f"amir-project-{project_id}",
        "owner": {"name": "amir"},
        "metadata": {
            "description": f"Rendered amir_project subset for project '{project_id}'",
            GENERATED_MARKER_KEY: "generated by amirctl; do not edit; regenerate via /amir:repair_project",
        },
        "plugins": [{
            "name": "amir_project",
            "source": "./plugins/amir_project",
            "description": "Manifest-selected amir_project component subset: " + ", ".join(groups),
            "version": catalog.get("catalog_version", "1.0.0"),
        }],
    }))

    source_plugin_json = {}
    if (plugin_root / ".claude-plugin" / "plugin.json").is_file():
        try:
            source_plugin_json = read_json(plugin_root / ".claude-plugin" / "plugin.json")
        except Exception:
            plan.notes.append("source plugin.json for amir_project is unreadable; synthesizing one")
    selected_servers = sorted({server for gid in groups
                               for server in byid.get(gid, {}).get("mcp_servers", [])})
    definitions = _mcp_server_definitions(catalog_root)
    mcp_servers = {}
    for server in selected_servers:
        if server in definitions:
            mcp_servers[server] = definitions[server]
        else:
            plan.notes.append(f"mcp server definition '{server}' not found in source plugins; "
                              "skipped (source plugin may still be under construction)")
    plugin_json = {
        "name": "amir",
        "version": source_plugin_json.get("version", catalog.get("catalog_version", "1.0.0")),
        "description": source_plugin_json.get(
            "description", "amir project components (rendered subset)"),
        GENERATED_MARKER_KEY: "generated by amirctl; do not edit; regenerate via /amir:repair_project",
    }
    if mcp_servers:
        plugin_json["mcpServers"] = mcp_servers
    dest_plugin = market / "plugins" / "amir_project"
    plan.add(dest_plugin / ".claude-plugin" / "plugin.json", dump_json(plugin_json))

    for gid in groups:
        component = byid.get(gid, {})
        for command in component.get("commands", []):
            source = _find_command_file(plugin_root, command)
            if source is None:
                plan.notes.append(f"command file for '{command}' (group '{gid}') not found; skipped")
                continue
            rel = source.relative_to(plugin_root)
            plan.add(dest_plugin / rel, _render_file_content(source))
        for kind, names in (("skills", component.get("skills", [])), ("mcp", component.get("mcp_servers", []))):
            for name in names:
                directory = plugin_root / kind / name
                if not directory.is_dir():
                    continue
                for path in sorted(directory.rglob("*")):
                    if path.is_file() and "__pycache__" not in path.parts:
                        plan.add(dest_plugin / path.relative_to(plugin_root), _render_file_content(path))
        scripts = plugin_root / "scripts" / gid
        if scripts.is_dir():
            for path in sorted(scripts.rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts:
                    plan.add(dest_plugin / path.relative_to(plugin_root), _render_file_content(path))


def _plan_cursor(plan: RenderPlan, catalog: dict, catalog_root: Path, groups: list[str]) -> None:
    byid = components_by_id(catalog)
    project_plugin_root = catalog_root / "plugins" / "amir_project"
    for gid in groups:
        for command in byid.get(gid, {}).get("commands", []):
            source = _find_command_file(project_plugin_root, command)
            if source is None:
                plan.notes.append(f"cursor: command file for '{command}' (group '{gid}') not found; skipped")
                continue
            content = inject_generated_header(source.read_text(encoding="utf-8"), source)
            plan.add(Path(".cursor") / "commands" / f"amir_{command}.md", content)

    rules_root = catalog_root / "plugins" / "amir_system" / "rules"
    rule_files = sorted(rules_root.glob("*.mdc")) if rules_root.is_dir() else []
    if not rule_files:
        plan.notes.append("cursor: no system rules found at plugins/amir_system/rules/*.mdc yet; "
                          "re-run /amir:repair_project once they exist")
    for rule in rule_files:
        content = inject_generated_header(rule.read_text(encoding="utf-8"), rule)
        name = rule.stem if rule.stem.startswith("amir_") else f"amir_{rule.stem.replace('-', '_')}"
        plan.add(Path(".cursor") / "rules" / f"{name}.mdc", content)

    _plan_cursor_mcp(plan, catalog, catalog_root, groups)


def _plan_cursor_mcp(plan: RenderPlan, catalog: dict, catalog_root: Path, groups: list[str]) -> None:
    byid = components_by_id(catalog)
    selected_servers = sorted({server for gid in groups
                               for server in byid.get(gid, {}).get("mcp_servers", [])})
    mcp_path = plan.project_root / ".cursor" / "mcp.json"
    existing: dict = {}
    if mcp_path.is_file():
        try:
            existing = read_json(mcp_path)
        except Exception:
            plan.notes.append("cursor: existing .cursor/mcp.json is not valid JSON; "
                              "left untouched (fix it manually, then re-render)")
            return
    existing_servers = existing.get("mcpServers") or {}
    preserved = {name: config for name, config in existing_servers.items()
                 if not (isinstance(config, dict) and GENERATED_MARKER_KEY in config)}

    definitions = _mcp_server_definitions(catalog_root)
    amir_entries = {}
    for server in selected_servers:
        if server not in definitions:
            plan.notes.append(f"cursor: mcp server definition '{server}' not found in source plugins; skipped")
            continue
        config = dict(definitions[server])
        config[GENERATED_MARKER_KEY] = "generated by amirctl; do not edit; regenerate via /amir:repair_project"
        amir_entries[server] = config

    had_amir_entries = len(preserved) != len(existing_servers)
    if not amir_entries and not had_amir_entries and not mcp_path.is_file():
        return  # nothing to add and nothing to clean up -- do not create an empty file
    if not amir_entries and not had_amir_entries and mcp_path.is_file():
        return  # user-only file; never touch it
    merged = dict(existing)
    merged["mcpServers"] = {**preserved, **amir_entries}
    plan.add(Path(".cursor") / "mcp.json", dump_json(merged))


def render_plan(project_root: Path, manifest_data: dict, catalog: dict,
                catalog_root: Path) -> RenderPlan:
    plan = RenderPlan(project_root)
    catalog_root = Path(catalog_root)
    hosts = manifest_data.get("hosts") or {}
    groups = selected_project_group_ids(manifest_data, catalog)
    amir_project = ((manifest_data.get("plugins") or {}).get("amir_project") or {})

    if (hosts.get("claude_code") or {}).get("enabled") and amir_project.get("enabled") and groups:
        _plan_claude(plan, manifest_data, catalog, catalog_root, groups)
    if (hosts.get("cursor") or {}).get("enabled"):
        _plan_cursor(plan, catalog, catalog_root, groups)
    return plan


def apply_plan(plan: RenderPlan) -> list[Action]:
    actions = plan.actions()
    for action in actions:
        target = plan.project_root / action.path
        if action.op in ("create", "update"):
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(plan.desired[action.path])
        elif action.op == "delete":
            target.unlink(missing_ok=True)
    _prune_empty_dirs(plan.project_root / CLAUDE_GENERATED_RELPATH)
    for sub in ("commands", "rules"):
        _prune_empty_dirs(plan.project_root / ".cursor" / sub)
    return actions


def _prune_empty_dirs(root: Path) -> None:
    if not root.is_dir():
        return
    for directory in sorted((p for p in root.rglob("*") if p.is_dir()),
                            key=lambda p: len(p.parts), reverse=True):
        try:
            directory.rmdir()  # only succeeds when empty
        except OSError:
            pass


def render(project_root: Path, manifest_data: dict, catalog: dict, catalog_root: Path,
           dry_run: bool = False) -> tuple[RenderPlan, list[Action]]:
    plan = render_plan(project_root, manifest_data, catalog, catalog_root)
    actions = plan.actions() if dry_run else apply_plan(plan)
    return plan, actions


def format_plan(plan: RenderPlan, actions: list[Action], dry_run: bool) -> str:
    lines = [f"render plan for {plan.project_root}" + (" (dry-run)" if dry_run else "")]
    if plan.fast_path:
        lines.append("fast path: full selection -> use "
                     "'claude plugin install amir_project@amir-marketplace --scope project'")
    for op in ("create", "update", "delete", "keep"):
        subset = [a for a in actions if a.op == op]
        lines.append(f"{op}: {len(subset)}")
        for action in subset if op != "keep" else []:
            lines.append(f"  {op:6} {action.path}")
    for note in plan.notes:
        lines.append(f"note: {note}")
    return "\n".join(lines)


def _json_default(obj):
    if isinstance(obj, Action):
        return {"op": obj.op, "path": obj.path}
    raise TypeError(str(type(obj)))


def plan_to_json(plan: RenderPlan, actions: list[Action]) -> str:
    return json.dumps({"fast_path": plan.fast_path, "notes": plan.notes,
                       "actions": actions}, indent=2, default=_json_default) + "\n"
