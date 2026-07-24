"""User-level project registry: %USERPROFILE%\\.amir\\registry\\projects.json (SPEC section 4.4).

Non-secret metadata only. Never scans the machine -- only registered roots are checked.
All mutations return new dicts (no in-place mutation of loaded state).
"""
from __future__ import annotations

from pathlib import Path

from util import AmirError, dump_json, read_json, utc_now_iso, write_text

REGISTRY_FIELDS = ("id", "name", "root", "type", "cursor_enabled", "claude_enabled",
                   "last_validation", "last_opened", "manifest_path", "enabled_component_ids")


def registry_path(home: Path | None = None) -> Path:
    return (Path(home) if home else Path.home()) / ".amir" / "registry" / "projects.json"


def load_registry(home: Path | None = None) -> dict:
    path = registry_path(home)
    if not path.is_file():
        return {"schema_version": 1, "projects": []}
    data = read_json(path)
    if not isinstance(data.get("projects"), list):
        raise AmirError(f"registry {path} is malformed: 'projects' must be a list")
    return data


def save_registry(registry: dict, home: Path | None = None) -> Path:
    path = registry_path(home)
    ordered = {
        "schema_version": registry.get("schema_version", 1),
        "projects": sorted(registry.get("projects", []), key=lambda p: p.get("id", "")),
    }
    write_text(path, dump_json(ordered))
    return path


def entry_from_manifest(manifest_data: dict, project_root: Path) -> dict:
    import manifest as manifest_mod  # noqa: PLC0415

    project = manifest_data.get("project") or {}
    hosts = manifest_data.get("hosts") or {}
    return {
        "id": project.get("id") or Path(project_root).name.lower(),
        "name": project.get("name") or Path(project_root).name,
        "root": str(Path(project_root).resolve()),
        "type": "onboarded" if project.get("onboarded") else "created",
        "cursor_enabled": bool((hosts.get("cursor") or {}).get("enabled")),
        "claude_enabled": bool((hosts.get("claude_code") or {}).get("enabled")),
        "last_validation": None,
        "last_opened": utc_now_iso(),
        "manifest_path": str(Path(project_root).resolve() / ".amir" / "project.yaml"),
        "enabled_component_ids": manifest_mod.selected_component_ids(manifest_data),
    }


def upsert_project(registry: dict, entry: dict) -> dict:
    others = [p for p in registry.get("projects", []) if p.get("id") != entry.get("id")]
    previous = next((p for p in registry.get("projects", []) if p.get("id") == entry.get("id")), None)
    merged = dict(entry)
    if previous and previous.get("last_validation") and not entry.get("last_validation"):
        merged["last_validation"] = previous["last_validation"]
    return {**registry, "projects": others + [merged]}


def remove_project(registry: dict, project_id: str) -> dict:
    remaining = [p for p in registry.get("projects", []) if p.get("id") != project_id]
    if len(remaining) == len(registry.get("projects", [])):
        raise AmirError(f"project '{project_id}' is not registered")
    return {**registry, "projects": remaining}


def inspect(registry: dict) -> list[dict]:
    """Per-entry health report (checks registered roots only; never scans the machine)."""
    report = []
    for entry in sorted(registry.get("projects", []), key=lambda p: p.get("id", "")):
        root = Path(entry.get("root", ""))
        manifest_file = Path(entry.get("manifest_path") or (root / ".amir" / "project.yaml"))
        if not root.is_dir():
            status = "missing-root"
        elif not manifest_file.is_file():
            status = "missing-manifest (project moved or config removed; re-register or prune)"
        else:
            status = "ok"
        report.append({**entry, "status": status})
    return report


def repair(registry: dict, prune: bool = False) -> tuple[dict, list[dict]]:
    """Report stale entries; with prune=True, drop entries whose root no longer exists."""
    report = inspect(registry)
    if not prune:
        return registry, report
    keep = [dict(entry) for entry in report if entry["status"] == "ok"]
    for entry in keep:
        entry.pop("status", None)
    return {**registry, "projects": keep}, report
