"""Install or refresh the project tracker artifact in one project.

Writes, inside the project:
  .claude/project_artifact.json          the artifact URL, title and page path (one artifact per project)
  .claude/project_artifact/tracker.html  the page, filled from assets/tracker.html
  CLAUDE.md                              a marked section with the rules every agent follows
  .claude/settings.json                  a Stop hook that reminds Claude to update the tracker

Publishing the page is done by Claude with the Artifact tool; run again with --url to record the URL.
Safe to re-run: every write replaces only what this script owns.
"""
import argparse
import datetime
import html
import json
import os
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(SKILL_DIR, "assets", "tracker.html")
HOOK = os.path.join(SKILL_DIR, "scripts", "stop_hook.py").replace("\\", "/")
MARK_START = "<!-- amir_project_artifact:start -->"
MARK_END = "<!-- amir_project_artifact:end -->"
HOOK_TAG = "amir_project_artifact"

RULES = """{start}
## Project tracker artifact

This project has one tracker artifact: {url}
Never create a second one. Page source: `.claude/project_artifact/tracker.html`. Config: `.claude/project_artifact.json`.
Republish the page (Artifact tool, `url` above) only when the page code changes. Data lives in the artifact's
database and is read and written with the `ArtifactData` tool (load it with ToolSearch `select:ArtifactData`).

Collections: `meta` (doc `project`), `plan`, `tasks`, `questions`, `logs`, `chats`. Field list: the
amir_project_artifact skill, section 5.

Every agent working in this project follows these rules:

1. At the end of every turn that changed anything (files, commands, decisions, findings, answers from the user),
   write only the rows that changed: task status and notes, question answers (status Answered or Follow up, with
   the date), one `logs` row per decision, change, finding or action (with `files` touched and `task` id), and
   `meta/project` fields `last_updated`, `current_stage`, `blockers`, `needed`.
2. Read a row before overwriting it and pin `if_version`. A row the user changed in the page wins.
3. Before asking the user anything, check `questions`. Never re-ask an Answered question; raise a new one that
   names the old one if a refinement is needed.
4. Task status is one of Not started, In progress, Done, Failed, Blocked, Cancelled. Never set Done without
   writing in `notes` how it was verified. Never delete a task; cancel it with a `cancel_reason`.
5. Subagents: with the `ArtifactData` tool, write a `logs` row for your own work with the task id. Without it,
   end your report with a section "Tracker update" listing the rows to write, and the parent agent writes them.
6. A Stop hook (`.claude/settings.json`) blocks the end of a turn once when work was done but no `ArtifactData`
   write happened. If nothing in the tracker needs to change, say so in one line and stop again.
{end}
"""


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def load_json(path, default):
    if not os.path.isfile(path):
        return default
    with open(path, encoding="utf-8") as fh:
        text = fh.read().strip()
    return json.loads(text) if text else default


def write_page(project, title, subtitle):
    with open(TEMPLATE, encoding="utf-8") as fh:
        page = fh.read()
    page = page.replace("__PROJECT_TITLE__", html.escape(title, quote=False))
    page = page.replace("__PROJECT_SUBTITLE__", html.escape(subtitle, quote=False))
    path = os.path.join(project, ".claude", "project_artifact", "tracker.html")
    write_text(path, page)
    return path


def write_rules(project, url):
    path = os.path.join(project, "CLAUDE.md")
    block = RULES.format(start=MARK_START, end=MARK_END, url=url or "not published yet (run the skill to publish it)")
    current = ""
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            current = fh.read()
    if MARK_START in current and MARK_END in current:
        head, rest = current.split(MARK_START, 1)
        tail = rest.split(MARK_END, 1)[1].lstrip("\n")
        updated = head + block + ("\n" + tail if tail else "")
    else:
        updated = (current.rstrip("\n") + "\n\n" if current.strip() else "") + block
    write_text(path, updated)
    return path


def write_hook(project, python):
    path = os.path.join(project, ".claude", "settings.json")
    settings = load_json(path, {})
    command = '{} -I "{}"'.format(python, HOOK)
    stop = settings.setdefault("hooks", {}).setdefault("Stop", [])
    for group in stop:
        for hook in group.get("hooks", []):
            if HOOK_TAG in str(hook.get("command", "")):
                hook["command"] = command
                break
        else:
            continue
        break
    else:
        stop.append({"hooks": [{"type": "command", "command": command, "timeout": 30}]})
    write_text(path, json.dumps(settings, indent=2) + "\n")
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=os.getcwd(), help="project root (default: current directory)")
    ap.add_argument("--title", help="artifact title, a short name (default: kept, else the folder name)")
    ap.add_argument("--subtitle", help="one line under the title")
    ap.add_argument("--url", help="record the published artifact URL")
    ap.add_argument("--python", default="python", help="interpreter used by the Stop hook")
    ap.add_argument("--status", action="store_true", help="print the current config and exit")
    args = ap.parse_args()

    project = os.path.abspath(args.project)
    config_path = os.path.join(project, ".claude", "project_artifact.json")
    try:
        config = load_json(config_path, {})
    except ValueError as exc:
        print("error: {} is not valid JSON: {}".format(config_path, exc), file=sys.stderr)
        return 1
    if args.status:
        print(json.dumps(config or {"installed": False}, indent=2))
        return 0
    if config.get("url") and args.url and args.url != config["url"]:
        print("error: this project already has a tracker at {}. One artifact per project.".format(config["url"]), file=sys.stderr)
        return 1

    title = args.title or config.get("title") or os.path.basename(project)
    subtitle = args.subtitle or config.get("subtitle") or "Project tracker"
    try:
        hook_path = write_hook(project, args.python)
    except ValueError as exc:
        print("error: .claude/settings.json is not valid JSON, fix it first: {}".format(exc), file=sys.stderr)
        return 1
    page_path = write_page(project, title, subtitle)
    config.update({
        "title": title,
        "subtitle": subtitle,
        "url": args.url or config.get("url", ""),
        "page": ".claude/project_artifact/tracker.html",
        "project_path": project.replace("\\", "/"),
        "skill_dir": SKILL_DIR.replace("\\", "/"),
        "updated": datetime.date.today().isoformat(),
    })
    write_text(config_path, json.dumps(config, indent=2) + "\n")
    rules_path = write_rules(project, config["url"])
    print(json.dumps({
        "page": page_path, "config": config_path, "rules": rules_path, "hook": hook_path,
        "url": config["url"] or None,
        "next": "publish the page, then re-run with --url" if not config["url"] else "republish the page to the url if its code changed",
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
