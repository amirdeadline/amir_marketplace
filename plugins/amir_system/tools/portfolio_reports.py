"""Portfolio report writers: %USERPROFILE%\\.amir\\portfolio\\reports\\*.md.

Content comes from the registry, each project's .ai\\ files, and the graph metadata --
never from secrets. Reports are regenerated wholesale on every run (atomic writes).
"""
from __future__ import annotations

from pathlib import Path

from util import atomic_write_text, utc_now_iso

REPORT_NAMES = ("portfolio-status.md", "portfolio-risks.md", "cross-project-dependencies.md",
                "stale-projects.md", "recent-progress.md")

_MAX_AI_EXCERPT_LINES = 40


def write_reports(home: Path | None = None) -> list[Path]:
    """Write the five portfolio reports; returns the written paths."""
    import portfolio  # noqa: PLC0415
    import registry as registry_mod  # noqa: PLC0415

    overview = portfolio.status(home)
    registry_data = registry_mod.load_registry(home)
    metadata = portfolio.load_metadata(home)
    graph = portfolio.load_global(home)
    target = portfolio.reports_dir(home)
    written = []
    for name, text in (
        ("portfolio-status.md", _status_report(overview, metadata)),
        ("portfolio-risks.md", _risks_report(overview)),
        ("cross-project-dependencies.md", _dependencies_report(registry_data, graph)),
        ("stale-projects.md", _stale_report(overview)),
        ("recent-progress.md", _progress_report(overview)),
    ):
        path = target / name
        atomic_write_text(path, text)
        written.append(path)
    return written


def _header(title: str) -> str:
    return f"# {title}\n\nGenerated: {utc_now_iso()} (by amirctl portfolio-report)\n\n"


def _fmt(value) -> str:
    return "-" if value in (None, "", []) else str(value)


def _status_report(overview: dict, metadata: dict) -> str:
    lines = [_header("Portfolio Status").rstrip(), ""]
    lines.append(f"- Registered projects: {overview['registered']} "
                 f"(reachable {overview['reachable']}, missing {overview['missing']})")
    lines.append(f"- Global graph: {overview['global_nodes']} nodes, "
                 f"{overview['global_links']} edges across "
                 f"{len(overview['namespaces'])} namespace(s)")
    lines.append(f"- Last global graph update: {_fmt(overview['last_global_update'])}")
    lines.append("")
    lines.append("| id | lifecycle | priority | health | phase | conf% | est% | graph | last status |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for project in overview["projects"]:
        lines.append("| " + " | ".join(_fmt(project.get(key)) for key in (
            "id", "lifecycle", "priority", "health", "current_phase", "confirmed_progress",
            "estimated_progress", "graph_state", "last_status_update")) + " |")
    return "\n".join(lines) + "\n"


def _ai_excerpt(root: Path, filename: str) -> str | None:
    path = root / ".ai" / filename
    if not path.is_file():
        return None
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    body = [line for line in lines if line.strip()][:_MAX_AI_EXCERPT_LINES]
    return "\n".join(body) if body else None


def _risks_report(overview: dict) -> str:
    lines = [_header("Portfolio Risks").rstrip(), ""]
    flagged = [p for p in overview["projects"] if p.get("health") in ("at-risk", "blocked")]
    if flagged:
        lines.append("## Health flags")
        for project in flagged:
            lines.append(f"- **{project['id']}**: health={project['health']}, "
                         f"lifecycle={_fmt(project.get('lifecycle'))}")
        lines.append("")
    lines.append("## Per-project risks (.ai/risks.md)")
    for project in overview["projects"]:
        if not project.get("reachable"):
            lines += [f"\n### {project['id']}", "_project root missing; risks unavailable_"]
            continue
        excerpt = _ai_excerpt(Path(project["root"]), "risks.md")
        lines += [f"\n### {project['id']}", excerpt if excerpt else "_no .ai/risks.md content_"]
    return "\n".join(lines) + "\n"


def _dependencies_report(registry_data: dict, graph: dict) -> str:
    import portfolio  # noqa: PLC0415
    import registry as registry_mod  # noqa: PLC0415

    lines = [_header("Cross-Project Dependencies").rstrip(), ""]
    lines.append("## Cross-namespace graph edges")
    cross = []
    for link in graph.get("links", []):
        source, target = str(link.get("source", "")), str(link.get("target", ""))
        sep = portfolio.NAMESPACE_SEP
        if sep in source and sep in target:
            ns_a, ns_b = source.split(sep, 1)[0], target.split(sep, 1)[0]
            if ns_a != ns_b:
                cross.append(f"- `{source}` -> `{target}` ({_fmt(link.get('relation'))})")
    lines += cross if cross else ["_no cross-namespace edges in the global graph_"]
    lines.append("\n## Shared technology (from .amir/portfolio.yaml)")
    tech_map: dict[str, list[str]] = {}
    for entry in registry_data.get("projects", []):
        root = Path(entry.get("root") or "")
        if not root.is_dir():
            continue
        try:
            tech = registry_mod.load_portfolio_yaml(root).get("technology") or {}
        except Exception:  # noqa: BLE001 - report generation must not die on one bad file
            continue
        for group in ("languages", "frameworks", "platforms"):
            for item in tech.get(group) or []:
                tech_map.setdefault(f"{group}:{item}", []).append(entry["id"])
    shared = {key: ids for key, ids in tech_map.items() if len(ids) > 1}
    if shared:
        for key, ids in sorted(shared.items()):
            lines.append(f"- {key}: {', '.join(sorted(ids))}")
    else:
        lines.append("_no shared technology declared across projects_")
    return "\n".join(lines) + "\n"


def _stale_report(overview: dict) -> str:
    lines = [_header("Stale Projects").rstrip(), ""]
    missing = [p for p in overview["projects"] if not p.get("reachable")]
    status_stale = [p for p in overview["projects"] if p.get("needs_status_update")]
    graph_stale = [p for p in overview["projects"]
                   if str(p.get("graph_state", "")).startswith(("stale", "unknown"))]
    for title, group, detail in (
        ("Missing directories", missing, lambda p: p.get("root")),
        ("Status updates overdue (> 14 days or never)", status_stale,
         lambda p: f"last: {_fmt(p.get('last_status_update'))}"),
        ("Graphs stale", graph_stale, lambda p: p.get("graph_state")),
    ):
        lines.append(f"## {title}")
        lines += ([f"- **{p['id']}** -- {detail(p)}" for p in group] or ["_none_"])
        lines.append("")
    return "\n".join(lines) + "\n"


def _progress_report(overview: dict) -> str:
    lines = [_header("Recent Progress").rstrip(), ""]
    ordered = sorted(overview["projects"],
                     key=lambda p: p.get("last_status_update") or "", reverse=True)
    for project in ordered:
        lines.append(f"## {project['id']}")
        lines.append(f"- last status update: {_fmt(project.get('last_status_update'))}")
        lines.append(f"- phase: {_fmt(project.get('current_phase'))}; confirmed "
                     f"{_fmt(project.get('confirmed_progress'))}% / estimated "
                     f"{_fmt(project.get('estimated_progress'))}%")
        accomplishments = _portfolio_status_block(project)
        if accomplishments:
            lines.append("- recent accomplishments:")
            lines += [f"  - {item}" for item in accomplishments]
        lines.append("")
    if not ordered:
        lines.append("_no projects registered_")
    return "\n".join(lines) + "\n"


def _portfolio_status_block(project: dict) -> list[str]:
    import registry as registry_mod  # noqa: PLC0415

    root = Path(project.get("root") or "")
    if not root.is_dir():
        return []
    try:
        block = registry_mod.load_portfolio_yaml(root).get("status") or {}
    except Exception:  # noqa: BLE001
        return []
    return [str(item) for item in block.get("accomplishments") or []][:10]
