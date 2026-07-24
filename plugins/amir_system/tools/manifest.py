"""Load and validate the project manifest (.amir/project.yaml, schema_version 2)."""
from __future__ import annotations

from pathlib import Path

from util import AmirError, read_json, require_yaml

MANIFEST_RELPATH = Path(".amir") / "project.yaml"

# manifest project_tools key -> catalog component id
TOOL_COMPONENT_MAP = {
    "graphify": "graphify",
    "serena": "serena",
    "context7": "context7",
    "semgrep": "semgrep",
    "langfuse": "langfuse",
    "openhands": "openhands",
    "git_worktrees": "worktrees",
    "swe_bench": "swebench",
    "terminal_bench": "terminalbench",
}

# manifest system_capabilities key -> catalog component id
CAPABILITY_COMPONENT_MAP = {"asana": "asana", "playwright": "playwright"}


def manifest_path(project_root: Path) -> Path:
    return Path(project_root) / MANIFEST_RELPATH


def load_manifest(project_root: Path) -> dict:
    """Parse the manifest; YAML syntax errors are reported with line/column context."""
    yaml = require_yaml()
    path = manifest_path(project_root)
    if not path.is_file():
        raise AmirError(f"manifest not found: {path}")
    text = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        raise AmirError(f"invalid YAML in {path}{where}: {getattr(exc, 'problem', exc)}")
    if not isinstance(data, dict):
        raise AmirError(f"manifest {path} must be a YAML mapping, got {type(data).__name__}")
    return data


def _line_hint(raw_text: str | None, key: str | None) -> str:
    """Best-effort line context: report the line number if the failing key appears exactly once."""
    if not raw_text or not key:
        return ""
    hits = [i + 1 for i, line in enumerate(raw_text.splitlines())
            if line.lstrip().startswith(f"{key}:")]
    return f" (near line {hits[0]})" if len(hits) == 1 else ""


def validate_manifest(manifest: dict, catalog_root: Path, raw_text: str | None = None) -> list[str]:
    """Schema-validate against schemas/project-manifest.schema.json; returns error strings."""
    from util import require_jsonschema  # noqa: PLC0415

    jsonschema = require_jsonschema()
    schema = read_json(Path(catalog_root) / "schemas" / "project-manifest.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(manifest), key=lambda e: list(e.absolute_path))
    messages = []
    for error in errors:
        location = "/".join(str(p) for p in error.absolute_path) or "<root>"
        key = None
        for part in reversed(list(error.absolute_path)):
            if isinstance(part, str):
                key = part
                break
        messages.append(f"at {location}: {error.message}{_line_hint(raw_text, key)}")
    return messages


def validate_manifest_file(project_root: Path, catalog_root: Path) -> tuple[dict, list[str]]:
    path = manifest_path(project_root)
    raw = path.read_text(encoding="utf-8") if path.is_file() else None
    data = load_manifest(project_root)
    return data, validate_manifest(data, catalog_root, raw)


def selected_component_ids(manifest: dict) -> list[str]:
    """Effective component selection: amir_project groups + enabled project tools + granted capabilities."""
    selected: set[str] = set()
    amir_project = ((manifest.get("plugins") or {}).get("amir_project") or {})
    if amir_project.get("enabled"):
        selected.update(amir_project.get("components") or [])
    for key, component_id in TOOL_COMPONENT_MAP.items():
        if ((manifest.get("project_tools") or {}).get(key) or {}).get("enabled"):
            selected.add(component_id)
    for key, component_id in CAPABILITY_COMPONENT_MAP.items():
        if ((manifest.get("system_capabilities") or {}).get(key) or {}).get("allowed"):
            selected.add(component_id)
    return sorted(selected)


def selected_project_group_ids(manifest: dict, catalog: dict) -> list[str]:
    """Only the amir_project groups from the effective selection (used by the renderer)."""
    from catalog import components_by_id  # noqa: PLC0415

    byid = components_by_id(catalog)
    return sorted(cid for cid in selected_component_ids(manifest)
                  if byid.get(cid, {}).get("plugin") == "amir_project")


def host_matrix(manifest: dict) -> dict:
    hosts = manifest.get("hosts") or {}
    return {
        "claude-code": {"enabled": bool((hosts.get("claude_code") or {}).get("enabled")), "version": None},
        "cursor": {"enabled": bool((hosts.get("cursor") or {}).get("enabled")), "version": None},
    }


def granted_permissions(manifest: dict) -> dict:
    return manifest.get("permissions") or {"network": {"default": "deny"}, "secrets": {"default": "deny"}}
