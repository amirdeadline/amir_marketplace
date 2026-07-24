"""Build and verify .amir/components.lock.json (per-source-file sha256 pinning)."""
from __future__ import annotations

from pathlib import Path

from util import AmirError, dump_json, read_json, sha256_file, utc_now_iso, write_text

LOCK_RELPATH = Path(".amir") / "components.lock.json"


def _add_tree(files: dict, catalog_root: Path, directory: Path) -> None:
    if not directory.is_dir():
        return
    for path in sorted(directory.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            files[path.relative_to(catalog_root).as_posix()] = path


def component_source_files(catalog_root: Path, component: dict) -> dict:
    """Repo-relative posix path -> absolute Path for every source file the component owns.

    Defensive by design: other agents may still be writing plugin content, so any missing
    directory or command file simply contributes nothing (drift/repair picks it up later).
    """
    catalog_root = Path(catalog_root)
    plugin_root = catalog_root / "plugins" / component["plugin"]
    files: dict[str, Path] = {}
    commands_root = plugin_root / "commands"
    if commands_root.is_dir():
        wanted = set(component.get("commands", []))
        for path in sorted(commands_root.rglob("*.md")):
            if path.stem in wanted:
                files[path.relative_to(catalog_root).as_posix()] = path
    for skill in component.get("skills", []):
        _add_tree(files, catalog_root, plugin_root / "skills" / skill)
    for server in component.get("mcp_servers", []):
        _add_tree(files, catalog_root, plugin_root / "mcp" / server)
    _add_tree(files, catalog_root, plugin_root / "scripts" / component["id"])
    if component["id"] == "rules":
        _add_tree(files, catalog_root, plugin_root / "rules")
    return files


def build_lock(catalog_root: Path, catalog: dict, selected_ids) -> dict:
    from catalog import components_by_id  # noqa: PLC0415

    byid = components_by_id(catalog)
    components = {}
    for cid in sorted(set(selected_ids)):
        component = byid.get(cid)
        if component is None:
            raise AmirError(f"cannot lock unknown component '{cid}'")
        sources = component_source_files(catalog_root, component)
        components[cid] = {
            "version": component["version"],
            "source_path": f"plugins/{component['plugin']}",
            "files": {rel: sha256_file(path) for rel, path in sources.items()},
        }
    return {
        "schema_version": 1,
        "generated_at": utc_now_iso(),
        "catalog_version": catalog.get("catalog_version", "0.0.0"),
        "components": components,
    }


def write_lock(project_root: Path, lock: dict) -> Path:
    path = Path(project_root) / LOCK_RELPATH
    write_text(path, dump_json(lock))
    return path


def load_lock(project_root: Path) -> dict:
    return read_json(Path(project_root) / LOCK_RELPATH)


def validate_lock(lock: dict, catalog_root: Path) -> list[str]:
    from util import require_jsonschema  # noqa: PLC0415

    jsonschema = require_jsonschema()
    schema = read_json(Path(catalog_root) / "schemas" / "components-lock.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(lock), key=lambda e: list(e.absolute_path))
    return [f"at {'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}" for e in errors]


def verify_lock(catalog_root: Path, catalog: dict, lock: dict) -> dict:
    """Compare locked checksums against current source files.

    Returns {component_id: {"changed": [...], "missing": [...], "added": [...]}} with only
    drifted components present. Empty dict == no drift.
    """
    from catalog import components_by_id  # noqa: PLC0415

    byid = components_by_id(catalog)
    drift: dict[str, dict] = {}
    for cid, locked in sorted((lock.get("components") or {}).items()):
        component = byid.get(cid)
        if component is None:
            drift[cid] = {"changed": [], "missing": [], "added": [],
                          "note": "component no longer exists in the catalog"}
            continue
        current = {rel: sha256_file(path)
                   for rel, path in component_source_files(catalog_root, component).items()}
        locked_files = locked.get("files") or {}
        changed = sorted(rel for rel, sha in locked_files.items()
                         if rel in current and current[rel] != sha)
        missing = sorted(rel for rel in locked_files if rel not in current)
        added = sorted(rel for rel in current if rel not in locked_files)
        if changed or missing or added:
            drift[cid] = {"changed": changed, "missing": missing, "added": added}
    return drift
