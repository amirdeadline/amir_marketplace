"""Stop hook for amir_project_artifact.

Blocks the end of a turn once when the turn did real work (edits, commands,
questions to the user, subagents) in a project that has a tracker artifact,
but never wrote to the tracker's database. The reason tells Claude what to
update. A second stop in the same turn is always allowed (stop_hook_active),
so the hook can never loop. Any error lets the stop through.
"""
import json
import os
import sys

CONFIG = os.path.join(".claude", "project_artifact.json")
TAIL_BYTES = 8 * 1024 * 1024

# Tools that only read or steer the app; a turn of only these needs no tracker update.
NEUTRAL = {
    "Read", "Grep", "Glob", "LS", "ToolSearch", "WebFetch", "WebSearch", "TodoWrite",
    "NotebookRead", "ReadNotifications", "ListAgents", "Skill", "Artifact", "ArtifactComments",
}
NEUTRAL_PREFIXES = ("mcp__ccd_", "mcp__visualize__")
TRACKER_WRITES = {"ArtifactData"}


def find_config(start):
    path = os.path.abspath(start or os.getcwd())
    while True:
        candidate = os.path.join(path, CONFIG)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent


def is_user_prompt(entry):
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isSidechain"):
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        kinds = {item.get("type") for item in content if isinstance(item, dict)}
        return "tool_result" not in kinds and "text" in kinds
    return False


def tools_this_turn(transcript_path):
    with open(transcript_path, "rb") as fh:
        fh.seek(0, os.SEEK_END)
        size = fh.tell()
        fh.seek(max(0, size - TAIL_BYTES))
        raw = fh.read().decode("utf-8", errors="replace")
    names = []
    for line in raw.splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if is_user_prompt(entry):
            names = []
            continue
        if entry.get("type") != "assistant" or entry.get("isSidechain"):
            continue
        for item in (entry.get("message") or {}).get("content") or []:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                names.append(str(item.get("name", "")))
    return names


def is_neutral(name):
    return name in NEUTRAL or name.startswith(NEUTRAL_PREFIXES)


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    if data.get("stop_hook_active"):
        return 0
    config_path = find_config(data.get("cwd"))
    transcript = data.get("transcript_path")
    if not config_path or not transcript or not os.path.isfile(transcript):
        return 0
    with open(config_path, encoding="utf-8") as fh:
        config = json.load(fh)
    url = config.get("url")
    if not url:
        return 0
    names = tools_this_turn(transcript)
    worked = [n for n in names if not is_neutral(n) and n not in TRACKER_WRITES]
    wrote = any(n in TRACKER_WRITES for n in names)
    if worked and not wrote:
        reason = (
            "Project tracker not updated this turn: " + url + ". "
            "Before stopping, write the rows that changed with ArtifactData (load it with ToolSearch "
            "'select:ArtifactData' if needed): task status and notes, answers to questions, one logs row per "
            "decision, change, finding or action with files touched and the task id, and meta last_updated, "
            "current_stage, blockers and needed. Read a row before overwriting it and pin if_version. "
            "If nothing in the tracker needs to change, say so in one line and stop."
        )
        print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # never block a stop because the hook itself failed
        sys.exit(0)
