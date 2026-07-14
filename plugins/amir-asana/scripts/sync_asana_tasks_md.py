"""Sync an asana_tasks.md backlog file to Asana.

Usage:
    python scripts/sync_asana_tasks_md.py path/to/asana_tasks.md
    python scripts/sync_asana_tasks_md.py path/to/asana_tasks.md --project "My Project" --section "Backlog"
    python scripts/sync_asana_tasks_md.py path/to/asana_tasks.md --limit 3 --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from asana_connector.asana_tasks_md import (  # noqa: E402
    build_sync_context,
    format_orphan_tag_results,
    format_results,
    load_and_parse,
    reorder_asana_tasks_md_file,
    reorder_section_parents,
    sync_plan,
    tag_orphan_subtasks,
)
from asana_connector.client import AsanaClient  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync asana_tasks.md to Asana")
    parser.add_argument("markdown_path", type=Path, help="Path to asana_tasks.md")
    parser.add_argument("--project", help="Override Asana project name")
    parser.add_argument("--section", help="Override Asana section name")
    parser.add_argument("--sync-tag", default=None, help="Default tag name to apply")
    parser.add_argument("--limit", type=int, default=None, help="Sync only first N main tasks")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and print plan without writing to Asana",
    )
    parser.add_argument(
        "--reorder-md",
        action="store_true",
        help="Rewrite markdown main-task sections to canonical order before sync",
    )
    parser.add_argument(
        "--reorder-section",
        action="store_true",
        help="Reorder parent tasks in the Asana section to match markdown order",
    )
    parser.add_argument(
        "--tag-orphans",
        metavar="TAG",
        default=None,
        help='Tag subtasks not listed in markdown (e.g. "remove")',
    )
    parser.add_argument(
        "--no-sync",
        action="store_true",
        help="Skip create/update sync (only --reorder-md / --reorder-section / --tag-orphans)",
    )
    args = parser.parse_args()

    if not args.markdown_path.is_file():
        print(f"File not found: {args.markdown_path}", file=sys.stderr)
        return 1

    if args.reorder_md:
        plan = reorder_asana_tasks_md_file(args.markdown_path)
        print(f"Reordered markdown: {args.markdown_path}")
    else:
        plan = load_and_parse(args.markdown_path)
    project = args.project or plan.metadata.project_name
    section = args.section or plan.metadata.section_name

    if not project or not section:
        print(
            "Missing project and/or section. Provide in markdown header table or "
            "use --project and --section.",
            file=sys.stderr,
        )
        return 1

    if args.dry_run:
        print(f"Project: {project}")
        print(f"Section: {section}")
        print(f"Main tasks: {len(plan.main_tasks)}")
        for mt in plan.main_tasks[: args.limit] if args.limit else plan.main_tasks:
            print(f"  - {mt.title}: {len(mt.subtasks)} subtasks, {len(mt.comments)} comments")
        return 0

    needs_asana = (not args.no_sync) or args.reorder_section or bool(args.tag_orphans)
    if not needs_asana:
        return 0

    with AsanaClient() as c:
        ctx = build_sync_context(
            c,
            plan,
            project_name=project,
            section_name=section,
            sync_tag=args.sync_tag,
        )
        results: list = []
        errors: list[str] = []
        if not args.no_sync:
            results, errors = sync_plan(c, plan, ctx, limit=args.limit)
        if args.reorder_section:
            reorder_section_parents(c, plan, ctx)
            print("Reordered parent tasks in Asana section.")
        if args.tag_orphans:
            orphan_results = tag_orphan_subtasks(
                c, plan, ctx, orphan_tag=args.tag_orphans
            )
            print(format_orphan_tag_results(orphan_results, args.tag_orphans))
            print("")

    if not args.no_sync:
        print(format_results(ctx, results, errors))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
