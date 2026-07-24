"""Catalog loading, schema validation, and component activation resolution.

resolve() implements every activation-block rule from SPEC-amir_project-tools.md section 10:
missing dependency (including transitive, with an explanation chain), unsupported host,
unsupported operating system, missing credentials (environment variable PRESENCE only -- values
are never read beyond truthiness), rejected permissions, version incompatibility, conflicts,
and circular dependencies. Output ordering is deterministic.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

from util import AmirError, default_catalog_root, read_json

HOST_IDS = ("claude-code", "cursor")


@dataclass(frozen=True)
class ResolveIssue:
    component_id: str
    rule: str
    message: str


@dataclass
class ResolveResult:
    ok: bool
    components: list = field(default_factory=list)  # deterministic activation order (ids)
    issues: list = field(default_factory=list)  # sorted list[ResolveIssue]


def current_os() -> str:
    return {"win32": "windows", "darwin": "macos"}.get(sys.platform, "linux")


def load_catalog(catalog_root: Path | None = None, validate: bool = True) -> dict:
    root = Path(catalog_root) if catalog_root else default_catalog_root()
    catalog = read_json(root / "catalog" / "catalog.json")
    if validate:
        errors = validate_catalog(catalog, root)
        if errors:
            raise AmirError("catalog.json failed schema validation:\n  " + "\n  ".join(errors))
    return catalog


def validate_catalog(catalog: dict, catalog_root: Path | None = None) -> list[str]:
    from util import require_jsonschema  # noqa: PLC0415

    jsonschema = require_jsonschema()
    root = Path(catalog_root) if catalog_root else default_catalog_root()
    schema = read_json(root / "schemas" / "component-metadata.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(catalog), key=lambda e: list(e.absolute_path))
    return [f"at {'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}" for e in errors]


def components_by_id(catalog: dict) -> dict:
    return {component["id"]: component for component in catalog.get("components", [])}


def plugin_group_ids(catalog: dict, plugin: str) -> list[str]:
    return sorted(c["id"] for c in catalog.get("components", []) if c.get("plugin") == plugin)


def _version_tuple(version: str) -> tuple:
    parts = re.findall(r"\d+", version or "")
    return tuple(int(part) for part in parts) if parts else (0,)


def _component_deps(component: dict, byid: dict) -> list[str]:
    return sorted(d for d in component.get("dependencies", []) if d in byid)


def _executable_deps(component: dict, byid: dict) -> list[str]:
    return sorted(d for d in component.get("dependencies", []) if d not in byid)


def _detect_cycles(byid: dict, roots: list[str]) -> list[list[str]]:
    cycles, visiting, done = [], [], set()

    def visit(node: str) -> None:
        if node in done:
            return
        if node in visiting:
            cycles.append(visiting[visiting.index(node):] + [node])
            return
        visiting.append(node)
        for dep in _component_deps(byid.get(node, {}), byid):
            visit(dep)
        visiting.pop()
        done.add(node)

    for root in roots:
        visit(root)
    return cycles


def _missing_dep_chains(byid: dict, selected: set, roots: list[str]) -> list[tuple[str, str, str]]:
    """(root, missing_dep, chain-string) for every transitive dep not in the selection."""
    findings = []

    def walk(node: str, chain: list[str], seen: set) -> None:
        for dep in _component_deps(byid[node], byid):
            if dep in seen:
                continue
            if dep not in selected:
                findings.append((chain[0], dep, " -> ".join(chain + [dep])))
                continue
            walk(dep, chain + [dep], seen | {dep})

    for root in roots:
        walk(root, [root], {root})
    return sorted(set(findings))


def _network_granted(component: dict, permissions: dict) -> bool:
    policy = (permissions or {}).get("network") or {}
    if policy.get("default", "deny") == "allow":
        return True
    return component["id"] in (policy.get("allowed_components") or [])


def _secrets_granted(component: dict, permissions: dict) -> bool:
    policy = (permissions or {}).get("secrets") or {}
    if policy.get("default", "deny") == "allow":
        return True
    allowed = set(policy.get("allowed_references") or [])
    required = set(component.get("required_credentials") or [])
    return bool(required) and required <= allowed


def _check_hosts(component: dict, host_matrix: dict, issues: list) -> None:
    for host, info in sorted((host_matrix or {}).items()):
        if not (info or {}).get("enabled"):
            continue
        if host not in component.get("supported_hosts", []):
            issues.append(ResolveIssue(component["id"], "unsupported-host",
                                       f"'{component['id']}' does not support enabled host '{host}' "
                                       f"(supported: {', '.join(component.get('supported_hosts', []))})"))
            continue
        constraint = (component.get("host_version_constraints") or {}).get(host) or {}
        version = (info or {}).get("version")
        if not constraint or not version:
            continue
        have = _version_tuple(version)
        if constraint.get("min") and have < _version_tuple(constraint["min"]):
            issues.append(ResolveIssue(component["id"], "version-incompatible",
                                       f"'{component['id']}' requires {host} >= {constraint['min']} (found {version})"))
        if constraint.get("max") and have > _version_tuple(constraint["max"]):
            issues.append(ResolveIssue(component["id"], "version-incompatible",
                                       f"'{component['id']}' requires {host} <= {constraint['max']} (found {version})"))


def _topological_order(byid: dict, selected: set) -> list[str]:
    order, placed = [], set()
    pending = sorted(selected)
    while pending:
        progressed = False
        for candidate in list(pending):
            deps = [d for d in _component_deps(byid.get(candidate, {}), byid) if d in selected]
            if all(dep in placed for dep in deps):
                order.append(candidate)
                placed.add(candidate)
                pending.remove(candidate)
                progressed = True
        if not progressed:  # cycle among remaining; append sorted for determinism
            order.extend(sorted(pending))
            break
    return order


def resolve(catalog: dict, selected_ids, host_matrix: dict | None = None,
            granted_permissions: dict | None = None, *, env=None, which=None,
            os_name: str | None = None) -> ResolveResult:
    """Validate an activation set against every catalog rule. Deterministic output."""
    env = os.environ if env is None else env
    which = shutil.which if which is None else which
    os_name = os_name or current_os()
    byid = components_by_id(catalog)
    issues: list[ResolveIssue] = []

    selected = sorted(set(selected_ids))
    known = [cid for cid in selected if cid in byid]
    for cid in selected:
        if cid not in byid:
            issues.append(ResolveIssue(cid, "unknown-component", f"'{cid}' is not in the catalog"))

    for cycle in _detect_cycles(byid, known):
        issues.append(ResolveIssue(cycle[0], "circular-dependency",
                                   "circular dependency: " + " -> ".join(cycle)))

    for root, missing, chain in _missing_dep_chains(byid, set(known), known):
        issues.append(ResolveIssue(root, "missing-dependency",
                                   f"'{root}' requires component '{missing}' which is not selected "
                                   f"(dependency chain: {chain}); add '{missing}' to the selection"))

    for cid in known:
        component = byid[cid]
        for exe in _executable_deps(component, byid):
            if which(exe) is None:
                issues.append(ResolveIssue(cid, "missing-dependency",
                                           f"'{cid}' depends on executable '{exe}' which is not on PATH"))
        for exe in sorted(component.get("required_executables", [])):
            if which(exe) is None:
                issues.append(ResolveIssue(cid, "missing-executable",
                                           f"'{cid}' requires executable '{exe}' which is not on PATH "
                                           f"(health check: {component.get('health_check', 'n/a')})"))
        if os_name not in component.get("supported_operating_systems", []):
            issues.append(ResolveIssue(cid, "unsupported-os",
                                       f"'{cid}' does not support OS '{os_name}' (supported: "
                                       f"{', '.join(component.get('supported_operating_systems', []))})"))
        _check_hosts(component, host_matrix or {}, issues)
        for name in sorted(component.get("required_credentials", [])):
            if not env.get(name):  # presence only -- the value is never inspected or logged
                issues.append(ResolveIssue(cid, "missing-credential",
                                           f"'{cid}' requires credential environment variable '{name}' "
                                           "which is not set (checked by name only)"))
        if granted_permissions is not None:
            if component.get("network_access") == "required" and not _network_granted(component, granted_permissions):
                issues.append(ResolveIssue(cid, "permission-rejected",
                                           f"'{cid}' requires network access but the project permission policy "
                                           "denies it (permissions.network)"))
            if component.get("secret_access") == "required" and not _secrets_granted(component, granted_permissions):
                issues.append(ResolveIssue(cid, "permission-rejected",
                                           f"'{cid}' requires secret access but the project permission policy "
                                           "denies it (permissions.secrets)"))
        for other in sorted(component.get("conflicts_with", [])):
            if other in known and cid < other:
                issues.append(ResolveIssue(cid, "conflict",
                                           f"'{cid}' conflicts with selected component '{other}'"))

    issues.sort(key=lambda issue: (issue.component_id, issue.rule, issue.message))
    order = _topological_order(byid, set(known))
    return ResolveResult(ok=not issues, components=order, issues=issues)
