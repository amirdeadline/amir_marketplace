#!/usr/bin/env python3
"""One-shot deterministic migration: build plugins/amir_project from plugins/amir
and the 15 amir-<x> satellite plugins, per design/component-map.md and
design/SPEC-amir_project-tools.md.

Idempotent: deletes only the outputs it owns before re-creating them.
Never touches source plugins (read-only) or other agents' paths
(commands/serena|context7|semgrep|langfuse|openhands|worktrees|swebench|terminalbench).
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

MARKETPLACE = Path(r"E:\PC3_Shared\Plugins\amir_marketplace")
PLUGINS = MARKETPLACE / "plugins"
SRC_HARNESS = PLUGINS / "amir"
DST = PLUGINS / "amir_project"

# ---------------------------------------------------------------- harness data

KEPT_HARNESS = [
    "agent_reset", "btw", "build_agents", "build_goal", "design",
    "design_agents", "design_qa", "docs_sync", "document_max", "git_commit",
    "git_push", "git_setup", "git_tree", "handoff", "milestone_retro", "plan",
    "project_cleanup", "project_cost", "project_tasks", "project_watch",
    "resume_build", "rollback", "security_scan", "tasks_update", "troubleshoot",
]

# alias -> (replacement command, extra note)
DEPRECATED_ALIASES = {
    "project_create": ("/amir:create_project", "provided by the amir_system plugin"),
    "project_import": ("/amir:onboard_project", "provided by the amir_system plugin"),
    "use_subagent": ("/amir:use_subagents", "provided by the amir_system plugin"),
    "compact": ("/amir:cleanup_context", "provided by the amir_system plugin"),
    "project_doctor": ("/amir:validate_project", "provided by the amir_system plugin"),
    "project_status": ("/amir:project_status", "which now lives in the amir_system plugin"),
}

RETIRED = ["system_cleanup", "system_settings", "system_skills",
           "user_cleanup", "user_settings", "user_skills"]

HARNESS_SUPPORT_DIRS = ["agents", "core", "templates", "tools", "schemas", "rules", "bin"]
HARNESS_ROOT_FILES = ["capabilities.md", "AGENTS.md"]

# --------------------------------------------------------------- satellite data

# group dir -> config
GROUPS: dict[str, dict] = {
    "aws": {
        "src": "amir-aws", "gate": "aws",
        "cmds": {"cli": "aws_cli", "whoami": "aws_whoami"},
        "skills": {"aws-cli-safety": "aws_cli_safety",
                   "aws-well-architected": "aws_well_architected"},
    },
    "azure": {
        "src": "amir-azure", "gate": "azure",
        "cmds": {"cli": "azure_cli", "whoami": "azure_whoami"},
        "skills": {"azure-core": "azure_core", "azure-monitor": "azure_monitor",
                   "azure-networking": "azure_networking"},
    },
    "xdr": {
        "src": "amir-cortex-xdr", "gate": "cortex-xdr",
        "cmds": {"ask": "xdr_ask", "incidents": "xdr_incidents",
                 "preflight": "xdr_preflight", "respond": "xdr_respond"},
        "skills": {"xdr-ir": "xdr_ir"},
    },
    "docker": {
        "src": "amir-docker", "gate": "docker",
        "cmds": {"build": "docker_build", "down": "docker_down",
                 "logs": "docker_logs", "push": "docker_push",
                 "status": "docker_status", "up": "docker_up"},
        "skills": {"docker-ops": "docker_ops"},
    },
    "elastic": {
        "src": "amir-elastic", "gate": "elastic",
        "cmds": {"ask": "elastic_ask", "preflight": "elastic_preflight",
                 "search": "elastic_search"},
        "skills": {"elastic-detections": "elastic_detections",
                   "esql-and-dsl": "elastic_esql_and_dsl"},
    },
    "litellm": {
        "src": "amir-litellm", "gate": "litellm",
        "cmds": {"chat": "litellm_chat", "models": "litellm_models",
                 "session": "litellm_session", "spend": "litellm_spend",
                 "status": "litellm_status"},
        "skills": {"litellm-usage": "litellm_usage"},
    },
    "nmap": {
        "src": "amir-nmap", "gate": "nmap",
        "cmds": {"parse": "nmap_parse", "scan": "nmap_scan"},
        "skills": {"nmap-methodology": "nmap_methodology"},
    },
    "paloalto": {
        "src": "amir-paloalto", "gate": "paloalto",
        "cmds": {"api": "panos_api", "ask": "panos_ask", "preflight": "panos_preflight"},
        "skills": {"globalprotect": "panos_globalprotect", "panorama": "panos_panorama",
                   "panos-api": "panos_api", "panos-ngfw": "panos_ngfw",
                   "panos-troubleshooting": "panos_troubleshooting"},
    },
    "prisma": {
        "src": "amir-prisma", "gate": "prisma",
        "cmds": {"api": "prisma_api", "ask": "prisma_ask", "design": "prisma_design",
                 "review": "prisma_review", "troubleshoot": "prisma_troubleshoot",
                 "update-index": "prisma_update_index", "whats-new": "prisma_whats_new"},
        "skills": {"adem": "prisma_adem", "prisma-access": "prisma_access",
                   "scm-api": "prisma_scm_api", "scm-platform": "prisma_scm_platform",
                   "sdwan": "prisma_sdwan", "security-policy": "prisma_security_policy",
                   "troubleshooting": "prisma_troubleshooting",
                   "ztna-access-agent": "prisma_ztna_access_agent"},
    },
    "qradar": {
        "src": "amir-qradar", "gate": "qradar",
        "cmds": {"aql": "qradar_aql", "ask": "qradar_ask", "preflight": "qradar_preflight"},
        "skills": {"aql-and-offenses": "qradar_aql_and_offenses"},
    },
    "sentinel": {
        "src": "amir-sentinel", "gate": "sentinel",
        "cmds": {"ask": "sentinel_ask", "preflight": "sentinel_preflight",
                 "query": "sentinel_query"},
        "skills": {"kql-hunting": "sentinel_kql_hunting",
                   "sentinel-analytics": "sentinel_analytics"},
    },
    "splunk": {
        "src": "amir-splunk", "gate": "splunk",
        "cmds": {"ask": "splunk_ask", "preflight": "splunk_preflight",
                 "search": "splunk_search"},
        "skills": {"spl": "splunk_spl"},
    },
    "ssh": {
        "src": "amir-ssh", "gate": "ssh",
        "cmds": {"copy": "ssh_copy", "run": "ssh_run", "session": "ssh_session"},
        "skills": {"ssh-safety": "ssh_safety"},
    },
    "terraform": {
        "src": "amir-terraform", "gate": "terraform",
        "cmds": {"apply": "terraform_apply", "destroy": "terraform_destroy",
                 "fmt": "terraform_fmt", "init": "terraform_init",
                 "plan": "terraform_plan", "validate": "terraform_validate"},
        "skills": {"terraform-review": "terraform_review"},
    },
    "wireshark": {
        "src": "amir-wireshark", "gate": "wireshark",
        "cmds": {"analyze": "wireshark_analyze", "capture": "wireshark_capture",
                 "extract": "wireshark_extract", "filter": "wireshark_filter"},
        "skills": {"packet-analysis": "wireshark_packet_analysis"},
    },
}

PRISMA_LITERAL = r"E:\PC3_Shared\Palo\Documents\Markdowns Prisma SASE"
PRISMA_NOTE = ("machine-specific default documented in the amir_project plugin "
               "README, section \"Prisma docs corpus\"")

# ------------------------------------------------------- global replacement maps


def build_namespace_map() -> dict[str, str]:
    m: dict[str, str] = {}
    for cfg in GROUPS.values():
        for old, new in cfg["cmds"].items():
            m[f"/{cfg['src']}:{old}"] = f"/amir:{new}"
    # stray short forms observed in the prisma corpus/generator
    m["/prisma:update-index"] = "/amir:prisma_update_index"
    return m


def build_skill_rename_map() -> list[tuple[str, str]]:
    """Ordered (old, new) replacements, longest-first, for skill identity fixes."""
    pairs: list[tuple[str, str]] = []
    for cfg in GROUPS.values():
        for old, new in cfg["skills"].items():
            pairs.append((f"amir-{cfg['src'].removeprefix('amir-')}-{old}", new))  # legacy frontmatter id (no plugin prefix variant)
            pairs.append((f"{cfg['src']}-{old}", new))     # e.g. amir-aws-aws-cli-safety
            pairs.append((f"skills/{old}/", f"skills/{new}/"))
            pairs.append((f"skills/{old}", f"skills/{new}"))
            if "-" in old:                                  # safe bare-token rename
                pairs.append((old, new))
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    return pairs


NS_MAP = build_namespace_map()
SKILL_RENAMES = build_skill_rename_map()

# ------------------------------------------------------------- text processing


def strip_frontmatter_name(text: str) -> str:
    m = re.match(r"^---\r?\n(.*?)^---\r?\n", text, re.S | re.M)
    if not m:
        return text
    fm = m.group(1)
    fm2 = re.sub(r"^name:[^\n]*\n", "", fm, flags=re.M)
    return text[:m.start(1)] + fm2 + text[m.end(1):]


def set_frontmatter_name(text: str, new_name: str) -> str:
    m = re.match(r"^---\r?\n(.*?)^---\r?\n", text, re.S | re.M)
    if not m:
        return text
    fm = m.group(1)
    if re.search(r"^name:", fm, re.M):
        fm2 = re.sub(r"^name:[^\n]*$", f"name: {new_name}", fm, count=1, flags=re.M)
    else:
        fm2 = f"name: {new_name}\n" + fm
    return text[:m.start(1)] + fm2 + text[m.end(1):]


def apply_common_renames(text: str) -> str:
    for old, new in NS_MAP.items():
        text = text.replace(old, new)
    for old, new in SKILL_RENAMES:
        if "-" in old and "/" not in old:
            text = re.sub(rf"(?<![\w/-]){re.escape(old)}(?![\w-])", new, text)
        else:
            text = text.replace(old, new)
    return text


def fix_script_paths(text: str, group_dir: str) -> str:
    text = re.sub(rf"scripts/(?!{group_dir}/|_migration/)", f"scripts/{group_dir}/", text)
    if group_dir == "litellm":
        text = text.replace("${CLAUDE_PLUGIN_ROOT}/bin/", "${CLAUDE_PLUGIN_ROOT}/scripts/litellm/")
    return text


DEFAULT_NOTE_RE = re.compile(r"\(default\s+`E:[^`]*Markdowns Prisma SASE`\)", re.S)


def fix_prisma_docs_path(text: str) -> str:
    text = DEFAULT_NOTE_RE.sub(f"(read env var `PRISMA_DOCS_PATH`; {PRISMA_NOTE})", text)
    # gen_skills.py stores the path with doubled backslashes inside a template string
    text = re.sub(r"\(default\s+`E:[^`]*Markdowns Prisma SASE`\)",
                  f"(read env var `PRISMA_DOCS_PATH`; {PRISMA_NOTE})", text)
    text = text.replace(
        '--docs "' + PRISMA_LITERAL + '"',
        '--docs "$env:PRISMA_DOCS_PATH"',
    )
    return text


GATE_TEMPLATE = (
    "> **Component gate (amir_project):** before doing anything else, read "
    "`.amir/project.yaml` at the project root and verify that "
    "`plugins.amir_project.components` includes `\"{gate}\"`. If the manifest is "
    "missing or `\"{gate}\"` is not listed, STOP — do not execute this command — "
    "and tell the user to enable the `{gate}` component via `/amir:configure_project`.\n"
)


def prepend_gate(text: str, gate: str) -> str:
    block = GATE_TEMPLATE.format(gate=gate)
    m = re.match(r"^---\r?\n.*?^---\r?\n", text, re.S | re.M)
    if m:
        return text[:m.end()] + "\n" + block + text[m.end():]
    return block + "\n" + text


# ------------------------------------------------------------------ file helpers

created: dict[str, int] = {}


def bump(cat: str, n: int = 1) -> None:
    created[cat] = created.get(cat, 0) + n


def clean(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def write(path: Path, text: str, cat: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    bump(cat)


def copy_tree_count(src: Path, dst: Path, cat: str) -> None:
    shutil.copytree(src, dst, dirs_exist_ok=True)
    bump(cat, sum(1 for p in dst.rglob("*") if p.is_file()))


# ------------------------------------------------------------------- migration


def migrate_harness() -> None:
    cmd_dir = DST / "commands" / "harness"
    clean(cmd_dir)
    for name in KEPT_HARNESS:
        src = SRC_HARNESS / "commands" / f"{name}.md"
        text = src.read_text(encoding="utf-8")
        text = strip_frontmatter_name(text)
        write(cmd_dir / f"{name}.md", text, "harness commands")

    for alias, (replacement, note) in DEPRECATED_ALIASES.items():
        body = f"""---
description: DEPRECATED alias
---

# /amir:{alias} (DEPRECATED)

This command is a deprecated alias. Do the following, in order:

1. Print this warning to the user verbatim:

   > WARNING: `/amir:{alias}` is deprecated and will be removed in amir_project 1.0.
   > Use `{replacement}` instead ({note}).

2. Then invoke the replacement: run `{replacement}` with the same arguments
   (`$ARGUMENTS`) and continue there. Do not perform any other work under the
   old name.
"""
        write(cmd_dir / f"{alias}.md", body, "harness deprecated aliases")

    # kept skills
    for name in KEPT_HARNESS:
        src = SRC_HARNESS / "skills" / name
        if not src.is_dir():
            print(f"WARN: harness skill missing in source: {name}")
            continue
        dst = DST / "skills" / name
        clean(dst)
        copy_tree_count(src, dst, "harness skills files")
        skill_md = dst / "SKILL.md"
        if skill_md.is_file():
            text = set_frontmatter_name(skill_md.read_text(encoding="utf-8"), name)
            skill_md.write_text(text, encoding="utf-8", newline="\n")

    # support dirs
    for d in HARNESS_SUPPORT_DIRS:
        src = SRC_HARNESS / d
        if not src.is_dir():
            print(f"WARN: harness support dir missing: {d}")
            continue
        dst = DST / d
        clean(dst)
        copy_tree_count(src, dst, f"harness support ({d})")

    for f in HARNESS_ROOT_FILES:
        src = SRC_HARNESS / f
        shutil.copy2(src, DST / f)
        bump("harness root files")

    # hooks.json: fix broken secrets_scan path, then merge terraform hook
    hooks = json.loads((SRC_HARNESS / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    for entry in hooks["hooks"].get("PreToolUse", []):
        for h in entry.get("hooks", []):
            h["command"] = h["command"].replace(
                "${CLAUDE_PLUGIN_ROOT}/../../tools/secrets_scan.js",
                "${CLAUDE_PLUGIN_ROOT}/tools/secrets_scan.js",
            )
    tf_hooks = json.loads((PLUGINS / "amir-terraform" / "hooks" / "hooks.json")
                          .read_text(encoding="utf-8"))
    for entry in tf_hooks["hooks"]["PreToolUse"]:
        for h in entry["hooks"]:
            h["command"] = h["command"].replace(
                "${CLAUDE_PLUGIN_ROOT}/scripts/hook_block_tf.py",
                "${CLAUDE_PLUGIN_ROOT}/scripts/terraform/hook_block_tf.py",
            )
        hooks["hooks"]["PreToolUse"].append(entry)
    hooks_dir = DST / "hooks"
    clean(hooks_dir)
    write(hooks_dir / "hooks.json", json.dumps(hooks, indent=2) + "\n", "hooks")


def migrate_satellites() -> None:
    for gd, cfg in GROUPS.items():
        src_plugin = PLUGINS / cfg["src"]
        cmd_dir = DST / "commands" / gd
        clean(cmd_dir)
        for old, new in cfg["cmds"].items():
            src = src_plugin / "commands" / f"{old}.md"
            text = src.read_text(encoding="utf-8")
            text = strip_frontmatter_name(text)
            text = apply_common_renames(text)
            text = fix_script_paths(text, gd)
            if gd == "prisma":
                text = fix_prisma_docs_path(text)
                text = text.replace("skills/*/references", "skills/prisma_*/references")
            text = prepend_gate(text, cfg["gate"])
            write(cmd_dir / f"{new}.md", text, f"{gd} commands")

        # skills
        for old, new in cfg["skills"].items():
            src = src_plugin / "skills" / old
            if not src.is_dir():
                print(f"WARN: skill missing in source: {cfg['src']}/skills/{old}")
                continue
            dst = DST / "skills" / new
            clean(dst)
            copy_tree_count(src, dst, f"{gd} skills files")
            for md in dst.rglob("*.md"):
                text = md.read_text(encoding="utf-8")
                text = apply_common_renames(text)
                text = fix_script_paths(text, gd)
                if gd == "prisma":
                    text = fix_prisma_docs_path(text)
                if md.name == "SKILL.md" and md.parent == dst:
                    text = set_frontmatter_name(text, new)
                md.write_text(text, encoding="utf-8", newline="\n")

        # scripts — only command-namespace fixes; internal domain-id dicts in .py
        # files keep their original ids (SKILL_DIRS in patch_prisma_scripts maps
        # them to the renamed skill folders)
        src_scripts = src_plugin / "scripts"
        if src_scripts.is_dir():
            dst_scripts = DST / "scripts" / gd
            clean(dst_scripts)
            copy_tree_count(src_scripts, dst_scripts, f"{gd} scripts files")
            for py in list(dst_scripts.rglob("*.py")) + list(dst_scripts.rglob("*.md")):
                text = py.read_text(encoding="utf-8")
                for old, new in NS_MAP.items():
                    text = text.replace(old, new)
                py.write_text(text, encoding="utf-8", newline="\n")

    # litellm bin/ -> scripts/litellm/
    lite_src = PLUGINS / "amir-litellm" / "bin"
    lite_dst = DST / "scripts" / "litellm"
    clean(lite_dst)
    copy_tree_count(lite_src, lite_dst, "litellm scripts files")

    # prisma agents -> agents/ (harness agents already copied; filenames disjoint)
    prisma_agents = PLUGINS / "amir-prisma" / "agents"
    if prisma_agents.is_dir():
        for f in prisma_agents.glob("*.md"):
            text = f.read_text(encoding="utf-8")
            text = apply_common_renames(text)
            text = fix_script_paths(text, "prisma")
            text = fix_prisma_docs_path(text)
            write(DST / "agents" / f.name, text, "prisma agents")


def patch_prisma_scripts() -> None:
    skill_dirs = GROUPS["prisma"]["skills"]
    mapping_src = ("SKILL_DIRS = {  # old domain id -> renamed skill folder (amir_project)\n"
                   + "".join(f"    {old!r}: {new!r},\n" for old, new in skill_dirs.items())
                   + "}\n")

    ingest = DST / "scripts" / "prisma" / "ingest.py"
    text = ingest.read_text(encoding="utf-8")
    text = text.replace(
        "PLUGIN_ROOT = Path(__file__).resolve().parents[1]",
        "PLUGIN_ROOT = Path(__file__).resolve().parents[2]  # scripts/prisma/ -> plugin root",
    )
    text = text.replace(
        'DEFAULT_DOCS = Path(r"E:\\PC3_Shared\\Palo\\Documents\\Markdowns Prisma SASE")',
        'DEFAULT_DOCS = Path(os.environ.get("PRISMA_DOCS_PATH", '
        'r"E:\\PC3_Shared\\Palo\\Documents\\Markdowns Prisma SASE"))',
    )
    text = text.replace('SKILLS_ROOT = PLUGIN_ROOT / "skills"',
                        'SKILLS_ROOT = PLUGIN_ROOT / "skills"\n\n' + mapping_src)
    text = text.replace('ref = SKILLS_ROOT / domain / "references"',
                        'ref = SKILLS_ROOT / SKILL_DIRS.get(domain, domain) / "references"')
    text = text.replace(
        '"Set `PRISMA_DOCS_PATH` (default `E:\\\\PC3_Shared\\\\Palo\\\\Documents'
        '\\\\Markdowns Prisma SASE`).",',
        '"Set `PRISMA_DOCS_PATH` (machine-specific default documented in the '
        'amir_project plugin README, section \'Prisma docs corpus\').",',
    )
    ingest.write_text(text, encoding="utf-8", newline="\n")

    gen = DST / "scripts" / "prisma" / "gen_skills.py"
    text = gen.read_text(encoding="utf-8")
    text = text.replace(
        "ROOT = Path(__file__).resolve().parents[1]",
        "ROOT = Path(__file__).resolve().parents[2]  # scripts/prisma/ -> plugin root",
    )
    text = re.sub(r"^SKILLS = \{", mapping_src + "\nSKILLS = {", text, count=1, flags=re.M)
    text = text.replace('d = ROOT / "skills" / name',
                        'd = ROOT / "skills" / SKILL_DIRS.get(name, name)')
    text = text.replace("TEMPLATE.format(name=name,",
                        "TEMPLATE.format(name=SKILL_DIRS.get(name, name),")
    text = fix_prisma_docs_path(text)
    gen.write_text(text, encoding="utf-8", newline="\n")


def write_plugin_json() -> None:
    plugin = {
        "name": "amir",
        "version": "1.0.0",
        "description": ("Amir project plugin — project-selected components "
                        "(harness, cloud/security/network groups, dev tools)"),
        "author": {"name": "Amir", "email": "amir.rashidi2016@gmail.com"},
        "keywords": ["multi-agent", "harness", "cloud", "security", "network",
                     "project-scoped"],
        "mcpServers": {
            "aws-mcp": {
                "command": "uvx",
                "args": ["mcp-proxy-for-aws@1.6.3",
                         "https://aws-mcp.us-east-1.api.aws/mcp",
                         "--metadata", "AWS_REGION=${env:AWS_REGION}"],
            },
            "azure-mcp": {
                "command": "npx",
                "args": ["-y", "@azure/mcp@latest", "server", "start"],
            },
            "litellm": {
                "command": "python",
                "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/litellm/litellm_mcp.py"],
            },
            "elastic-agent-builder": {
                "command": "npx",
                "args": ["-y", "mcp-remote",
                         "${env:ELASTIC_KIBANA_URL}/api/agent_builder/mcp",
                         "--header", "Authorization:${env:ELASTIC_AUTH_HEADER}"],
            },
        },
    }
    write(DST / ".claude-plugin" / "plugin.json",
          json.dumps(plugin, indent=2, ensure_ascii=False) + "\n", "plugin.json")


def write_readme() -> None:
    groups_rows = "\n".join(
        f"| `{gd}` (manifest id `{cfg['gate']}`) | "
        + ", ".join(f"`/amir:{n}`" for n in sorted(cfg["cmds"].values()))
        + f" | `{cfg['src']}` |"
        for gd, cfg in GROUPS.items()
    )
    aliases_rows = "\n".join(
        f"| `/amir:{a}` | `{r}` ({n}) |" for a, (r, n) in DEPRECATED_ALIASES.items()
    )
    retired_list = "\n".join(f"- `/amir:{r}`" for r in RETIRED)
    harness_list = ", ".join(f"`/amir:{c}`" for c in KEPT_HARNESS)
    text = f"""# amir_project

Marketplace entry ID `amir_project`; plugin.json name `amir` (all commands surface
as `/amir:<name>`). NEVER auto-enabled — installed per project (`--scope project`)
or rendered as a component subset during `/amir:create_project` /
`/amir:onboard_project` (both live in the amir_system plugin).

## Structure

- `commands/<group>/<name>.md` — group dirs are organizational only; the command
  name is the filename.
- `skills/<name>/SKILL.md` — underscore skill names; large `references/` corpora
  kept intact.
- `scripts/<group>/` — per-group helper scripts (paths referenced as
  `${{CLAUDE_PLUGIN_ROOT}}/scripts/<group>/...`).
- `agents/`, `core/`, `templates/`, `tools/`, `schemas/`, `rules/`, `bin/` —
  harness support content migrated from the old `amir` plugin.
- `hooks/hooks.json` — secrets PreToolUse scan (harness) + terraform
  plan/apply guard.

## Component gating

Every non-harness command starts with a component gate: it reads
`.amir/project.yaml` and requires `plugins.amir_project.components` to include
its group id (e.g. `"aws"`, `"cortex-xdr"`). If the manifest is missing or the
group is not enabled the command refuses and points to `/amir:configure_project`.
Harness commands are gated by the plugin being enabled for the project at all.

## Groups

| Group (dir) | Commands | Origin plugin |
|---|---|---|
| `harness` | {harness_list} | `amir` |
{groups_rows}

New tool groups (serena, context7, semgrep, langfuse, openhands, worktrees,
swebench, terminalbench) are built separately — see
`design/SPEC-amir_project-tools.md`.

## Deprecated aliases (removed at amir_project 1.0)

| Alias | Replacement |
|---|---|
{aliases_rows}

## Retired commands

Retired because they violate the project-scope principle (they operated on
user/system scope). No aliases are provided:

{retired_list}

## Prisma docs corpus

Prisma skills and `scripts/prisma/ingest.py` read the live corpus location from
the environment variable `PRISMA_DOCS_PATH`. The historical default —
machine-specific, documented once here only — was:

```
{PRISMA_LITERAL}
```

Set `PRISMA_DOCS_PATH` before running `/amir:prisma_update_index` if the corpus
lives elsewhere (or on any other machine). If the variable is unset and the
default path does not exist, prisma skills fall back to the baked
`skills/prisma_*/references/` layer.

## MCP servers

Declared in `.claude-plugin/plugin.json` and loaded only when the plugin (or a
rendered subset containing the group) is enabled: `aws-mcp` (aws), `azure-mcp`
(azure), `litellm` (litellm, `scripts/litellm/litellm_mcp.py`),
`elastic-agent-builder` (elastic). Credentials always via `${{env:...}}`
references — never inlined.
"""
    write(DST / "README.md", text, "README")


# ------------------------------------------------------------------ verification


def verify() -> bool:
    ok = True
    print("\n================ VERIFICATION ================")

    expected = set(KEPT_HARNESS) | set(DEPRECATED_ALIASES)
    for cfg in GROUPS.values():
        expected |= set(cfg["cmds"].values())

    owned_dirs = {"harness"} | set(GROUPS)
    all_cmd_files = sorted((DST / "commands").rglob("*.md"))
    owned_files = [f for f in all_cmd_files
                   if f.relative_to(DST / "commands").parts[0] in owned_dirs]
    basenames: dict[str, list[str]] = {}
    for f in all_cmd_files:
        basenames.setdefault(f.stem, []).append(str(f.relative_to(DST)))

    missing = sorted(n for n in expected if n not in basenames)
    extra_owned = sorted(f.stem for f in owned_files if f.stem not in expected)
    dups = {n: v for n, v in basenames.items() if len(v) > 1}
    print(f"[1] expected command files (this migration's groups): {len(expected)}; "
          f"found in owned group dirs: {len(owned_files)}; "
          f"total commands/**/*.md incl. other agent's groups: {len(all_cmd_files)}")
    if extra_owned:
        ok = False
        print(f"    FAIL unexpected files in owned dirs: {extra_owned}")
    if missing:
        ok = False
        print(f"    FAIL missing: {missing}")
    else:
        print("    PASS every expected command file exists")
    if dups:
        ok = False
        print(f"    FAIL duplicate basenames: {dups}")
    else:
        print("    PASS no duplicate basenames across commands/**/*.md")

    ns_re = re.compile(r"/amir-[a-z0-9][a-z0-9-]*:")
    offenders = []
    for f in DST.rglob("*"):
        if not f.is_file() or "_migration" in f.parts:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        for m in ns_re.finditer(text):
            offenders.append((str(f.relative_to(DST)), m.group(0)))
        if "/prisma:" in text:
            offenders.append((str(f.relative_to(DST)), "/prisma:"))
    print(f"[2] old-namespace references (/amir-<x>:, /prisma:):")
    if offenders:
        ok = False
        for path, tok in offenders:
            print(f"    FAIL {path}: {tok}")
    else:
        print("    PASS none found")

    allow = {
        Path("README.md"),                       # documented-default note
        Path("scripts/prisma/ingest.py"),        # instructed env-var fallback
    }
    prisma_hits = []
    for f in DST.rglob("*"):
        if not f.is_file() or "_migration" in f.parts:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        if "Markdowns Prisma SASE" in text:
            rel = f.relative_to(DST)
            if rel in allow:
                continue
            if "PC3_Shared" not in text:
                # corpus name used as a document *title* in baked reference data
                # (index.json/summary.md) — no filesystem path present
                prisma_hits.append((str(rel), "data-title only (no path)"))
                continue
            prisma_hits.append((str(rel), "UNEXPECTED"))
    print(f"[3] 'Markdowns Prisma SASE' outside documented-default notes:")
    unexpected = [h for h in prisma_hits if h[1] == "UNEXPECTED"]
    for rel, kind in prisma_hits:
        print(f"    {'FAIL' if kind == 'UNEXPECTED' else 'INFO'} {rel}: {kind}")
    if unexpected:
        ok = False
    else:
        print("    PASS no unexpected occurrences "
              "(allowlisted: README.md note, ingest.py env fallback, "
              "index.json document titles containing the corpus name but no path)")

    checks = [
        ("tools/secrets_scan.js", DST / "tools" / "secrets_scan.js"),
        ("scripts/terraform/hook_block_tf.py", DST / "scripts" / "terraform" / "hook_block_tf.py"),
        ("scripts/litellm/litellm_mcp.py", DST / "scripts" / "litellm" / "litellm_mcp.py"),
        ("hooks/hooks.json", DST / "hooks" / "hooks.json"),
        (".claude-plugin/plugin.json", DST / ".claude-plugin" / "plugin.json"),
    ]
    print("[4] critical files:")
    for label, p in checks:
        exists = p.is_file()
        ok &= exists
        print(f"    {'PASS' if exists else 'FAIL'} {label}")

    hooks_text = (DST / "hooks" / "hooks.json").read_text(encoding="utf-8")
    fixed = "${CLAUDE_PLUGIN_ROOT}/tools/secrets_scan.js" in hooks_text \
        and "../../tools" not in hooks_text \
        and "scripts/terraform/hook_block_tf.py" in hooks_text
    ok &= fixed
    print(f"    {'PASS' if fixed else 'FAIL'} hooks.json secrets path fixed + "
          "terraform hook merged")

    gate_missing = []
    for gd, cfg in GROUPS.items():
        for new in cfg["cmds"].values():
            text = (DST / "commands" / gd / f"{new}.md").read_text(encoding="utf-8")
            if "Component gate (amir_project)" not in text \
                    or f'"{cfg["gate"]}"' not in text:
                gate_missing.append(f"{gd}/{new}")
    print("[5] tool-scope gate present in every satellite command:")
    if gate_missing:
        ok = False
        print(f"    FAIL missing gate: {gate_missing}")
    else:
        print("    PASS all satellite commands gated")

    print("==============================================")
    print("VERIFICATION:", "ALL PASS" if ok else "FAILURES PRESENT")
    return ok


def main() -> int:
    for p in [SRC_HARNESS] + [PLUGINS / c["src"] for c in GROUPS.values()]:
        if not p.is_dir():
            print(f"FATAL: source missing: {p}")
            return 2
    migrate_harness()
    migrate_satellites()
    patch_prisma_scripts()
    write_plugin_json()
    write_readme()
    print("\n--- files created/modified per category ---")
    for cat in sorted(created):
        print(f"{cat}: {created[cat]}")
    return 0 if verify() else 1


if __name__ == "__main__":
    sys.exit(main())
