"""amirctl -- deterministic CLI for the amir marketplace tooling.

Usage: python amirctl.py <subcommand> [options]

Subcommands:
  validate [--json]                 run all project checks (manifest, lock, naming, hosts, ...)
  generate [--dry-run]              render host outputs from the manifest selection
  lock                              (re)build .amir/components.lock.json from the selection
  drift                             report lock-vs-source drift without changing anything
  repair                            re-render generated files and refresh the lock (never changes selections)
  registry-list                     list registered projects with health status
  registry-add                      register/refresh the current project in the user registry
  registry-remove <id>              remove a project from the registry
  registry-repair [--prune]         report stale registry entries; --prune drops missing roots
  portfolio-add <dir>               register a project + merge its graphify graph globally
  portfolio-remove <dir|id>         strip its namespace from the global graph
      [--keep-registry | --archive-registry] [--remove-local-graph]
  portfolio-update <dir|id>         refresh registry fields; refresh graph only when stale
  portfolio-update-all              update every registered project (honest partial-failure status)
  portfolio-list [filter]           table view; filters: all active paused archived at-risk
                                    stale graph-stale missing-directory needs-attention
  portfolio-status                  registry health + global graph freshness overview
  portfolio-validate                registry/graph consistency + secret sweep (report only)
  portfolio-rebuild --confirm       full re-merge of the global graph from local graphs
  portfolio-report                  write the 5 portfolio reports to %USERPROFILE%\\.amir\\portfolio\\reports

The unified registry lives at %USERPROFILE%\\.amir\\registry\\projects.yaml (ONE registry
for registry-* and portfolio-*; a legacy projects.json is migrated on first use).
PowerShell 5.1 example:  python amirctl.py portfolio-add "C:\\path\\to\\project"
  catalog-list [--json]             list catalog components
  catalog-resolve <ids...>          run activation-rule resolution for a component set
  remove-project-config [--apply]   plan (default) or apply removal of Amir-managed files only
  doctor                            environment/self health checks
  migrate                           detect legacy installs and print a migration plan (plan only)

Works from any cwd: the project root is the nearest ancestor containing .amir/project.yaml,
or pass --project PATH. The catalog repo defaults to this file's marketplace checkout, or
%USERPROFILE%\\.amir\\config.json {"catalog_root": ...}, or --catalog PATH.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from util import AmirError, dump_json, read_json, utc_now_iso, write_text  # noqa: E402

VERSION = "1.0.0"


def _catalog_root(args) -> Path:
    import catalog as catalog_mod  # noqa: PLC0415, F401
    from util import default_catalog_root  # noqa: PLC0415

    if getattr(args, "catalog", None):
        return Path(args.catalog).resolve()
    root = default_catalog_root()
    if (root / "catalog" / "catalog.json").is_file():
        return root
    config = Path.home() / ".amir" / "config.json"
    if config.is_file():
        configured = Path(read_json(config).get("catalog_root", ""))
        if (configured / "catalog" / "catalog.json").is_file():
            return configured
    raise AmirError("cannot locate the catalog repo; pass --catalog PATH or set catalog_root in "
                    "%USERPROFILE%\\.amir\\config.json")


def _project_root(args, required: bool = True) -> Path | None:
    from util import find_project_root  # noqa: PLC0415

    root = find_project_root(explicit=getattr(args, "project", None))
    if root is None and required:
        raise AmirError("no project found: no .amir/project.yaml in this directory or any ancestor "
                        "(use --project PATH, or /amir:create_project to make one)")
    return root


def _load_project(args):
    import catalog as catalog_mod  # noqa: PLC0415
    import manifest as manifest_mod  # noqa: PLC0415

    catalog_root = _catalog_root(args)
    project_root = _project_root(args)
    cat = catalog_mod.load_catalog(catalog_root)
    data = manifest_mod.load_manifest(project_root)
    return project_root, catalog_root, cat, data


def _load_project_gated(args, require_resolution: bool = True):
    """Load the project, refusing (before any write) on schema errors or blocked activation.

    The resolution gate maps the FULL effective selection -- plugins.amir_project.components,
    every enabled project_tools entry, and system_capabilities grants -- through the same
    resolver as catalog-resolve, with the manifest permissions block as granted permissions.
    """
    import catalog as catalog_mod  # noqa: PLC0415
    import manifest as manifest_mod  # noqa: PLC0415

    catalog_root = _catalog_root(args)
    project_root = _project_root(args)
    cat = catalog_mod.load_catalog(catalog_root)
    data, errors = manifest_mod.validate_manifest_file(project_root, catalog_root)
    if errors:
        raise AmirError("manifest failed schema validation; refusing to proceed (no files written):\n  "
                        + "\n  ".join(errors))
    if require_resolution:
        selection = manifest_mod.selected_component_ids(data)
        result = catalog_mod.resolve(cat, selection, manifest_mod.host_matrix(data),
                                     manifest_mod.granted_permissions(data))
        if not result.ok:
            blocked = "\n".join(f"BLOCKED [{i.rule}] {i.message}" for i in result.issues)
            raise AmirError("component selection cannot be activated; refusing to render "
                            f"(no files written):\n{blocked}")
    return project_root, catalog_root, cat, data


def cmd_validate(args) -> int:
    import validator  # noqa: PLC0415

    catalog_root = _catalog_root(args)
    project_root = _project_root(args)
    checks = validator.run_checks(project_root, catalog_root)
    print(validator.to_json(checks) if args.json else validator.format_table(checks), end="")
    if not args.json:
        print()
    return 0 if all(c.status != "error" for c in checks) else 1


def cmd_generate(args) -> int:
    import lockfile  # noqa: PLC0415
    import renderer  # noqa: PLC0415

    project_root, catalog_root, cat, data = _load_project_gated(args)
    plan, actions = renderer.render(project_root, data, cat, catalog_root, dry_run=args.dry_run)
    print(renderer.format_plan(plan, actions, args.dry_run))
    if not args.dry_run and not (project_root / lockfile.LOCK_RELPATH).is_file():
        print("hint: no .amir/components.lock.json yet -- run 'amirctl lock' "
              "to pin source checksums (validate reports an error until then)")
    return 0


def cmd_lock(args) -> int:
    import lockfile  # noqa: PLC0415
    import manifest as manifest_mod  # noqa: PLC0415

    project_root, catalog_root, cat, data = _load_project_gated(args, require_resolution=False)
    selection = manifest_mod.selected_component_ids(data)
    lock = lockfile.build_lock(catalog_root, cat, selection)
    path = lockfile.write_lock(project_root, lock)
    total = sum(len(c["files"]) for c in lock["components"].values())
    print(f"wrote {path}: {len(lock['components'])} component(s), {total} file checksum(s)")
    return 0


def cmd_drift(args) -> int:
    import lockfile  # noqa: PLC0415

    project_root, catalog_root, cat, _data = _load_project(args)
    lock = lockfile.load_lock(project_root)
    drift = lockfile.verify_lock(catalog_root, cat, lock)
    if not drift:
        print("no drift: all locked component sources match their checksums")
        return 0
    for cid, info in sorted(drift.items()):
        print(f"{cid}:")
        for kind in ("changed", "missing", "added"):
            for rel in info.get(kind, []):
                print(f"  {kind}: {rel}")
        if info.get("note"):
            print(f"  note: {info['note']}")
    print("\nrun 'amirctl repair' (or /amir:repair_project) to regenerate outputs and refresh the lock")
    return 1


def cmd_repair(args) -> int:
    """Fix drift and missing generated files only -- never changes selections."""
    import lockfile  # noqa: PLC0415
    import manifest as manifest_mod  # noqa: PLC0415
    import renderer  # noqa: PLC0415

    project_root, catalog_root, cat, data = _load_project_gated(args)
    plan, actions = renderer.render(project_root, data, cat, catalog_root, dry_run=False)
    selection = manifest_mod.selected_component_ids(data)
    lockfile.write_lock(project_root, lockfile.build_lock(catalog_root, cat, selection))
    print(renderer.format_plan(plan, actions, dry_run=False))
    print("lock refreshed from current sources")
    return 0


def cmd_registry_list(args) -> int:
    import registry  # noqa: PLC0415

    report = registry.inspect(registry.load_registry())
    if not report:
        print("no projects registered")
        return 0
    for entry in report:
        print(f"{entry.get('id', '?'):24} {entry.get('status', '?'):14} {entry.get('root', '')}")
    return 0


def cmd_registry_add(args) -> int:
    import manifest as manifest_mod  # noqa: PLC0415
    import registry  # noqa: PLC0415

    project_root = _project_root(args)
    data = manifest_mod.load_manifest(project_root)
    entry = registry.entry_from_manifest(data, project_root)
    path = registry.save_registry(registry.upsert_project(registry.load_registry(), entry))
    print(f"registered '{entry['id']}' ({entry['root']}) in {path}")
    return 0


def cmd_registry_remove(args) -> int:
    import registry  # noqa: PLC0415

    path = registry.save_registry(registry.remove_project(registry.load_registry(), args.id))
    print(f"removed '{args.id}' from {path}")
    return 0


def cmd_registry_repair(args) -> int:
    import registry  # noqa: PLC0415

    reg, report = registry.repair(registry.load_registry(), prune=args.prune)
    for entry in report:
        print(f"{entry.get('id', '?'):24} {entry.get('status', '?')}")
    if args.prune:
        registry.save_registry(reg)
        dropped = sum(1 for entry in report if entry["status"] != "ok")
        print(f"pruned {dropped} stale entr{'y' if dropped == 1 else 'ies'}")
    return 0


def cmd_portfolio_add(args) -> int:
    import portfolio  # noqa: PLC0415

    report = portfolio.add(args.dir)
    print(f"registered '{report['id']}' ({report['root']})")
    if report["graph_merged"]:
        print(f"graph merged: {report['node_count']} node(s), {report['edge_count']} edge(s) "
              f"under namespace '{report['id']}::'")
    else:
        print(f"graph NOT merged: {report['reason']}")
    return 0


def cmd_portfolio_remove(args) -> int:
    import portfolio  # noqa: PLC0415

    report = portfolio.remove(args.target, keep_registry=args.keep_registry,
                              remove_local_graph=args.remove_local_graph)
    print(f"'{report['id']}': "
          f"global-graph namespace {'removed' if report['graph_removed'] else 'not present'}; "
          f"registry entry {'archived + removed' if report['registry_removed'] else 'kept'}; "
          f"local graph {'REMOVED' if report['local_graph_removed'] else 'preserved'}")
    print("project source files were not touched")
    return 0


def _print_update_report(report: dict) -> None:
    if report.get("status") == "error":
        print(f"{report['id']}: ERROR -- {report.get('error')}")
    elif report.get("graph_refreshed"):
        print(f"{report['id']}: graph refreshed ({report.get('node_count', '?')} nodes; "
              f"stale reason: {report.get('graph_stale_reason')}) "
              + ("+ registry metadata" if report.get("registry_refreshed") else ""))
    elif report.get("registry_refreshed"):
        print(f"{report['id']}: registry metadata refreshed only "
              f"({', '.join(report['registry_changes'])}); graph unchanged")
    else:
        print(f"{report['id']}: no change")


def cmd_portfolio_update(args) -> int:
    import portfolio  # noqa: PLC0415

    report = portfolio.update(args.target)
    _print_update_report(report)
    return 0 if report.get("status") != "error" else 1


def cmd_portfolio_update_all(args) -> int:
    import portfolio  # noqa: PLC0415

    result = portfolio.update_all()
    for report in result["results"]:
        _print_update_report(report)
    print(f"\noverall: {result['status']} ({result['total'] - result['failed']}/"
          f"{result['total']} succeeded)")
    return 0 if result["status"] == "ok" else 1


def cmd_portfolio_status(args) -> int:
    import portfolio  # noqa: PLC0415

    overview = portfolio.status()
    print(f"registered: {overview['registered']}  reachable: {overview['reachable']}  "
          f"missing: {overview['missing']}")
    print(f"global graph: {overview['global_nodes']} nodes, {overview['global_links']} edges, "
          f"{len(overview['namespaces'])} namespace(s)")
    print(f"last global update: {overview['last_global_update'] or '-'}")
    for project in overview["projects"]:
        flags = []
        if not project["reachable"]:
            flags.append("MISSING-DIR")
        if project["needs_status_update"]:
            flags.append("needs-status-update")
        print(f"  {project['id']:24} graph={project['graph_state']:22} "
              f"last-status={(project.get('last_status_update') or '-'):20} "
              + (" ".join(flags)))
    return 0


PORTFOLIO_FILTERS = ("all", "active", "paused", "archived", "at-risk", "stale",
                     "graph-stale", "missing-directory", "needs-attention")


def _portfolio_filter(project: dict, name: str) -> bool:
    stale = project.get("needs_status_update", False)
    graph_stale = str(project.get("graph_state", "")).startswith(("stale", "unknown"))
    missing = not project.get("reachable", False)
    at_risk = project.get("health") in ("at-risk", "blocked")
    return {
        "all": True,
        "active": project.get("lifecycle") == "active",
        "paused": project.get("lifecycle") == "paused",
        "archived": project.get("lifecycle") == "archived",
        "at-risk": at_risk,
        "stale": stale,
        "graph-stale": graph_stale,
        "missing-directory": missing,
        "needs-attention": at_risk or stale or graph_stale or missing,
    }[name]


def cmd_portfolio_list(args) -> int:
    import portfolio  # noqa: PLC0415

    overview = portfolio.status()
    rows = [p for p in overview["projects"] if _portfolio_filter(p, args.filter)]
    if not rows:
        print(f"no projects match filter '{args.filter}'")
        return 0
    fmt = "{:24} {:9} {:7} {:8} {:16} {:>5} {:>5} {:20} {:20}"
    print(fmt.format("ID", "LIFECYCLE", "PRIO", "HEALTH", "PHASE", "CONF%", "EST%",
                     "GRAPH", "LAST-STATUS"))
    for p in rows:
        print(fmt.format(p["id"][:24], str(p.get("lifecycle") or "-"),
                         str(p.get("priority") or "-"), str(p.get("health") or "-"),
                         str(p.get("current_phase") or "-")[:16],
                         "-" if p.get("confirmed_progress") is None else str(p["confirmed_progress"]),
                         "-" if p.get("estimated_progress") is None else str(p["estimated_progress"]),
                         str(p.get("graph_state") or "-")[:20],
                         str(p.get("last_status_update") or "-")))
    return 0


def cmd_portfolio_validate(args) -> int:
    import portfolio  # noqa: PLC0415

    issues = portfolio.validate()
    if not issues:
        print("portfolio validate: OK (no issues)")
        return 0
    for issue in issues:
        print(f"{issue['level'].upper():8} [{issue['code']}] {issue['message']}")
    errors = sum(1 for issue in issues if issue["level"] == "error")
    print(f"\n{len(issues)} issue(s): {errors} error(s)")
    return 1 if errors else 0


def cmd_portfolio_rebuild(args) -> int:
    import portfolio  # noqa: PLC0415

    if not args.confirm:
        print("portfolio-rebuild replaces the global graph from all local graphs "
              "(a backup is taken first). Re-run with --confirm to proceed.")
        return 1
    result = portfolio.rebuild()
    for project in result["projects"]:
        if project["merged"]:
            print(f"  merged {project['id']}: {project['node_count']} nodes, "
                  f"{project['edge_count']} edges")
        else:
            print(f"  skipped {project['id']}: {project['reason']}")
    print(f"rebuilt global graph: {result['node_count']} nodes, {result['edge_count']} edges")
    return 0


def cmd_portfolio_report(args) -> int:
    import portfolio_reports  # noqa: PLC0415

    for path in portfolio_reports.write_reports():
        print(f"wrote {path}")
    return 0


def cmd_catalog_list(args) -> int:
    import catalog as catalog_mod  # noqa: PLC0415

    cat = catalog_mod.load_catalog(_catalog_root(args))
    if args.json:
        print(dump_json(cat), end="")
        return 0
    for component in sorted(cat["components"], key=lambda c: (c["plugin"], c["id"])):
        commands = len(component.get("commands", []))
        print(f"{component['plugin']:13} {component['id']:14} v{component['version']}  "
              f"{commands:3} cmd  {component['description'][:70]}")
    return 0


def cmd_catalog_resolve(args) -> int:
    import catalog as catalog_mod  # noqa: PLC0415

    cat = catalog_mod.load_catalog(_catalog_root(args))
    host_matrix = {"claude-code": {"enabled": True, "version": None},
                   "cursor": {"enabled": True, "version": None}}
    result = catalog_mod.resolve(cat, args.ids, host_matrix, None)
    if result.ok:
        print("resolution OK; activation order: " + ", ".join(result.components))
        return 0
    for issue in result.issues:
        print(f"BLOCKED [{issue.rule}] {issue.message}")
    return 1


def _removal_plan(project_root: Path) -> list[Path]:
    from util import is_amir_generated_text  # noqa: PLC0415

    targets: list[Path] = []
    amir_dir = project_root / ".amir"
    if amir_dir.is_dir():
        targets.extend(sorted(p for p in amir_dir.rglob("*") if p.is_file()))
    for pattern, folder in (("amir_*.md", "commands"), ("amir_*.mdc", "rules")):
        directory = project_root / ".cursor" / folder
        if directory.is_dir():
            targets.extend(p for p in sorted(directory.glob(pattern)) if is_amir_generated_text(p))
    return targets


def cmd_remove_project_config(args) -> int:
    from util import GENERATED_MARKER_KEY  # noqa: PLC0415

    project_root = _project_root(args)
    targets = _removal_plan(project_root)
    mcp_path = project_root / ".cursor" / "mcp.json"
    mcp_amir = []
    if mcp_path.is_file():
        try:
            servers = read_json(mcp_path).get("mcpServers") or {}
            mcp_amir = sorted(name for name, config in servers.items()
                              if isinstance(config, dict) and GENERATED_MARKER_KEY in config)
        except AmirError:
            pass
    print(f"removal plan for {project_root} (Amir-managed files ONLY; user files are preserved):")
    for target in targets:
        print(f"  delete {target.relative_to(project_root).as_posix()}")
    for name in mcp_amir:
        print(f"  remove mcp entry '{name}' from .cursor/mcp.json (other entries preserved)")
    print("  remove registry entry for this project")
    if not args.apply:
        print("\nplan only -- re-run with --apply to execute (a backup is taken first)")
        return 0

    backup_root = project_root / f".amir-removed-backup-{utc_now_iso().replace(':', '')}"
    for target in targets:
        rel = target.relative_to(project_root)
        destination = backup_root / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, destination)
        target.unlink()
    for directory in (project_root / ".amir", project_root / ".cursor" / "commands",
                      project_root / ".cursor" / "rules"):
        if directory.is_dir() and not any(directory.rglob("*")):
            shutil.rmtree(directory, ignore_errors=True)
    if mcp_amir:
        data = read_json(mcp_path)
        shutil.copy2(mcp_path, backup_root / "mcp.json") if backup_root.is_dir() else None
        data["mcpServers"] = {name: config for name, config in (data.get("mcpServers") or {}).items()
                              if not (isinstance(config, dict) and GENERATED_MARKER_KEY in config)}
        write_text(mcp_path, dump_json(data))
    try:
        import manifest as manifest_mod  # noqa: PLC0415, F401
        import registry  # noqa: PLC0415

        reg = registry.load_registry()
        ids = [p["id"] for p in reg.get("projects", [])
               if Path(p.get("root", "")) == project_root.resolve()]
        for project_id in ids:
            reg = registry.remove_project(reg, project_id)
        registry.save_registry(reg)
    except AmirError:
        pass
    print(f"\nremoved {len(targets)} file(s); backup at {backup_root}")
    return 0


def cmd_doctor(args) -> int:
    import catalog as catalog_mod  # noqa: PLC0415
    import validator  # noqa: PLC0415
    from util import require_jsonschema, require_yaml  # noqa: PLC0415

    ok = True
    print(f"amirctl {VERSION}  python {sys.version.split()[0]}")
    require_yaml(), require_jsonschema()
    print("deps: pyyaml + jsonschema importable")
    try:
        catalog_root = _catalog_root(args)
        cat = catalog_mod.load_catalog(catalog_root)
        print(f"catalog: {catalog_root} -- {len(cat['components'])} components, schema OK")
        duplicates = validator.find_duplicate_commands(cat)
        if duplicates:
            ok = False
            print("ERROR duplicate commands: " + ", ".join(sorted(duplicates)))
        else:
            print("commands: no duplicates across amir_system + amir_project")
        for name in (".claude-plugin/marketplace.json", ".cursor-plugin/marketplace.json",
                     ".agents/plugins/marketplace.json"):
            try:
                doc = read_json(catalog_root / name)
                plugins = sorted(p.get("name", "?") for p in doc.get("plugins", []))
                good = plugins == ["amir_project", "amir_system"]
                ok = ok and good
                print(("marketplace OK: " if good else "ERROR marketplace: ") + f"{name} -> {plugins}")
            except AmirError as exc:
                ok = False
                print(f"ERROR marketplace {name}: {exc}")
    except AmirError as exc:
        ok = False
        print(f"ERROR catalog: {exc}")
    print("graphify CLI: " + (shutil.which("graphify") or "not on PATH (only needed when enabled)"))
    from util import find_project_root  # noqa: PLC0415

    root = find_project_root(explicit=getattr(args, "project", None))
    print(f"project: {root if root else 'none detected from cwd (fine outside projects)'}")
    print("doctor: " + ("OK" if ok else "PROBLEMS FOUND"))
    return 0 if ok else 1


def cmd_migrate(args) -> int:
    import migrate  # noqa: PLC0415

    print(migrate.format_plan(migrate.detect_legacy()))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="amirctl", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=f"amirctl {VERSION}")
    parser.add_argument("--project", help="project root (default: nearest ancestor with .amir/project.yaml)")
    parser.add_argument("--catalog", help="catalog repo root (default: this checkout or ~/.amir/config.json)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="run all project checks")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_validate)
    p = sub.add_parser("generate", help="render host outputs from the manifest")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_generate)
    sub.add_parser("lock", help="build the components lock").set_defaults(func=cmd_lock)
    sub.add_parser("drift", help="report lock drift").set_defaults(func=cmd_drift)
    sub.add_parser("repair", help="re-render + refresh lock").set_defaults(func=cmd_repair)
    sub.add_parser("registry-list", help="list registered projects").set_defaults(func=cmd_registry_list)
    sub.add_parser("registry-add", help="register the current project").set_defaults(func=cmd_registry_add)
    p = sub.add_parser("registry-remove", help="remove a registry entry")
    p.add_argument("id")
    p.set_defaults(func=cmd_registry_remove)
    p = sub.add_parser("registry-repair", help="report/prune stale registry entries")
    p.add_argument("--prune", action="store_true")
    p.set_defaults(func=cmd_registry_repair)
    p = sub.add_parser("portfolio-add", help="register a project + merge its graph globally")
    p.add_argument("dir", help="project directory (must contain .amir/project.yaml)")
    p.set_defaults(func=cmd_portfolio_add)
    p = sub.add_parser("portfolio-remove", help="remove a project's namespace from the global graph")
    p.add_argument("target", help="project directory or registered id")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--keep-registry", action="store_true",
                       help="keep the registry entry (only strip the graph namespace)")
    group.add_argument("--archive-registry", action="store_true",
                       help="archive + remove the registry entry (default behavior)")
    p.add_argument("--remove-local-graph", action="store_true",
                   help="also delete the project's local graphify-out/graph.json")
    p.set_defaults(func=cmd_portfolio_remove)
    p = sub.add_parser("portfolio-update", help="refresh one project (graph only when stale)")
    p.add_argument("target", help="project directory or registered id")
    p.set_defaults(func=cmd_portfolio_update)
    sub.add_parser("portfolio-update-all",
                   help="update every registered project").set_defaults(func=cmd_portfolio_update_all)
    p = sub.add_parser("portfolio-list", help="table of registered projects")
    p.add_argument("filter", nargs="?", default="all", choices=PORTFOLIO_FILTERS)
    p.set_defaults(func=cmd_portfolio_list)
    sub.add_parser("portfolio-status",
                   help="registry + graph freshness overview").set_defaults(func=cmd_portfolio_status)
    sub.add_parser("portfolio-validate",
                   help="consistency + secret sweep (report only)").set_defaults(func=cmd_portfolio_validate)
    p = sub.add_parser("portfolio-rebuild", help="full re-merge of the global graph")
    p.add_argument("--confirm", action="store_true")
    p.set_defaults(func=cmd_portfolio_rebuild)
    sub.add_parser("portfolio-report",
                   help="write the 5 portfolio reports").set_defaults(func=cmd_portfolio_report)
    p = sub.add_parser("catalog-list", help="list catalog components")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_catalog_list)
    p = sub.add_parser("catalog-resolve", help="resolve a component selection")
    p.add_argument("ids", nargs="+")
    p.set_defaults(func=cmd_catalog_resolve)
    p = sub.add_parser("remove-project-config", help="remove Amir-managed files (plan by default)")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--plan", action="store_true", help="show the plan (default)")
    group.add_argument("--apply", action="store_true", help="apply after backup")
    p.set_defaults(func=cmd_remove_project_config)
    sub.add_parser("doctor", help="environment health checks").set_defaults(func=cmd_doctor)
    sub.add_parser("migrate", help="legacy install migration plan").set_defaults(func=cmd_migrate)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except AmirError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
