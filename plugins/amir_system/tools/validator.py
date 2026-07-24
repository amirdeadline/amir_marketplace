"""Project validation per SPEC: schema, lock drift, naming, duplicates, hosts, MCP,
secret hygiene, graphify health, isolation. Output: human table or --json."""
from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import catalog as catalog_mod
import lockfile
import manifest as manifest_mod
import renderer
from util import GENERATED_MARKER_KEY, AmirError, read_json

SNAKE_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")
ENV_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
SKILL_NAME_EXCEPTIONS = {"create-project-doc"}  # user-specified exact name


@dataclass
class Check:
    name: str
    status: str  # ok | warn | error
    detail: str


def find_duplicate_commands(catalog: dict, extra_names: dict | None = None) -> dict:
    """Map duplicate command name -> sorted owner list across all components (+ extras)."""
    owners: dict[str, list[str]] = {}
    for component in catalog.get("components", []):
        for command in component.get("commands", []):
            owners.setdefault(command, []).append(component["id"])
    for name, owner in (extra_names or {}).items():
        owners.setdefault(name, []).append(owner)
    return {name: sorted(ids) for name, ids in owners.items() if len(ids) > 1}


def _check_manifest(project_root: Path, catalog_root: Path, checks: list):
    try:
        data, errors = manifest_mod.validate_manifest_file(project_root, catalog_root)
    except AmirError as exc:
        checks.append(Check("manifest-schema", "error", str(exc)))
        return None
    if errors:
        checks.append(Check("manifest-schema", "error", "; ".join(errors)))
    else:
        checks.append(Check("manifest-schema", "ok", "manifest validates against schema v2"))
    return data


def _check_lock(project_root: Path, catalog_root: Path, cat: dict, data: dict, checks: list):
    lock_path = project_root / lockfile.LOCK_RELPATH
    if not lock_path.is_file():
        checks.append(Check("lock-drift", "error", f"lock file missing: {lock_path}"))
        return
    try:
        lock = lockfile.load_lock(project_root)
    except AmirError as exc:
        checks.append(Check("lock-drift", "error", str(exc)))
        return
    schema_errors = lockfile.validate_lock(lock, catalog_root)
    if schema_errors:
        checks.append(Check("lock-drift", "error", "lock schema: " + "; ".join(schema_errors)))
        return
    drift = lockfile.verify_lock(catalog_root, cat, lock)
    selected = set(manifest_mod.selected_component_ids(data))
    locked = set((lock.get("components") or {}).keys())
    parts = []
    for cid, info in sorted(drift.items()):
        parts.append(f"{cid}: changed={len(info['changed'])} missing={len(info['missing'])} "
                     f"added={len(info['added'])}")
    if selected - locked:
        parts.append("selected but not locked: " + ", ".join(sorted(selected - locked)))
    if locked - selected:
        parts.append("locked but not selected: " + ", ".join(sorted(locked - selected)))
    if parts:
        checks.append(Check("lock-drift", "error", "; ".join(parts) + " -- run /amir:repair_project"))
    else:
        checks.append(Check("lock-drift", "ok", f"{len(locked)} component(s) match lock checksums"))


def _check_naming(cat: dict, checks: list) -> None:
    bad = []
    for component in cat.get("components", []):
        bad.extend(f"command '{c}'" for c in component.get("commands", []) if not SNAKE_RE.match(c))
        bad.extend(f"skill '{s}'" for s in component.get("skills", [])
                   if not SNAKE_RE.match(s) and s not in SKILL_NAME_EXCEPTIONS)
    if bad:
        checks.append(Check("naming", "error",
                            "non-snake_case names (only create-project-doc is exempt): " + ", ".join(sorted(bad))))
    else:
        checks.append(Check("naming", "ok", "all command/skill names comply with /amir: snake_case"))


def _check_duplicates(project_root: Path, cat: dict, checks: list) -> None:
    extra = {}
    commands_dir = project_root / ".cursor" / "commands"
    known = {c for component in cat.get("components", []) for c in component.get("commands", [])}
    if commands_dir.is_dir():
        for path in sorted(commands_dir.glob("amir_*.md")):
            name = path.stem[len("amir_"):]
            if name not in known:
                extra[name] = f"rendered:{path.name}"
    duplicates = find_duplicate_commands(cat, extra)
    if duplicates:
        detail = "; ".join(f"'{name}' owned by {', '.join(ids)}" for name, ids in sorted(duplicates.items()))
        checks.append(Check("duplicate-commands", "error", detail))
    else:
        checks.append(Check("duplicate-commands", "ok", "no duplicate command names across plugins or rendered output"))


def _check_resolution(data: dict, cat: dict, checks: list, env, which) -> None:
    selection = manifest_mod.selected_component_ids(data)
    result = catalog_mod.resolve(cat, selection, manifest_mod.host_matrix(data),
                                 manifest_mod.granted_permissions(data), env=env, which=which)
    if result.ok:
        checks.append(Check("component-resolution", "ok",
                            f"{len(selection)} selected component(s) resolve cleanly"))
    else:
        detail = "; ".join(f"[{i.rule}] {i.message}" for i in result.issues)
        checks.append(Check("component-resolution", "error", detail))


def _check_mcp(project_root: Path, checks: list) -> None:
    mcp_path = project_root / ".cursor" / "mcp.json"
    if not mcp_path.is_file():
        checks.append(Check("mcp-definitions", "ok", "no .cursor/mcp.json rendered (nothing selected needs MCP)"))
        return
    try:
        data = read_json(mcp_path)
    except AmirError as exc:
        checks.append(Check("mcp-definitions", "error", str(exc)))
        return
    problems, secret_problems = [], []
    for name, config in sorted((data.get("mcpServers") or {}).items()):
        if not isinstance(config, dict):
            problems.append(f"server '{name}' is not an object")
            continue
        if not isinstance(config.get("command"), str) or not config.get("command"):
            problems.append(f"server '{name}' has no 'command'")
        for key, value in sorted((config.get("env") or {}).items()):
            literal = isinstance(value, str) and value and not (
                ENV_NAME_RE.match(value) or value.startswith("${"))
            if literal:
                secret_problems.append(f"server '{name}' env '{key}' holds a literal value; "
                                       "use an env-var reference instead")
    if problems:
        checks.append(Check("mcp-definitions", "error", "; ".join(problems)))
    else:
        checks.append(Check("mcp-definitions", "ok", "all MCP server entries are well-formed"))
    if secret_problems:
        checks.append(Check("secret-references", "error", "; ".join(secret_problems)))
    else:
        checks.append(Check("secret-references", "ok",
                            "secret references are env-var names only (values never stored)"))


def _check_graphify(project_root: Path, data: dict, checks: list, which) -> None:
    tool = ((data.get("project_tools") or {}).get("graphify") or {})
    if not tool.get("enabled"):
        checks.append(Check("graphify-health", "ok", "graphify not enabled for this project"))
        return
    problems = []
    if which("graphify") is None:
        problems.append("graphify CLI not found on PATH")
    output_dir = tool.get("output_directory", "graphify-out")
    graph = project_root / output_dir / "graph.json"
    if not graph.is_file():
        problems.append(f"{output_dir}/graph.json missing -- run /amir:graphify_build")
    if problems:
        checks.append(Check("graphify-health", "error", "; ".join(problems)))
    else:
        checks.append(Check("graphify-health", "ok", f"CLI present and {output_dir}/graph.json exists"))


def _check_isolation(project_root: Path, data: dict, cat: dict, catalog_root: Path, checks: list) -> None:
    try:
        plan = renderer.render_plan(project_root, data, cat, catalog_root)
    except Exception as exc:  # renderer must never take validation down
        checks.append(Check("isolation", "error", f"render planning failed: {exc}"))
        return
    outside = []
    root_resolved = project_root.resolve()
    for rel in plan.desired:
        target = (project_root / rel).resolve()
        if root_resolved not in (target, *target.parents):
            outside.append(rel)
    if outside:
        checks.append(Check("isolation", "error", "rendered paths escape project root: " + ", ".join(outside)))
    else:
        checks.append(Check("isolation", "ok",
                            f"all {len(plan.desired)} rendered path(s) stay inside the project root"))


def run_checks(project_root: Path, catalog_root: Path, *, env=None, which=None) -> list[Check]:
    import os  # noqa: PLC0415

    env = os.environ if env is None else env
    which = shutil.which if which is None else which
    project_root = Path(project_root)
    catalog_root = Path(catalog_root)
    checks: list[Check] = []
    try:
        cat = catalog_mod.load_catalog(catalog_root)
        checks.append(Check("catalog-schema", "ok", "catalog.json validates against component metadata schema"))
    except AmirError as exc:
        checks.append(Check("catalog-schema", "error", str(exc)))
        return checks
    data = _check_manifest(project_root, catalog_root, checks)
    _check_naming(cat, checks)
    _check_duplicates(project_root, cat, checks)
    if data is None:
        return checks
    _check_lock(project_root, catalog_root, cat, data, checks)
    _check_resolution(data, cat, checks, env, which)
    _check_mcp(project_root, checks)
    _check_graphify(project_root, data, checks, which)
    _check_isolation(project_root, data, cat, catalog_root, checks)
    return checks


def format_table(checks: list) -> str:
    width = max((len(c.name) for c in checks), default=10)
    lines = [f"{'CHECK'.ljust(width)}  STATUS  DETAIL",
             f"{'-' * width}  ------  {'-' * 40}"]
    for check in checks:
        lines.append(f"{check.name.ljust(width)}  {check.status.upper():6}  {check.detail}")
    errors = sum(1 for c in checks if c.status == "error")
    warns = sum(1 for c in checks if c.status == "warn")
    lines.append(f"\n{len(checks)} checks: {errors} error(s), {warns} warning(s)")
    return "\n".join(lines)


def to_json(checks: list) -> str:
    return json.dumps({"checks": [check.__dict__ for check in checks],
                       "ok": all(c.status != "error" for c in checks)}, indent=2) + "\n"
