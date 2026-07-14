"""Parse asana_tasks.md backlog files and sync to Asana."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from .client import AsanaClient, AsanaError, TASK_OPT_FIELDS

MAIN_TASK_RE = re.compile(r"^### Main task:\s*(.+?)\s*$", re.MULTILINE)
PHASE_RE = re.compile(
    r"\*\*Phase target:\*\*\s*(\d{4}-\d{2}-\d{2})"
    r".*?\*\*Phase status:\*\*\s*(.+?)\s*$",
    re.MULTILINE,
)
HEADER_FIELD_RE = re.compile(r"\*\*(Asana project|Asana section|Program deadline)\*\*\s*\|\s*(.+?)\s*\|")

# Legacy Asana parent names in the same section
PARENT_ALIASES: dict[str, list[str]] = {
    "Discovery & Planning": ["Planning and Discovery"],
    "Health Assessment": ["Prisma SDWAN Health Assessment"],
    "Documentation": ["Prisma SDWAN S&O Documentation"],
    "Maturity Assessment": ["Prisma SDWAN MA", "Maturity Model for Prisma SD-WAN"],
    "Adoption Assessment": ["Prisma SDWAN Adoption Assessment"],
    "Review & Release": ["Review, Refinement, and Finalization"],
    "SD-WAN Config SDK": ["Lab Validation and Tooling Integration"],
}

TAG_BY_MAIN: dict[str, list[str]] = {
    "Discovery & Planning": ["planning"],
    "Maturity Assessment": ["MA"],
    "Health Assessment": ["HA"],
    "Adoption Assessment": ["AA"],
    "Documentation": ["Playbook", "Reporting"],
    "Review & Release": ["review"],
    "SD-WAN Config SDK": ["SDK"],
    "Netsec Assistant Integration": ["Netsec"],
}

# Canonical main-task order for backlog markdown and section layout
MAIN_TASK_ORDER: list[str] = [
    "Discovery & Planning",
    "Maturity Assessment",
    "Health Assessment",
    "Adoption Assessment",
    "Netsec Assistant Integration",
    "SD-WAN Config SDK",
    "Documentation",
    "Review & Release",
]


@dataclass
class SubtaskSpec:
    name: str
    due: str | None
    status: str
    notes: str = ""


@dataclass
class MainTaskSpec:
    title: str
    phase_target: str
    phase_status: str
    subtasks: list[SubtaskSpec] = field(default_factory=list)
    comments: list[str] = field(default_factory=list)

    @property
    def aliases(self) -> list[str]:
        return PARENT_ALIASES.get(self.title, [])

    @property
    def tag_names(self) -> list[str]:
        return TAG_BY_MAIN.get(self.title, [])


@dataclass
class SyncMetadata:
    project_name: str | None = None
    section_name: str | None = None
    program_deadline: str | None = None
    last_synced: str | None = None
    default_sync_tag: str = "SD-WAN-SnO"


@dataclass
class SyncPlan:
    metadata: SyncMetadata
    main_tasks: list[MainTaskSpec] = field(default_factory=list)
    source_path: Path | None = None


@dataclass
class SyncContext:
    workspace_gid: str
    project_gid: str
    section_gid: str
    project_name: str
    section_name: str
    sync_tag: str
    comment_prefix: str
    rate_limit_s: float = 0.12


@dataclass
class MainTaskResult:
    title: str
    gid: str
    permalink: str | None
    subtasks_created: int
    subtasks_updated: int
    subtasks_done: int
    comments_added: int


def norm(s: str) -> str:
    return " ".join(s.split()).casefold()


def _parse_table_rows(block: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or cells[0].lower() == "subtask":
            continue
        if all(set(c) <= {"-"} for c in cells):
            continue
        rows.append(cells)
    return rows


def _parse_comments(block: str) -> list[str]:
    comments: list[str] = []
    if "**Comments**" not in block:
        return comments
    _, tail = block.split("**Comments**", 1)
    for line in tail.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            if line.startswith("---") or line.startswith("### Main task:"):
                break
            continue
        body = line[2:].strip()
        body = re.sub(r"^\*\*\d{4}-\d{2}-\d{2}\*\*\s*", "", body)
        body = body.replace(" — ", " — ", 1)
        if " — " in body:
            _, rest = body.split(" — ", 1)
            comments.append(rest.strip() if rest.strip() else body)
        else:
            comments.append(body)
    return comments


def parse_asana_tasks_md(text: str, source_path: Path | None = None) -> SyncPlan:
    metadata = SyncMetadata()
    for match in HEADER_FIELD_RE.finditer(text):
        key, value = match.group(1), match.group(2).strip()
        if key == "Asana project":
            metadata.project_name = value
        elif key == "Asana section":
            metadata.section_name = value
        elif key == "Program deadline":
            metadata.program_deadline = value

    main_tasks: list[MainTaskSpec] = []
    parts = MAIN_TASK_RE.split(text)
    # parts[0] is preamble; then title, body, title, body, ...
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        phase_match = PHASE_RE.search(body)
        phase_target = phase_match.group(1) if phase_match else ""
        phase_status = phase_match.group(2).strip() if phase_match else ""

        table_block = body.split("**Comments**")[0]
        subtasks: list[SubtaskSpec] = []
        for row in _parse_table_rows(table_block):
            if len(row) < 3:
                continue
            name, due, status = row[0], row[1], row[2]
            notes = row[3] if len(row) > 3 else ""
            due_val = due if re.fullmatch(r"\d{4}-\d{2}-\d{2}", due) else None
            subtasks.append(
                SubtaskSpec(name=name, due=due_val, status=status, notes=notes)
            )

        main_tasks.append(
            MainTaskSpec(
                title=title,
                phase_target=phase_target,
                phase_status=phase_status,
                subtasks=subtasks,
                comments=_parse_comments(body),
            )
        )

    return SyncPlan(metadata=metadata, main_tasks=main_tasks, source_path=source_path)


def resolve_project_gid(c: AsanaClient, ws: str, project_name: str) -> str:
    needle = norm(project_name)

    def _pick(matches: list[dict[str, Any]]) -> str:
        active = [p for p in matches if not p.get("archived")]
        if len(active) == 1:
            return active[0]["gid"]
        if not active:
            raise AsanaError(404, f"Project not found: {project_name}")
        names = ", ".join(p.get("name", "?") for p in active)
        raise AsanaError(400, f"Ambiguous project '{project_name}': {names}")

    projects = c.get_all(
        "/projects", params={"workspace": ws, "opt_fields": "name,archived"}
    )
    matches = [p for p in projects if norm(p.get("name") or "") == needle]
    if matches:
        return _pick(matches)

    typeahead = c.get(
        f"/workspaces/{ws}/typeahead",
        resource_type="project",
        query=project_name,
        count=20,
        opt_fields="name,archived",
    ) or []
    matches = [p for p in typeahead if norm(p.get("name") or "") == needle]
    if matches:
        return _pick(matches)

    raise AsanaError(404, f"Project not found: {project_name}")


def resolve_section_gid(c: AsanaClient, project_gid: str, section_name: str) -> str:
    sections = c.list_sections(project_gid)
    needle = norm(section_name)
    matches = [s for s in sections if norm(s.get("name") or "") == needle]
    if len(matches) == 1:
        return matches[0]["gid"]
    if not matches:
        names = ", ".join(s.get("name", "?") for s in sections) or "(none)"
        raise AsanaError(
            404, f"Section '{section_name}' not found in project. Available: {names}"
        )
    raise AsanaError(400, f"Ambiguous section '{section_name}'")


def build_sync_context(
    c: AsanaClient,
    plan: SyncPlan,
    *,
    project_name: str | None = None,
    section_name: str | None = None,
    sync_tag: str | None = None,
) -> SyncContext:
    ws = c.default_workspace_gid()
    proj = project_name or plan.metadata.project_name
    sect = section_name or plan.metadata.section_name
    if not proj or not sect:
        raise ValueError(
            "project_name and section_name are required (in markdown header or arguments)"
        )
    project_gid = resolve_project_gid(c, ws, proj)
    section_gid = resolve_section_gid(c, project_gid, sect)
    tag = sync_tag or plan.metadata.default_sync_tag
    today = date.today().isoformat()
    src = plan.source_path.name if plan.source_path else "asana_tasks.md"
    prefix = f"[{src} sync {today}]"
    return SyncContext(
        workspace_gid=ws,
        project_gid=project_gid,
        section_gid=section_gid,
        project_name=proj,
        section_name=sect,
        sync_tag=tag,
        comment_prefix=prefix,
    )


def find_parent_in_section(
    c: AsanaClient, ctx: SyncContext, spec: MainTaskSpec
) -> dict[str, Any] | None:
    tasks = c.get_all(
        f"/sections/{ctx.section_gid}/tasks",
        params={"opt_fields": TASK_OPT_FIELDS, "completed_since": "1970-01-01"},
    )
    aliases = {norm(a) for a in [spec.title, *spec.aliases]}
    for t in tasks:
        if norm(t.get("name") or "") in aliases:
            return t
    return None


def ensure_parent(c: AsanaClient, ctx: SyncContext, spec: MainTaskSpec) -> dict[str, Any]:
    parent = find_parent_in_section(c, ctx, spec)
    if parent:
        updates: dict[str, Any] = {}
        if parent.get("completed"):
            updates["completed"] = False
        if norm(parent.get("name") or "") != norm(spec.title):
            updates["name"] = spec.title
        if spec.phase_target:
            updates["due_on"] = spec.phase_target
        if updates:
            parent = c.put(f"/tasks/{parent['gid']}", data=updates)
        c.add_task_to_section(parent["gid"], ctx.section_gid)
        return parent

    tag_gids = c.resolve_tag_gids(
        ctx.workspace_gid, tag_names=[ctx.sync_tag], create_missing=True
    )
    data: dict[str, Any] = {
        "name": spec.title,
        "projects": [ctx.project_gid],
        "due_on": spec.phase_target or None,
        "assignee": "me",
        "notes": f"Phase status: {spec.phase_status}\nSynced from {ctx.comment_prefix}",
    }
    if tag_gids:
        data["tags"] = tag_gids
    parent = c.post("/tasks", data=data)
    c.add_task_to_section(parent["gid"], ctx.section_gid)
    return parent


def index_subtasks(c: AsanaClient, parent_gid: str) -> dict[str, dict[str, Any]]:
    subs = c.get_all(
        f"/tasks/{parent_gid}/subtasks",
        params={"opt_fields": "name,completed,due_on,notes"},
        max_items=500,
    )
    return {norm(s.get("name") or ""): s for s in subs}


def sync_subtasks(
    c: AsanaClient,
    parent_gid: str,
    specs: list[SubtaskSpec],
    *,
    rate_limit_s: float = 0.12,
) -> tuple[int, int, int]:
    existing = index_subtasks(c, parent_gid)
    created = updated = done_count = 0

    for spec in specs:
        key = norm(spec.name)
        is_done = spec.status.strip().casefold() == "done"
        body_notes = spec.notes or None

        if key in existing:
            sub = existing[key]
            gid = sub["gid"]
            patch: dict[str, Any] = {}
            if spec.due and sub.get("due_on") != spec.due:
                patch["due_on"] = spec.due
            if body_notes and (sub.get("notes") or "") != body_notes:
                patch["notes"] = body_notes
            if is_done != bool(sub.get("completed")):
                patch["completed"] = is_done
            if patch:
                c.put(f"/tasks/{gid}", data=patch)
                updated += 1
        else:
            data: dict[str, Any] = {
                "name": spec.name,
                "assignee": "me",
                "completed": is_done,
            }
            if spec.due:
                data["due_on"] = spec.due
            if body_notes:
                data["notes"] = body_notes
            c.create_subtask(parent_gid, data)
            created += 1

        if is_done:
            done_count += 1
        time.sleep(rate_limit_s)

    return created, updated, done_count


def add_comments(
    c: AsanaClient,
    parent_gid: str,
    comments: list[str],
    *,
    prefix: str,
    rate_limit_s: float = 0.12,
) -> int:
    stories = c.get_all(
        f"/tasks/{parent_gid}/stories",
        params={"opt_fields": "text,type"},
        max_items=200,
    )
    existing_text = {(s.get("text") or "") for s in stories if s.get("type") == "comment"}
    added = 0
    for comment in comments:
        text = f"{prefix} {comment}"
        if text in existing_text:
            continue
        c.post(f"/tasks/{parent_gid}/stories", data={"text": text})
        added += 1
        time.sleep(rate_limit_s)
    return added


def sync_main_task(
    c: AsanaClient, ctx: SyncContext, spec: MainTaskSpec
) -> MainTaskResult:
    parent = ensure_parent(c, ctx, spec)
    pgid = parent["gid"]
    tag_names = [ctx.sync_tag, *spec.tag_names]
    c.apply_task_tags(pgid, ctx.workspace_gid, add_tag_names=tag_names, create_missing=True)
    cr, up, done = sync_subtasks(
        c, pgid, spec.subtasks, rate_limit_s=ctx.rate_limit_s
    )
    cm = add_comments(
        c, pgid, spec.comments, prefix=ctx.comment_prefix, rate_limit_s=ctx.rate_limit_s
    )
    return MainTaskResult(
        title=spec.title,
        gid=pgid,
        permalink=parent.get("permalink_url"),
        subtasks_created=cr,
        subtasks_updated=up,
        subtasks_done=done,
        comments_added=cm,
    )


def sync_plan(
    c: AsanaClient,
    plan: SyncPlan,
    ctx: SyncContext,
    *,
    limit: int | None = None,
) -> tuple[list[MainTaskResult], list[str]]:
    results: list[MainTaskResult] = []
    errors: list[str] = []
    tasks = plan.main_tasks[:limit] if limit else plan.main_tasks
    for spec in tasks:
        try:
            results.append(sync_main_task(c, ctx, spec))
        except AsanaError as exc:
            errors.append(f"{spec.title}: {exc.message}")
    return results, errors


def load_and_parse(path: str | Path) -> SyncPlan:
    p = Path(path)
    return parse_asana_tasks_md(p.read_text(encoding="utf-8"), source_path=p)


def format_results(
    ctx: SyncContext,
    results: list[MainTaskResult],
    errors: list[str],
) -> str:
    lines = [
        f"Synced **{len(results)}** main task(s) -> "
        f"**{ctx.project_name}** / **{ctx.section_name}**",
        "",
    ]
    for r in results:
        lines.extend(
            [
                f"### {r.title}",
                f"- GID: `{r.gid}`",
                f"- URL: {r.permalink or '-'}",
                f"- Subtasks: +{r.subtasks_created} created, {r.subtasks_updated} updated "
                f"({r.subtasks_done} done in spec)",
                f"- Comments: +{r.comments_added}",
                "",
            ]
        )
    if errors:
        lines.append("### Errors")
        lines.extend(f"- {e}" for e in errors)
    return "\n".join(lines)


@dataclass
class OrphanTagResult:
    parent_title: str
    parent_gid: str
    subtask_name: str
    subtask_gid: str
    tagged: bool
    already_tagged: bool = False


def reorder_plan_main_tasks(plan: SyncPlan, order: list[str] | None = None) -> SyncPlan:
    """Return a plan copy with main tasks sorted to *order* (unknown titles appended)."""
    order = order or MAIN_TASK_ORDER
    rank = {norm(t): i for i, t in enumerate(order)}
    sorted_tasks = sorted(
        plan.main_tasks,
        key=lambda t: rank.get(norm(t.title), len(order)),
    )
    return SyncPlan(
        metadata=plan.metadata,
        main_tasks=sorted_tasks,
        source_path=plan.source_path,
    )


def reorder_asana_tasks_md_file(
    path: str | Path,
    order: list[str] | None = None,
) -> SyncPlan:
    """Rewrite *path* so main-task sections and summary table follow *order*."""
    order = order or MAIN_TASK_ORDER
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    summary_match = re.search(r"\n## Summary\n", text)
    if not summary_match:
        raise ValueError(f"No '## Summary' section in {p}")

    body = text[: summary_match.start()]
    summary = text[summary_match.start() + 1 :]

    blocks: dict[str, str] = {}
    for m in re.finditer(
        r"### Main task:\s*(.+?)\s*\n(.*?)(?=\n---\n|\Z)",
        body,
        re.DOTALL,
    ):
        title = m.group(1).strip()
        blocks[title] = f"### Main task: {title}\n{m.group(2).rstrip()}\n"

    preamble_end = body.find("\n---\n\n### Main task:")
    if preamble_end < 0:
        raise ValueError(f"No main tasks found in {p}")
    preamble = body[: preamble_end].rstrip() + "\n"

    ordered_blocks: list[str] = []
    for title in order:
        if title in blocks:
            ordered_blocks.append(blocks.pop(title))
    ordered_blocks.extend(blocks[t] for t in sorted(blocks))

    new_body = preamble + "\n---\n\n" + "\n---\n\n".join(ordered_blocks) + "\n---\n\n"

    plan = reorder_plan_main_tasks(
        parse_asana_tasks_md(new_body + summary, source_path=p),
        order,
    )
    summary_lines = ["## Summary", "", "| Main task | Subtasks | Done | Open / In progress |", "|-----------|----------|------|---------------------|"]
    total_sub = total_done = total_open = 0
    for mt in plan.main_tasks:
        done = sum(1 for s in mt.subtasks if s.status.strip().casefold() == "done")
        open_count = len(mt.subtasks) - done
        total_sub += len(mt.subtasks)
        total_done += done
        total_open += open_count
        summary_lines.append(
            f"| {mt.title} | {len(mt.subtasks)} | {done} | {open_count} |"
        )
    summary_lines.append(f"| **Total** | **{total_sub}** | **{total_done}** | **{total_open}** |")
    summary_lines.append("")
    summary_lines.append(
        "**Suggested tags for notes:** `SD-WAN-SnO`, `MA`, `HA`, `AA`, `SDK`, `Netsec`, "
        "`Scoring`, `Checklist`, `Playbook`, `Reporting`, `Blocker`"
    )

    p.write_text(new_body + "\n".join(summary_lines) + "\n", encoding="utf-8")
    plan.source_path = p
    return plan


def tag_orphan_subtasks(
    c: AsanaClient,
    plan: SyncPlan,
    ctx: SyncContext,
    *,
    orphan_tag: str = "remove",
) -> list[OrphanTagResult]:
    """Tag subtasks under each main parent that are not listed in the markdown."""
    results: list[OrphanTagResult] = []
    remove_tag_gid = c.resolve_tag_gids(
        ctx.workspace_gid, tag_names=[orphan_tag], create_missing=True
    )[0]

    for spec in plan.main_tasks:
        parent = find_parent_in_section(c, ctx, spec)
        if not parent:
            continue
        pgid = parent["gid"]
        expected = {norm(s.name) for s in spec.subtasks}
        subs = c.get_all(
            f"/tasks/{pgid}/subtasks",
            params={"opt_fields": "name,tags.name,tags.gid"},
            max_items=500,
        )
        for sub in subs:
            name = sub.get("name") or ""
            if norm(name) in expected:
                continue
            sg = sub["gid"]
            current_tags = {t.get("gid") for t in (sub.get("tags") or []) if t.get("gid")}
            already = remove_tag_gid in current_tags
            tagged = False
            if not already:
                c.add_tag_to_task(sg, remove_tag_gid)
                tagged = True
                time.sleep(ctx.rate_limit_s)
            results.append(
                OrphanTagResult(
                    parent_title=spec.title,
                    parent_gid=pgid,
                    subtask_name=name,
                    subtask_gid=sg,
                    tagged=tagged,
                    already_tagged=already,
                )
            )
    return results


def reorder_section_parents(
    c: AsanaClient,
    plan: SyncPlan,
    ctx: SyncContext,
) -> list[tuple[str, str]]:
    """Reorder parent tasks in the section to match plan main-task order."""
    ordered: list[tuple[str, str]] = []
    prev_gid: str | None = None
    for spec in plan.main_tasks:
        parent = find_parent_in_section(c, ctx, spec)
        if not parent:
            continue
        gid = parent["gid"]
        data: dict[str, Any] = {"task": gid}
        if prev_gid:
            data["insert_after"] = prev_gid
        c.post(f"/sections/{ctx.section_gid}/addTask", data=data)
        ordered.append((spec.title, gid))
        prev_gid = gid
        time.sleep(ctx.rate_limit_s)
    return ordered


def format_orphan_tag_results(results: list[OrphanTagResult], orphan_tag: str) -> str:
    if not results:
        return f"No orphan subtasks found (tag `{orphan_tag}` not needed)."
    tagged = [r for r in results if r.tagged]
    already = [r for r in results if r.already_tagged and not r.tagged]
    lines = [
        f"Orphan subtasks tagged `{orphan_tag}`: {len(tagged)} newly tagged, "
        f"{len(already)} already tagged, {len(results)} total orphans",
        "",
    ]
    by_parent: dict[str, list[OrphanTagResult]] = {}
    for r in results:
        by_parent.setdefault(r.parent_title, []).append(r)
    for parent, items in by_parent.items():
        lines.append(f"### {parent}")
        for r in items:
            status = "already tagged" if r.already_tagged and not r.tagged else "tagged"
            lines.append(f"- [{status}] {r.subtask_name} (`{r.subtask_gid}`)")
        lines.append("")
    return "\n".join(lines).rstrip()
