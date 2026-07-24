"""Cross-project portfolio graph engine: %USERPROFILE%\\.amir\\portfolio\\.

Merges per-project graphify graphs (<project>/graphify-out/graph.json) into ONE global
graph with per-project node namespacing '<project.id>::<node.id>'.

Merge is a pure-JSON merge (stdlib): graphify 0.8.33's own 'merge-graphs' derives its
namespace tag from the graph file's directory (no per-input --as), which collapses
same-id nodes across projects, and 'global add' stores state under ~/.graphify -- both
verified unsuitable, so we do not shell out for merging. 'graphify update' IS used to
refresh stale local graphs when the CLI is on PATH.

Storage under %USERPROFILE%\\.amir\\portfolio\\:
  graph\\global-graph.json     merged node-link graph (namespaced ids)
  graph\\graph-metadata.json   per-project provenance {namespace, source_commit, counts, updated_at}
  graph\\backups\\              last 5 pre-replacement copies of the global graph
  reports\\ cache\\ locks\\      reports, scratch, and the update-all lock

Guarantees: atomic writes everywhere; a failed update retains the previous valid global
graph; re-adding a project replaces its namespace (idempotent, no duplicates); project
source trees are never modified (only <project>/graphify-out/graph.json, and only when
--remove-local-graph is explicitly requested).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from util import (AmirError, acquire_lock_file, atomic_write_text, dump_json, read_json,
                  release_lock_file, utc_now_iso, utc_stamp)

NAMESPACE_SEP = "::"
BACKUP_KEEP = 5
PORTFOLIO_LOCK_STALE_SECONDS = 30 * 60
STALE_STATUS_DAYS = 14
GRAPHIFY_TIMEOUT_SECONDS = 600

AI_FILES = ("project.md", "status.md", "tasks.md", "decisions.md", "risks.md",
            "architecture.md", "references.md", "changelog.md", "context_handoff.md")

SOURCE_EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv",
                       ".pytest_cache", ".mypy_cache", "dist", "build"}

# Report-only secret sweep of the global graph (names/counts reported, values never echoed).
SECRET_PATTERNS = (
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")),
    ("slack-token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("openai-style-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("bearer-token", re.compile(r"(?i)\bbearer\s+[a-z0-9_\-.=]{20,}")),
    ("generic-assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|password|passwd|access[_-]?token)\b['\"]?\s*[:=]\s*['\"][^'\"]{8,}")),
)


# ---------------------------------------------------------------- paths / state

def portfolio_dir(home: Path | None = None) -> Path:
    return (Path(home) if home else Path.home()) / ".amir" / "portfolio"


def graph_dir(home: Path | None = None) -> Path:
    return portfolio_dir(home) / "graph"


def global_graph_path(home: Path | None = None) -> Path:
    return graph_dir(home) / "global-graph.json"


def metadata_path(home: Path | None = None) -> Path:
    return graph_dir(home) / "graph-metadata.json"


def backups_dir(home: Path | None = None) -> Path:
    return graph_dir(home) / "backups"


def reports_dir(home: Path | None = None) -> Path:
    return portfolio_dir(home) / "reports"


def cache_dir(home: Path | None = None) -> Path:
    return portfolio_dir(home) / "cache"


def locks_dir(home: Path | None = None) -> Path:
    return portfolio_dir(home) / "locks"


def portfolio_lock_path(home: Path | None = None) -> Path:
    return locks_dir(home) / "portfolio.lock"


def empty_graph() -> dict:
    return {"directed": False, "multigraph": False, "graph": {},
            "nodes": [], "links": [], "hyperedges": []}


def load_global(home: Path | None = None) -> dict:
    path = global_graph_path(home)
    if not path.is_file():
        return empty_graph()
    graph = read_json(path)
    for key in ("nodes", "links"):
        if not isinstance(graph.get(key), list):
            raise AmirError(f"global graph {path} is malformed: '{key}' must be a list")
    return graph


def load_metadata(home: Path | None = None) -> dict:
    path = metadata_path(home)
    if not path.is_file():
        return {"schema_version": 1, "updated_at": None, "projects": {}}
    data = read_json(path)
    if not isinstance(data.get("projects"), dict):
        raise AmirError(f"graph metadata {path} is malformed: 'projects' must be a mapping")
    return data


# ---------------------------------------------------------------- graph primitives

def namespace_graph(local_graph: dict, project_id: str) -> tuple[list, list]:
    """Namespaced copies of a local graph's nodes and links ('<id>::<node>')."""
    prefix = f"{project_id}{NAMESPACE_SEP}"
    nodes = [{**node, "id": f"{prefix}{node['id']}", "namespace": project_id}
             for node in (local_graph.get("nodes") or []) if node.get("id") is not None]
    links = [{**link, "source": f"{prefix}{link['source']}",
              "target": f"{prefix}{link['target']}", "namespace": project_id}
             for link in (local_graph.get("links") or local_graph.get("edges") or [])
             if link.get("source") is not None and link.get("target") is not None]
    return nodes, links


def strip_namespace(global_graph: dict, project_id: str) -> dict:
    prefix = f"{project_id}{NAMESPACE_SEP}"
    nodes = [n for n in global_graph.get("nodes", [])
             if not str(n.get("id", "")).startswith(prefix)]
    links = [link for link in global_graph.get("links", [])
             if not (str(link.get("source", "")).startswith(prefix)
                     or str(link.get("target", "")).startswith(prefix))]
    return {**global_graph, "nodes": nodes, "links": links}


def graph_namespaces(global_graph: dict) -> set[str]:
    spaces = set()
    for node in global_graph.get("nodes", []):
        node_id = str(node.get("id", ""))
        if NAMESPACE_SEP in node_id:
            spaces.add(node_id.split(NAMESPACE_SEP, 1)[0])
    return spaces


def _backup_global(home: Path | None = None) -> Path | None:
    """Copy the current global graph into backups\\ (keep the newest BACKUP_KEEP)."""
    source = global_graph_path(home)
    if not source.is_file():
        return None
    destination = backups_dir(home) / f"global-graph-{utc_stamp()}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    backups = sorted(backups_dir(home).glob("global-graph-*.json"))
    for stale in backups[:-BACKUP_KEEP]:
        try:
            stale.unlink()
        except OSError:
            pass
    return destination


def _write_global_state(home: Path | None, graph: dict, metadata: dict) -> None:
    """Backup the previous global graph, then atomically write graph + metadata."""
    _backup_global(home)
    metadata = {**metadata, "updated_at": utc_now_iso()}
    atomic_write_text(global_graph_path(home), dump_json(graph))
    atomic_write_text(metadata_path(home), dump_json(metadata))


def _load_local_graph(path: Path) -> dict:
    graph = read_json(path)
    if not isinstance(graph.get("nodes"), list):
        raise AmirError(f"local graph {path} is malformed: 'nodes' must be a list")
    return graph


def merge_project_graph(home: Path | None, project_id: str, local_path: Path,
                        source_commit: str | None) -> tuple[int, int]:
    """Replace this project's namespace in the global graph from its local graph.

    Idempotent (strip-then-extend); the previous global graph is backed up first and
    retained untouched if anything here raises before the atomic write."""
    local = _load_local_graph(Path(local_path))
    nodes, links = namespace_graph(local, project_id)
    merged = strip_namespace(load_global(home), project_id)
    merged = {**merged, "nodes": merged["nodes"] + nodes, "links": merged["links"] + links}
    metadata = load_metadata(home)
    block = {"id": project_id, "namespace": project_id,
             "source_commit": source_commit or "unknown",
             "node_count": len(nodes), "edge_count": len(links),
             "updated_at": utc_now_iso()}
    metadata = {**metadata, "projects": {**metadata["projects"], project_id: block}}
    _write_global_state(home, merged, metadata)
    return len(nodes), len(links)


# ---------------------------------------------------------------- staleness

def newest_source_mtime(project_root: Path, extra_exclude: set[str] | None = None) -> float:
    """Newest file mtime under the project, skipping VCS/dependency/output dirs."""
    exclude = SOURCE_EXCLUDE_DIRS | (extra_exclude or set())
    newest = 0.0
    for dirpath, dirnames, filenames in os.walk(project_root):
        dirnames[:] = [d for d in dirnames
                       if d not in exclude and not d.startswith(".amir-removed-backup")]
        for name in filenames:
            try:
                newest = max(newest, (Path(dirpath) / name).stat().st_mtime)
            except OSError:
                pass
    return newest


def graph_staleness(project_root: Path, graph_path: Path, recorded_commit: str | None,
                    output_dir_name: str = "graphify-out") -> tuple[bool, str | None]:
    """(stale, reason): 'missing', 'commit-changed', 'source-newer', or (False, None)."""
    import registry as registry_mod  # noqa: PLC0415

    graph_path = Path(graph_path)
    if not graph_path.is_file():
        return True, "missing"
    current = registry_mod.commit_marker(registry_mod.git_info(project_root))
    if recorded_commit and current and recorded_commit != current:
        return True, "commit-changed"
    if newest_source_mtime(project_root, {output_dir_name}) > graph_path.stat().st_mtime:
        return True, "source-newer"
    return False, None


def _parse_iso(stamp: str | None) -> float | None:
    if not stamp:
        return None
    try:
        return datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc).timestamp()
    except ValueError:
        return None


def _namespace_out_of_date(metadata: dict, project_id: str, local_path: Path) -> bool:
    block = metadata.get("projects", {}).get(project_id)
    if block is None:
        return local_path.is_file()
    merged_at = _parse_iso(block.get("updated_at"))
    if merged_at is None:
        return True
    try:
        # +1s tolerance: updated_at is truncated to whole seconds, so a graph written in
        # the same second as the merge must not look newer than the merge.
        return local_path.stat().st_mtime > merged_at + 1.0
    except OSError:
        return False


def default_graphify_runner(project_root: Path) -> tuple[bool, str]:
    """Run 'graphify update <root>' when the CLI is on PATH."""
    executable = shutil.which("graphify")
    if not executable:
        return False, "graphify CLI not on PATH"
    try:
        proc = subprocess.run([executable, "update", str(project_root)], capture_output=True,
                              text=True, timeout=GRAPHIFY_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    tail = (proc.stdout + proc.stderr).strip().splitlines()
    return proc.returncode == 0, (tail[-1] if tail else f"exit {proc.returncode}")


# ---------------------------------------------------------------- operations

def _resolve_target(registry_data: dict, target: str) -> tuple[dict | None, str, Path | None]:
    """(registry_entry_or_None, project_id, root_or_None) from a directory or an id."""
    import manifest as manifest_mod  # noqa: PLC0415
    import registry as registry_mod  # noqa: PLC0415

    candidate = Path(target)
    if (candidate / ".amir" / "project.yaml").is_file():
        root = candidate.resolve()
        data = manifest_mod.load_manifest(root)
        project_id = (data.get("project") or {}).get("id")
        if not project_id:
            raise AmirError(f"{root} has no project.id in .amir/project.yaml")
        entry = registry_mod.find_entry(registry_data, str(project_id))
        return entry, str(project_id), root
    entry = registry_mod.find_entry(registry_data, target)
    if entry is None:
        raise AmirError(f"'{target}' is neither a project directory (with .amir/project.yaml) "
                        "nor a registered project id")
    return entry, entry["id"], Path(entry["root"]) if entry.get("root") else None


def add(project_dir: str | Path, home: Path | None = None) -> dict:
    """Register (or refresh) a project and merge its local graph into the global graph.

    Honest reporting: when graphify is disabled or no local graph exists, only registry
    metadata is recorded and the report says so (graph_merged=False + reason)."""
    import manifest as manifest_mod  # noqa: PLC0415
    import registry as registry_mod  # noqa: PLC0415

    root = Path(project_dir).resolve()
    if not root.is_dir():
        raise AmirError(f"project directory does not exist: {root}")
    data = manifest_mod.load_manifest(root)
    entry = registry_mod.entry_from_sources(root, data)
    project_id = entry["id"]
    registry_data = registry_mod.upsert_project(registry_mod.load_registry(home), entry)
    local = registry_mod.local_graph_path(root, data)
    report = {"id": project_id, "root": str(root), "registered": True,
              "graph_enabled": entry["graph_enabled"], "graph_merged": False,
              "node_count": 0, "edge_count": 0, "reason": None}
    if not entry["graph_enabled"]:
        report["reason"] = "graphify is not enabled in .amir/project.yaml; registered metadata only"
    elif not local.is_file():
        report["reason"] = (f"no local graph at {local}; registered metadata only "
                            "(run 'graphify update .' inside the project, then re-add)")
    else:
        marker = registry_mod.commit_marker(registry_mod.git_info(root))
        nodes_n, links_n = merge_project_graph(home, project_id, local, marker)
        refreshed = {**entry, "last_graph_update": utc_now_iso(),
                     "graph_source_commit": marker, "graph_path": str(local)}
        registry_data = registry_mod.upsert_project(registry_data, refreshed)
        report.update({"graph_merged": True, "node_count": nodes_n, "edge_count": links_n})
    registry_mod.save_registry(registry_data, home)
    return report


def remove(target: str, home: Path | None = None, keep_registry: bool = False,
           remove_local_graph: bool = False) -> dict:
    """Strip the project's namespace from the global graph; archive + drop its registry
    entry (unless keep_registry). NEVER touches project sources; the local graph is
    preserved unless remove_local_graph is explicitly passed."""
    import registry as registry_mod  # noqa: PLC0415

    registry_data = registry_mod.load_registry(home)
    entry, project_id, root = _resolve_target(registry_data, target)
    report = {"id": project_id, "graph_removed": False, "registry_removed": False,
              "registry_archived": False, "local_graph_removed": False}
    metadata = load_metadata(home)
    if project_id in metadata["projects"] or project_id in graph_namespaces(load_global(home)):
        stripped = strip_namespace(load_global(home), project_id)
        metadata = {**metadata, "projects": {k: v for k, v in metadata["projects"].items()
                                             if k != project_id}}
        _write_global_state(home, stripped, metadata)
        report["graph_removed"] = True
    if entry is not None and not keep_registry:
        registry_mod.archive_entry(entry, home)
        registry_mod.save_registry(registry_mod.remove_project(registry_data, project_id), home)
        report["registry_archived"] = report["registry_removed"] = True
    if remove_local_graph:
        local = Path(entry["graph_path"]) if entry and entry.get("graph_path") else (
            (root / "graphify-out" / "graph.json") if root else None)
        if local and local.is_file():
            local.unlink()
            report["local_graph_removed"] = True
    return report


def update(target: str, home: Path | None = None, graphify_runner=None) -> dict:
    """Refresh registry fields from sources; refresh + re-merge the local graph only when
    stale. The report distinguishes metadata-only refreshes from graph refreshes -- a
    project is never reported as graph-updated when only registry metadata changed."""
    import manifest as manifest_mod  # noqa: PLC0415
    import registry as registry_mod  # noqa: PLC0415

    registry_data = registry_mod.load_registry(home)
    entry, project_id, _root = _resolve_target(registry_data, target)
    if entry is None:
        raise AmirError(f"'{target}' is not registered; run portfolio-add first")
    root = Path(entry["root"])
    report = {"id": project_id, "status": "no-change", "registry_refreshed": False,
              "registry_changes": [], "graph_refreshed": False, "graph_stale_reason": None,
              "error": None}
    if not root.is_dir():
        report.update(status="error", error=f"project root missing: {root}")
        return report
    data = manifest_mod.load_manifest(root)
    fresh = registry_mod.entry_from_sources(root, data)
    changes = [field for field in registry_mod.REGISTRY_FIELDS
               if field not in registry_mod.PORTFOLIO_OWNED_FIELDS
               and fresh.get(field) != entry.get(field)]
    fresh, report = _refresh_graph_if_stale(home, root, project_id, data, entry, fresh,
                                            report, graphify_runner)
    if changes or report["graph_refreshed"]:
        registry_data = registry_mod.upsert_project(registry_data, fresh)
        registry_mod.save_registry(registry_data, home)
    report["registry_refreshed"] = bool(changes)
    report["registry_changes"] = changes
    if report["error"]:
        report["status"] = "error"
    elif report["graph_refreshed"]:
        report["status"] = "graph-refreshed"
    elif changes:
        report["status"] = "metadata-refreshed"
    return report


def _refresh_graph_if_stale(home, root: Path, project_id: str, manifest_data: dict,
                            entry: dict, fresh: dict, report: dict,
                            graphify_runner) -> tuple[dict, dict]:
    """Regenerate (via graphify) and re-merge the namespace only when actually stale.
    A failed regeneration keeps the previous valid global graph untouched."""
    import registry as registry_mod  # noqa: PLC0415

    if not fresh["graph_enabled"]:
        return fresh, report
    local = registry_mod.local_graph_path(root, manifest_data)
    output_dir = registry_mod.graphify_config(manifest_data).get("output_directory") or "graphify-out"
    metadata = load_metadata(home)
    recorded = (metadata["projects"].get(project_id) or {}).get("source_commit")
    stale, reason = graph_staleness(root, local, recorded, output_dir)
    report["graph_stale_reason"] = reason
    if stale:
        runner = default_graphify_runner if graphify_runner is None else graphify_runner
        ok, message = runner(root)
        if not ok:
            report["error"] = (f"graphify update failed ({message}); previous global graph "
                               "left unchanged")
            return fresh, report
        if not local.is_file():
            report["error"] = (f"graphify update reported success but produced no graph at "
                               f"{local}; global graph left unchanged")
            return fresh, report
    if stale or _namespace_out_of_date(metadata, project_id, local):
        marker = registry_mod.commit_marker(registry_mod.git_info(root))
        nodes_n, links_n = merge_project_graph(home, project_id, local, marker)
        fresh = {**fresh, "last_graph_update": utc_now_iso(), "graph_source_commit": marker,
                 "graph_path": str(local)}
        report.update(graph_refreshed=True, node_count=nodes_n, edge_count=links_n)
    return fresh, report


def update_all(home: Path | None = None, graphify_runner=None) -> dict:
    """Update every registered project under the portfolio lock (stale after 30 minutes).
    Per-project failures are isolated; the overall status is honest: any failure means
    'partial' (or 'failed' when nothing succeeded), never 'ok'."""
    import registry as registry_mod  # noqa: PLC0415

    lock = acquire_lock_file(portfolio_lock_path(home), PORTFOLIO_LOCK_STALE_SECONDS)
    try:
        registry_data = registry_mod.load_registry(home)
        results = []
        for entry in sorted(registry_data["projects"], key=lambda p: p.get("id") or ""):
            try:
                results.append(update(entry["id"], home, graphify_runner))
            except AmirError as exc:
                results.append({"id": entry.get("id"), "status": "error", "error": str(exc)})
        failed = sum(1 for r in results if r.get("status") == "error")
        if failed == 0:
            overall = "ok"
        else:
            overall = "failed" if failed == len(results) else "partial"
        return {"status": overall, "total": len(results), "failed": failed, "results": results}
    finally:
        release_lock_file(lock)


def status(home: Path | None = None) -> dict:
    """Registry health + graph freshness overview (read-only)."""
    import registry as registry_mod  # noqa: PLC0415

    registry_data = registry_mod.load_registry(home)
    metadata = load_metadata(home)
    graph = load_global(home)
    projects, missing = [], 0
    now = datetime.now(timezone.utc).timestamp()
    for entry in sorted(registry_data["projects"], key=lambda p: p.get("id") or ""):
        root = Path(entry.get("root") or "")
        reachable = root.is_dir()
        missing += 0 if reachable else 1
        projects.append({**entry, "reachable": reachable,
                         "graph_state": _graph_state(entry, metadata, reachable),
                         "needs_status_update": _needs_status_update(entry, now)})
    return {"registered": len(projects), "reachable": len(projects) - missing,
            "missing": missing, "global_nodes": len(graph.get("nodes", [])),
            "global_links": len(graph.get("links", [])),
            "namespaces": sorted(metadata["projects"]),
            "last_global_update": metadata.get("updated_at"), "projects": projects}


def _graph_state(entry: dict, metadata: dict, reachable: bool) -> str:
    if not entry.get("graph_enabled"):
        return "disabled"
    if not reachable:
        return "unknown (root missing)"
    root = Path(entry["root"])
    local = Path(entry.get("graph_path") or (root / "graphify-out" / "graph.json"))
    recorded = (metadata["projects"].get(entry["id"]) or {}).get("source_commit")
    stale, reason = graph_staleness(root, local, recorded)
    if stale:
        return f"stale ({reason})"
    return "fresh" if entry["id"] in metadata["projects"] else "fresh (not merged)"


def _needs_status_update(entry: dict, now_epoch: float) -> bool:
    last = _parse_iso(entry.get("last_status_update"))
    return last is None or (now_epoch - last) > STALE_STATUS_DAYS * 86400


def rebuild(home: Path | None = None) -> dict:
    """Full re-merge of the global graph from every registered project's local graph
    (previous global graph is backed up first)."""
    import registry as registry_mod  # noqa: PLC0415

    registry_data = registry_mod.load_registry(home)
    graph, metadata_projects, results = empty_graph(), {}, []
    for entry in sorted(registry_data["projects"], key=lambda p: p.get("id") or ""):
        project_id = entry["id"]
        root = Path(entry.get("root") or "")
        local = Path(entry.get("graph_path") or (root / "graphify-out" / "graph.json"))
        if not entry.get("graph_enabled"):
            results.append({"id": project_id, "merged": False, "reason": "graphify disabled"})
            continue
        if not local.is_file():
            results.append({"id": project_id, "merged": False, "reason": f"no local graph: {local}"})
            continue
        try:
            nodes, links = namespace_graph(_load_local_graph(local), project_id)
        except AmirError as exc:
            results.append({"id": project_id, "merged": False, "reason": str(exc)})
            continue
        graph["nodes"].extend(nodes)
        graph["links"].extend(links)
        marker = registry_mod.commit_marker(registry_mod.git_info(root)) if root.is_dir() else None
        metadata_projects[project_id] = {
            "id": project_id, "namespace": project_id, "source_commit": marker or "unknown",
            "node_count": len(nodes), "edge_count": len(links), "updated_at": utc_now_iso()}
        results.append({"id": project_id, "merged": True,
                        "node_count": len(nodes), "edge_count": len(links)})
    _write_global_state(home, graph, {"schema_version": 1, "projects": metadata_projects})
    return {"projects": results, "node_count": len(graph["nodes"]),
            "edge_count": len(graph["links"])}


# ---------------------------------------------------------------- validate

def validate(home: Path | None = None, catalog_root: Path | None = None) -> list[dict]:
    """Consistency + hygiene issues as [{level, code, message}] (report-only, never fixes)."""
    import registry as registry_mod  # noqa: PLC0415
    from util import default_catalog_root  # noqa: PLC0415

    issues: list[dict] = []
    try:
        registry_data = registry_mod.load_registry(home)
    except AmirError as exc:
        return [{"level": "error", "code": "registry-unreadable", "message": str(exc)}]
    for message in registry_mod.validate_registry_data(
            registry_data, catalog_root or default_catalog_root()):
        issues.append({"level": "error", "code": "registry-schema", "message": message})
    issues += _check_unique_ids(registry_data)
    metadata = load_metadata(home)
    graph = load_global(home)
    for entry in registry_data["projects"]:
        issues += _check_project(entry, metadata)
    issues += _check_graph_consistency(registry_data, metadata, graph)
    issues += _scan_secrets(home)
    return issues


def _check_unique_ids(registry_data: dict) -> list[dict]:
    seen, issues = {}, []
    for entry in registry_data["projects"]:
        project_id = entry.get("id")
        if project_id in seen:
            issues.append({"level": "error", "code": "duplicate-id",
                           "message": f"project id '{project_id}' appears more than once"})
        seen[project_id] = True
    return issues


def _check_project(entry: dict, metadata: dict) -> list[dict]:
    import manifest as manifest_mod  # noqa: PLC0415
    import registry as registry_mod  # noqa: PLC0415

    issues = []
    project_id = entry.get("id")
    root = Path(entry.get("root") or "")
    if not root.is_dir():
        return [{"level": "error", "code": "missing-root",
                 "message": f"{project_id}: root does not exist: {root}"}]
    try:
        data = manifest_mod.load_manifest(root)
        manifest_id = (data.get("project") or {}).get("id")
        if str(manifest_id) != str(project_id):
            issues.append({"level": "error", "code": "id-mismatch",
                           "message": f"{project_id}: manifest project.id is '{manifest_id}'"})
    except AmirError as exc:
        issues.append({"level": "error", "code": "invalid-manifest",
                       "message": f"{project_id}: {exc}"})
        return issues
    missing_ai = [name for name in AI_FILES if not (root / ".ai" / name).is_file()]
    if missing_ai:
        issues.append({"level": "info", "code": "missing-ai-files",
                       "message": f"{project_id}: missing .ai files: {', '.join(missing_ai)}"})
    if entry.get("graph_enabled"):
        local = registry_mod.local_graph_path(root, data)
        if not local.is_file():
            issues.append({"level": "warning", "code": "missing-local-graph",
                           "message": f"{project_id}: graphify enabled but no graph at {local}"})
        else:
            recorded = (metadata["projects"].get(project_id) or {}).get("source_commit")
            stale, reason = graph_staleness(root, local, recorded)
            if stale:
                issues.append({"level": "warning", "code": "stale-local-graph",
                               "message": f"{project_id}: local graph is stale ({reason})"})
    return issues


def _check_graph_consistency(registry_data: dict, metadata: dict, graph: dict) -> list[dict]:
    issues = []
    registered_ids = {entry.get("id") for entry in registry_data["projects"]}
    actual_nodes: dict[str, int] = {}
    seen_node_ids: set[str] = set()
    for node in graph.get("nodes", []):
        node_id = str(node.get("id", ""))
        if node_id in seen_node_ids:
            issues.append({"level": "error", "code": "duplicate-node",
                           "message": f"duplicate node id in global graph: {node_id}"})
        seen_node_ids.add(node_id)
        if NAMESPACE_SEP in node_id:
            namespace = node_id.split(NAMESPACE_SEP, 1)[0]
            actual_nodes[namespace] = actual_nodes.get(namespace, 0) + 1
        else:
            issues.append({"level": "warning", "code": "unnamespaced-node",
                           "message": f"global graph node without namespace: {node_id}"})
    for namespace, block in metadata["projects"].items():
        actual = actual_nodes.get(namespace, 0)
        if actual != block.get("node_count"):
            issues.append({"level": "error", "code": "namespace-count-mismatch",
                           "message": f"{namespace}: metadata records {block.get('node_count')} "
                                      f"nodes but the global graph has {actual}"})
        if namespace not in registered_ids:
            issues.append({"level": "warning", "code": "unregistered-namespace",
                           "message": f"namespace '{namespace}' is in the global graph but not "
                                      "in the registry"})
    for namespace in actual_nodes:
        if namespace not in metadata["projects"]:
            issues.append({"level": "error", "code": "orphaned-namespace",
                           "message": f"namespace '{namespace}' has nodes in the global graph "
                                      "but no graph-metadata entry"})
    return issues


def _scan_secrets(home: Path | None = None) -> list[dict]:
    """Report-only regex sweep of global-graph.json; matched VALUES are never echoed."""
    path = global_graph_path(home)
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = []
    for name, pattern in SECRET_PATTERNS:
        count = len(pattern.findall(text))
        if count:
            issues.append({"level": "error", "code": "secret-leak",
                           "message": f"pattern '{name}' matched {count} time(s) in "
                                      "global-graph.json (values not shown); scrub the source "
                                      "project and rebuild"})
    return issues
