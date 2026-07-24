"""Detect legacy amir installs and print a migration plan. PLAN ONLY -- never destructive."""
from __future__ import annotations

import json
import os
from pathlib import Path

# legacy plugin@marketplace ids known to exist on this machine
LEGACY_CLAUDE_PLUGINS = (
    "amir-ai@amir-ai-marketplace",
    "amir-asana@amir-asana-marketplace",
)

# legacy plugin dir name -> replacement in the two-plugin model
LEGACY_MAP = {
    "amir": "amir_project (group: harness) + amir_system (core lifecycle commands)",
    "amir-ai": "amir_system (core) + amir_project (group: harness)",
    "amir-asana": "amir_system (group: asana)",
    "amir-aws": "amir_project (group: aws)",
    "amir-azure": "amir_project (group: azure)",
    "amir-cortex-xdr": "amir_project (group: xdr)",
    "amir-docker": "amir_project (group: docker)",
    "amir-elastic": "amir_project (group: elastic)",
    "amir-litellm": "amir_project (group: litellm)",
    "amir-nmap": "amir_project (group: nmap)",
    "amir-paloalto": "amir_project (group: paloalto)",
    "amir-prisma": "amir_project (group: prisma)",
    "amir-qradar": "amir_project (group: qradar)",
    "amir-sentinel": "amir_project (group: sentinel)",
    "amir-splunk": "amir_project (group: splunk)",
    "amir-ssh": "amir_project (group: ssh)",
    "amir-terraform": "amir_project (group: terraform)",
    "amir-wireshark": "amir_project (group: wireshark)",
}


def _detect_claude_plugins(home: Path) -> list[dict]:
    installed_path = home / ".claude" / "plugins" / "installed_plugins.json"
    findings = []
    if not installed_path.is_file():
        return findings
    text = installed_path.read_text(encoding="utf-8", errors="replace")
    for legacy in LEGACY_CLAUDE_PLUGINS:
        if legacy in text:
            findings.append({"kind": "claude-plugin", "id": legacy, "source": str(installed_path)})
    try:  # also enumerate any other amir-prefixed entries, format-tolerantly
        data = json.loads(text)
        keys = list(data.keys()) if isinstance(data, dict) else []
        for key in keys:
            if "amir" in key and key not in [f["id"] for f in findings] and key not in (
                    "amir_system@amir-marketplace", "amir_project@amir-marketplace"):
                findings.append({"kind": "claude-plugin", "id": key, "source": str(installed_path)})
    except (json.JSONDecodeError, AttributeError):
        pass
    return findings


def _detect_cursor_junctions(home: Path) -> list[dict]:
    local = home / ".cursor" / "plugins" / "local"
    findings = []
    if not local.is_dir():
        return findings
    for child in sorted(local.iterdir()):
        if not child.is_dir():
            continue
        try:
            target = Path(os.path.realpath(child))
        except OSError:
            continue
        target_str = str(target).lower()
        if "amir_marketplace" not in target_str:
            continue
        old_name = target.name
        if old_name in LEGACY_MAP or (old_name.startswith("amir-")) or old_name == "amir":
            findings.append({"kind": "cursor-junction", "path": str(child), "target": str(target),
                             "legacy_name": old_name})
    return findings


def detect_legacy(home: Path | None = None) -> dict:
    home = Path(home) if home else Path.home()
    return {
        "claude_plugins": _detect_claude_plugins(home),
        "cursor_junctions": _detect_cursor_junctions(home),
    }


def format_plan(report: dict) -> str:
    lines = ["Legacy install migration plan (NO actions are taken -- run the listed commands yourself):", ""]
    if not report["claude_plugins"] and not report["cursor_junctions"]:
        lines.append("No legacy amir installs detected.")
        return "\n".join(lines)
    for finding in report["claude_plugins"]:
        plugin_name = finding["id"].split("@")[0]
        replacement = LEGACY_MAP.get(plugin_name, LEGACY_MAP.get(plugin_name.replace("amir-", ""), "see design/component-map.md"))
        lines.append(f"[claude] {finding['id']}")
        lines.append(f"    replaced by: {replacement}")
        lines.append(f"    removal:     claude plugin uninstall {finding['id']}")
    for finding in report["cursor_junctions"]:
        replacement = LEGACY_MAP.get(finding["legacy_name"], "see design/component-map.md")
        lines.append(f"[cursor] junction {finding['path']} -> {finding['target']}")
        lines.append(f"    replaced by: {replacement}")
        lines.append(f"    removal:     cmd /c rmdir \"{finding['path']}\"  (removes the junction only, not the target)")
    lines += ["", "After removal, install the new model:",
              "  claude plugin install amir_system@amir-marketplace --scope user",
              "  per project: /amir:create_project or /amir:onboard_project"]
    return "\n".join(lines)
