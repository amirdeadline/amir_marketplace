"""Unified user-level project registry: %USERPROFILE%\\.amir\\registry\\projects.yaml.

ONE registry for both classic registry-* commands and the portfolio-* graph commands.
Layout under %USERPROFILE%\\.amir\\registry\\:
  projects.yaml       the registry (YAML, schema_version 2)
  projects.lock.json  concurrency guard (exclusive-create; stale after 10 minutes)
  project-history\\    one timestamped YAML snapshot per mutation + archived removed entries

Rules:
  - Non-secret metadata only. Never scans the machine -- only registered roots are checked.
  - All mutations return new dicts (no in-place mutation of loaded state).
  - Unknown values stay null -- progress/lifecycle are NEVER fabricated.
  - Stable ids come from .amir/project.yaml project.id (never the folder name alone);
    duplicate ids across different roots are refused.
  - A legacy projects.json is migrated to YAML on first load (old file kept as
    projects.json.migrated).
"""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from util import (AmirError, acquire_lock_file, atomic_write_text, read_json,
                  release_lock_file, require_yaml, utc_stamp)

REGISTRY_SCHEMA_VERSION = 2
LOCK_STALE_SECONDS = 10 * 60
GIT_TIMEOUT_SECONDS = 15

REGISTRY_FIELDS = (
    "id", "name", "root", "manifest", "lifecycle", "priority", "health", "current_phase",
    "confirmed_progress", "estimated_progress", "last_status_update", "last_graph_update",
    "graph_source_commit", "graph_path", "graph_enabled", "cursor_enabled",
    "claude_code_enabled", "asana_reference",
)
LIFECYCLES = ("active", "paused", "archived")
PRIORITIES = ("high", "medium", "low")
HEALTH_STATES = ("healthy", "at-risk", "blocked", "unknown")

# Fields written by portfolio graph operations; preserved across metadata-only refreshes.
PORTFOLIO_OWNED_FIELDS = ("last_graph_update", "graph_source_commit")


# ---------------------------------------------------------------- paths

def registry_dir(home: Path | None = None) -> Path:
    return (Path(home) if home else Path.home()) / ".amir" / "registry"


def registry_path(home: Path | None = None) -> Path:
    return registry_dir(home) / "projects.yaml"


def legacy_registry_path(home: Path | None = None) -> Path:
    return registry_dir(home) / "projects.json"


def history_dir(home: Path | None = None) -> Path:
    return registry_dir(home) / "project-history"


def lock_path(home: Path | None = None) -> Path:
    return registry_dir(home) / "projects.lock.json"


# ---------------------------------------------------------------- load / save / migrate

def _empty_registry() -> dict:
    return {"schema_version": REGISTRY_SCHEMA_VERSION, "projects": []}


def normalize_entry(entry: dict) -> dict:
    """Project the entry onto exactly REGISTRY_FIELDS; absent values become null."""
    normalized = {field: entry.get(field) for field in REGISTRY_FIELDS}
    if normalized["health"] is None:
        normalized["health"] = "unknown"
    return normalized


def load_registry(home: Path | None = None) -> dict:
    yaml = require_yaml()
    path = registry_path(home)
    if not path.is_file():
        migrated = _migrate_legacy_json(home)
        return migrated if migrated is not None else _empty_registry()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict) or not isinstance(data.get("projects"), list):
        raise AmirError(f"registry {path} is malformed: 'projects' must be a list")
    return {"schema_version": data.get("schema_version", REGISTRY_SCHEMA_VERSION),
            "projects": [normalize_entry(p) for p in data["projects"] if isinstance(p, dict)]}


def save_registry(registry: dict, home: Path | None = None, snapshot: bool = True) -> Path:
    """Atomic write (tmp + os.replace) under the registry lock; one history snapshot per mutation."""
    yaml = require_yaml()
    path = registry_path(home)
    ordered = {"schema_version": REGISTRY_SCHEMA_VERSION,
               "projects": sorted((normalize_entry(p) for p in registry.get("projects", [])),
                                  key=lambda p: p.get("id") or "")}
    text = yaml.safe_dump(ordered, sort_keys=True, allow_unicode=True, default_flow_style=False)
    lock = acquire_lock_file(lock_path(home), LOCK_STALE_SECONDS)
    try:
        atomic_write_text(path, text)
        if snapshot:
            atomic_write_text(history_dir(home) / f"{utc_stamp()}-projects.yaml", text)
    finally:
        release_lock_file(lock)
    return path


def _legacy_entry(old: dict) -> dict:
    return normalize_entry({
        "id": old.get("id"), "name": old.get("name"), "root": old.get("root"),
        "manifest": old.get("manifest_path") or old.get("manifest"),
        "cursor_enabled": old.get("cursor_enabled"),
        "claude_code_enabled": old.get("claude_code_enabled", old.get("claude_enabled")),
    })


def _migrate_legacy_json(home: Path | None = None) -> dict | None:
    """One-time projects.json -> projects.yaml migration; old file kept as .migrated."""
    legacy = legacy_registry_path(home)
    if not legacy.is_file():
        return None
    data = read_json(legacy)
    projects = [_legacy_entry(p) for p in data.get("projects", [])
                if isinstance(p, dict) and p.get("id")]
    registry = {"schema_version": REGISTRY_SCHEMA_VERSION, "projects": projects}
    save_registry(registry, home)
    target = legacy.with_name(legacy.name + ".migrated")
    if target.exists():
        target = legacy.with_name(f"{legacy.name}.migrated-{utc_stamp()}")
    os.replace(legacy, target)
    return registry


# ---------------------------------------------------------------- data sources

def _enum_or_none(value, allowed: tuple) -> str | None:
    return value if value in allowed else None


def _number_or_none(value) -> float | int | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _mtime_iso(path: Path) -> str | None:
    try:
        stamp = path.stat().st_mtime
    except OSError:
        return None
    return datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_portfolio_yaml(project_root: Path) -> dict:
    """Optional per-project .amir/portfolio.yaml; absent -> {} (fields stay null)."""
    yaml = require_yaml()
    path = Path(project_root) / ".amir" / "portfolio.yaml"
    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise AmirError(f"invalid YAML in {path}: {exc}")
    return data if isinstance(data, dict) else {}


def git_info(project_root: Path) -> dict:
    """Best-effort git metadata via subprocess; any failure -> nulls (never raises)."""
    def run(*argv) -> str | None:
        try:
            proc = subprocess.run(["git", "-C", str(project_root), *argv],
                                  capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS)
        except (OSError, subprocess.TimeoutExpired):
            return None
        return proc.stdout.strip() if proc.returncode == 0 else None

    commit = run("rev-parse", "HEAD")
    if commit is None:
        return {"branch": None, "commit": None, "dirty": None}
    porcelain = run("status", "--porcelain")
    return {"branch": run("rev-parse", "--abbrev-ref", "HEAD"), "commit": commit,
            "dirty": None if porcelain is None else bool(porcelain)}


def commit_marker(info: dict) -> str | None:
    """'<sha>' or '<sha>-dirty' for graph provenance; None when not a git repo."""
    if not info.get("commit"):
        return None
    return info["commit"] + ("-dirty" if info.get("dirty") else "")


def graphify_config(manifest_data: dict) -> dict:
    return (manifest_data.get("project_tools") or {}).get("graphify") or {}


def local_graph_path(project_root: Path, manifest_data: dict) -> Path:
    out_dir = graphify_config(manifest_data).get("output_directory") or "graphify-out"
    return Path(project_root) / out_dir / "graph.json"


def entry_from_sources(project_root: Path, manifest_data: dict | None = None) -> dict:
    """Build a registry entry from .amir/project.yaml, optional .amir/portfolio.yaml,
    .ai/status.md mtime, and the local graphify output. Portfolio-owned graph fields
    (last_graph_update, graph_source_commit) start null; portfolio.py fills them."""
    import manifest as manifest_mod  # noqa: PLC0415

    root = Path(project_root).resolve()
    data = manifest_data if manifest_data is not None else manifest_mod.load_manifest(root)
    project = data.get("project") or {}
    project_id = project.get("id")
    if not project_id:
        raise AmirError(f"{root / '.amir' / 'project.yaml'} has no project.id; a stable id is "
                        "required (ids are never derived from the folder name alone)")
    hosts = data.get("hosts") or {}
    graph_file = local_graph_path(root, data)
    portfolio_meta = load_portfolio_yaml(root)
    proj_block = portfolio_meta.get("project") or {}
    progress = portfolio_meta.get("progress") or {}
    asana = (portfolio_meta.get("references") or {}).get("asana") or {}
    return normalize_entry({
        "id": str(project_id),
        "name": project.get("name") or str(project_id),
        "root": str(root),
        "manifest": str(root / ".amir" / "project.yaml"),
        "lifecycle": _enum_or_none(proj_block.get("lifecycle"), LIFECYCLES),
        "priority": _enum_or_none(proj_block.get("priority"), PRIORITIES),
        "health": _enum_or_none(proj_block.get("health"), HEALTH_STATES),
        "current_phase": progress.get("current_phase"),
        "confirmed_progress": _number_or_none(progress.get("confirmed_percent")),
        "estimated_progress": _number_or_none(progress.get("estimated_percent")),
        "last_status_update": _mtime_iso(root / ".ai" / "status.md"),
        "graph_path": str(graph_file) if graph_file.is_file() else None,
        "graph_enabled": bool(graphify_config(data).get("enabled")),
        "cursor_enabled": bool((hosts.get("cursor") or {}).get("enabled")),
        "claude_code_enabled": bool((hosts.get("claude_code") or {}).get("enabled")),
        "asana_reference": (str(asana["project_gid"])
                            if asana.get("enabled") and asana.get("project_gid") else None),
    })


def entry_from_manifest(manifest_data: dict, project_root: Path) -> dict:
    """Back-compat name used by amirctl registry-add."""
    return entry_from_sources(project_root, manifest_data)


# ---------------------------------------------------------------- mutations / queries

def _same_root(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    return os.path.normcase(os.path.normpath(a)) == os.path.normcase(os.path.normpath(b))


def upsert_project(registry: dict, entry: dict) -> dict:
    """Add/refresh an entry. Same id at a DIFFERENT root is refused (ids are unique)."""
    entry = normalize_entry(entry)
    previous = next((p for p in registry.get("projects", []) if p.get("id") == entry["id"]), None)
    if previous is not None and not _same_root(previous.get("root"), entry.get("root")):
        raise AmirError(f"duplicate project id '{entry['id']}': already registered at "
                        f"{previous.get('root')} -- ids must be unique; change project.id in "
                        ".amir/project.yaml of the new project")
    merged = dict(entry)
    if previous:
        for field in PORTFOLIO_OWNED_FIELDS:
            if merged.get(field) is None:
                merged[field] = previous.get(field)
    others = [p for p in registry.get("projects", []) if p.get("id") != entry["id"]]
    return {**registry, "projects": others + [merged]}


def remove_project(registry: dict, project_id: str) -> dict:
    remaining = [p for p in registry.get("projects", []) if p.get("id") != project_id]
    if len(remaining) == len(registry.get("projects", [])):
        raise AmirError(f"project '{project_id}' is not registered")
    return {**registry, "projects": remaining}


def find_entry(registry: dict, target: str) -> dict | None:
    """Look up by id first, then by (resolved) root path."""
    for entry in registry.get("projects", []):
        if entry.get("id") == target:
            return entry
    try:
        resolved = str(Path(target).resolve())
    except OSError:
        return None
    return next((p for p in registry.get("projects", [])
                 if _same_root(p.get("root"), resolved)), None)


def archive_entry(entry: dict, home: Path | None = None) -> Path:
    """Write the removed entry to project-history\\removed-<id>-<stamp>.yaml."""
    yaml = require_yaml()
    path = history_dir(home) / f"removed-{entry.get('id', 'unknown')}-{utc_stamp()}.yaml"
    atomic_write_text(path, yaml.safe_dump(normalize_entry(entry), sort_keys=True,
                                           allow_unicode=True))
    return path


def inspect(registry: dict) -> list[dict]:
    """Per-entry health report (checks registered roots only; never scans the machine)."""
    report = []
    for entry in sorted(registry.get("projects", []), key=lambda p: p.get("id") or ""):
        root = Path(entry.get("root") or "")
        manifest_file = Path(entry.get("manifest") or (root / ".amir" / "project.yaml"))
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


def validate_registry_data(registry: dict, catalog_root: Path) -> list[str]:
    """Schema-validate the registry dict against schemas/registry.schema.json."""
    from util import require_jsonschema  # noqa: PLC0415

    jsonschema = require_jsonschema()
    schema_file = Path(catalog_root) / "schemas" / "registry.schema.json"
    if not schema_file.is_file():
        return [f"registry schema not found: {schema_file}"]
    validator = jsonschema.Draft202012Validator(read_json(schema_file))
    errors = sorted(validator.iter_errors(registry), key=lambda e: list(e.absolute_path))
    return [f"at {'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in errors]
