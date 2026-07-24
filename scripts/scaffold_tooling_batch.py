#!/usr/bin/env python3
"""
Scaffold the tooling-plugins batch into ../<name>/ and pack into plugins/<name>/.

Patterns (verified at build time 2026-07-14):
  aws      — MCP: mcp-proxy-for-aws → https://aws-mcp.us-east-1.api.aws/mcp (+ CLI)
  azure    — MCP: npx -y @azure/mcp@latest server start (+ az CLI)
  elastic  — optional remote Kibana Agent Builder MCP; Knowledge+API primary
  splunk   — Knowledge+API (Splunk MCP is an on-platform app, not a local npm)
  others   — CLI-wrap and/or Knowledge+API as specified
"""
from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path

PLUGINS_ROOT = Path(__file__).resolve().parents[2]  # e:\PC3_Shared\Plugins
MARKET = Path(__file__).resolve().parents[1]
OUT_PLUGINS = MARKET / "plugins"

# ---------------------------------------------------------------------------
# Shared snippets
# ---------------------------------------------------------------------------

SAFETY_PY = r'''#!/usr/bin/env python3
"""Shared safety helpers: masking, confirm gates, destructive patterns."""
from __future__ import annotations

import os
import re
import sys
from typing import Iterable

DESTRUCTIVE_REMOTE = re.compile(
    r"\b(rm\s+-rf|mkfs|shutdown|reboot|dd\s+if=|:(){:|:&};:)\b",
    re.I,
)

def mask_secret(value: str | None) -> str:
    if not value:
        return "(missing)"
    v = value.strip()
    if len(v) <= 4:
        return "****"
    return f"****{v[-4:]}"

def require_env(names: Iterable[str]) -> dict[str, str]:
    missing = [n for n in names if not (os.environ.get(n) or "").strip()]
    if missing:
        print("REFUSING — missing env var(s) by name only:", ", ".join(missing), file=sys.stderr)
        raise SystemExit(2)
    return {n: os.environ[n].strip() for n in names}

def confirm(prompt: str, *, typed: str | None = None) -> bool:
    print(prompt)
    if typed:
        print(f'Type exactly: {typed}')
        ans = input("> ").strip()
        return ans == typed
    ans = input("Proceed? [y/N] > ").strip().lower()
    return ans in {"y", "yes"}

def print_command(cmd: str | list[str]) -> None:
    if isinstance(cmd, list):
        import shlex
        try:
            s = " ".join(shlex.quote(c) for c in cmd)
        except Exception:
            s = " ".join(cmd)
    else:
        s = cmd
    print("EXACT COMMAND/REQUEST:")
    print(s)
'''

HOOKS_TF = {
    "hooks": {
        "PreToolUse": [
            {
                "matcher": "Bash|Shell",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python \"${CLAUDE_PLUGIN_ROOT}/scripts/hook_block_tf.py\""
                    }
                ]
            }
        ]
    }
}

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip("\n") if content.startswith("\n") else content, encoding="utf-8")
    if not content.endswith("\n"):
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")


def plugin_json(name: str, desc: str, version: str = "0.1.0", mcp: dict | None = None) -> dict:
    d = {
        "name": name,
        "version": version,
        "description": desc,
        "author": {"name": "Amir", "email": "amir.rashidi2016@gmail.com"},
        "keywords": [name],
    }
    if mcp:
        d["mcpServers"] = mcp
    return d


def skill(name: str, description: str, body: str) -> str:
    return f"""---
name: {name}
description: >-
  {description}
---

{body}
"""


def cmd(name: str, description: str, body: str) -> str:
    return f"""---
name: {name}
description: {description}
---

{body}
"""


# ---------------------------------------------------------------------------
# Plugin definitions
# ---------------------------------------------------------------------------

PLUGINS: list[dict] = []


def add(p: dict) -> None:
    PLUGINS.append(p)


# --- paloalto ---
add({
    "name": "paloalto",
    "category": "security",
    "tags": ["pan-os", "panorama", "globalprotect", "firewall"],
    "pattern": "Knowledge+API + CLI-wrap",
    "desc": "PAN-OS / Panorama / GlobalProtect companion to prisma (SASE/SCM). Knowledge skills + API helper; mutations confirm-first.",
    "prereq": "Optional: pan-os-python or curl; env PANOS_HOST, PANOS_API_KEY (or user/password for keygen).",
    "env": ["PANOS_HOST", "PANOS_API_KEY"],
    "skills": {
        "panos-ngfw": ("PAN-OS NGFW policy, profiles, NAT, zones, HA, best-practice rulebase.",
            "# panos-ngfw\n\nCover security rules, profiles, NAT, zones, HA.\nPrefer live pan.dev / docs.paloaltonetworks.com for version-specific facts.\nLabel VERIFIED | INFERRED | ASSUMED.\nCompanion to `prisma` (SASE) — no baked corpus overlap."),
        "panorama": ("Panorama device groups, templates, config push.",
            "# panorama\n\nDevice groups, templates, template stacks, commit/push implications.\nConfirm before any commit/push."),
        "panos-api": ("PAN-OS XML API + REST: keygen, op/show, config get; set/edit/delete/commit confirm-first.",
            "# panos-api\n\nGenerate XML/REST calls. Execute read (type=op, config/action=get) freely.\nAny set/edit/delete/commit: print exact call and confirm first.\nEnv: PANOS_HOST, PANOS_API_KEY (masked ****last4)."),
        "globalprotect": ("GlobalProtect portal/gateway, HIP, auth sequences (on-prem/Panorama context).",
            "# globalprotect\n\nPortal/gateway design, HIP objects, auth. Cross-link prisma-access for SASE MU."),
        "panos-troubleshooting": ("Session/flow logic, show command playbook, tech-support-file guidance.",
            "# panos-troubleshooting\n\nSymptom → session → policy/NAT → route. Collect show session / show counter evidence before guessing."),
    },
    "commands": {
        "preflight": ("Validate PAN-OS API reachability / identity.",
            "# /paloalto:preflight\n\nRun `python \"${CLAUDE_PLUGIN_ROOT}/scripts/api_helper.py\" preflight`.\nMask keys. Refuse further mutating help if unauthenticated."),
        "api": ("Generate or run a PAN-OS API call (reads free; writes confirm).",
            "# /paloalto:api\n\nArgs: `$ARGUMENTS`\nUse `scripts/api_helper.py`. Print exact request. Confirm set/edit/delete/commit."),
        "ask": ("Route a PAN-OS/Panorama question to the right skill.",
            "# /paloalto:ask\n\nQuestion: `$ARGUMENTS`\nPick skill; cite sources; honesty labels."),
    },
    "scripts": {
        "api_helper.py": r'''#!/usr/bin/env python3
"""PAN-OS XML API helper — reads free; writes confirm-first."""
from __future__ import annotations
import argparse, os, sys, urllib.parse, urllib.request, ssl
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, mask_secret, print_command, require_env

MUTATING = {"set", "edit", "delete", "rename", "move", "complete", "commit"}

def call(host: str, key: str, params: dict) -> str:
    q = urllib.parse.urlencode(params)
    url = f"https://{host}/api/?{q}"
    print_command(url.replace(urllib.parse.quote(key), mask_secret(key)))
    req = urllib.request.Request(url)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")[:8000]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preflight", "op", "config"])
    ap.add_argument("--cmd", default="")
    ap.add_argument("--xpath", default="")
    ap.add_argument("--element", default="")
    ap.add_argument("--action", default="get")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()
    env = require_env(["PANOS_HOST", "PANOS_API_KEY"])
    host, key = env["PANOS_HOST"], env["PANOS_API_KEY"]
    print(f"host={host} key={mask_secret(key)}")
    if args.mode == "preflight":
        print(call(host, key, {"type": "op", "cmd": "<show><system><info></info></system></show>", "key": key})[:2000])
        return
    if args.mode == "op":
        params = {"type": "op", "cmd": args.cmd, "key": key}
        print(call(host, key, params))
        return
    action = args.action
    if action in MUTATING and not args.yes:
        print_command(f"type=config action={action} xpath={args.xpath}")
        if not confirm("Mutating PAN-OS config API call."):
            sys.exit(3)
    params = {"type": "config", "action": action, "xpath": args.xpath, "key": key}
    if args.element:
        params["element"] = args.element
    print(call(host, key, params))

if __name__ == "__main__":
    main()
''',
    },
    "always_on_tokens": "~1.5k (thin skills; references on demand)",
    "safety": "API set/edit/delete/commit confirm-first. Companion to prisma; no corpus overlap.",
})


# --- aws ---
add({
    "name": "aws",
    "category": "infra",
    "tags": ["aws", "mcp", "cli", "well-architected"],
    "pattern": "MCP (official AWS MCP Server) + CLI-wrap fallback",
    "desc": "AWS via official managed MCP (mcp-proxy-for-aws) plus aws CLI fallback. Preflight STS; mutations confirm-first.",
    "prereq": "uv/uvx + AWS credentials (same as CLI). Optional: aws CLI on PATH.",
    "env": ["AWS_REGION", "AWS_PROFILE (optional)"],
    "mcp": {
        "aws-mcp": {
            "command": "uvx",
            "args": [
                "mcp-proxy-for-aws@1.6.3",
                "https://aws-mcp.us-east-1.api.aws/mcp",
                "--metadata",
                "AWS_REGION=${env:AWS_REGION}"
            ]
        }
    },
    "skills": {
        "aws-cli-safety": ("Safe aws CLI usage: preflight identity, confirm mutations, never store keys in files.",
            "# aws-cli-safety\n\n1. Always run `aws sts get-caller-identity` first.\n2. Reads (describe/list/get) free.\n3. Mutations: print exact CLI and confirm.\n4. Prefer least-privilege profile. Never write keys to files."),
        "aws-well-architected": ("Well-Architected review methodology + cost-trap checks.",
            "# aws-well-architected\n\nReview against pillars. Flag common cost traps (idle NAT, unattached EBS, oversized RD). Cite AWS docs."),
    },
    "commands": {
        "whoami": ("Show active AWS account/role/region via STS.",
            "# /aws:whoami\n\nRun `python \"${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py\"`.\nRefuse other AWS actions if this fails."),
        "cli": ("Run an aws CLI command with confirm-first for mutations.",
            "# /aws:cli\n\nArgs: `$ARGUMENTS`\nUse scripts/cli_wrap.py. Print exact command. Confirm create/delete/modify/put/update/attach."),
    },
    "scripts": {
        "preflight.py": r'''#!/usr/bin/env python3
import json, shutil, subprocess, sys
if not shutil.which("aws"):
    print("PARTIALLY DOABLE — aws CLI not on PATH. Install AWS CLI v2: https://docs.aws.amazon.com/cli/")
    print("MCP path may still work via uvx mcp-proxy-for-aws if credentials exist.")
    sys.exit(2)
r = subprocess.run(["aws", "sts", "get-caller-identity", "--output", "json"], capture_output=True, text=True)
if r.returncode != 0:
    print("REFUSING — unauthenticated:", r.stderr.strip()[:500])
    sys.exit(2)
print(r.stdout)
''',
        "cli_wrap.py": r'''#!/usr/bin/env python3
import argparse, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, print_command
MUT = re.compile(r"\b(create|delete|put|update|modify|attach|detach|terminate|revoke|authorize|run-instances|stop-instances)\b", re.I)
ap = argparse.ArgumentParser(); ap.add_argument("args", nargs=argparse.REMAINDER); a = ap.parse_args()
args = a.args[1:] if a.args and a.args[0] == "--" else a.args
if not shutil.which("aws"):
    print("aws CLI missing"); sys.exit(2)
cmd = ["aws", *args]
print_command(cmd)
line = " ".join(cmd)
if MUT.search(line):
    if not confirm("Mutating AWS CLI command."):
        sys.exit(3)
raise SystemExit(subprocess.call(cmd))
''',
    },
    "always_on_tokens": "~1.2k (+ MCP tools discovered at runtime)",
    "safety": "STS preflight. Mutations confirm. Keys never in files. Official MCP verified: aws/agent-toolkit-for-aws mcp-proxy-for-aws@1.6.3.",
    "verified": "https://github.com/aws/agent-toolkit-for-aws",
})


# --- azure ---
add({
    "name": "azure",
    "category": "infra",
    "tags": ["azure", "mcp", "networking", "cli"],
    "pattern": "MCP (Azure MCP Server) + CLI-wrap (az)",
    "desc": "Azure via official Azure MCP Server (@azure/mcp) and az CLI. Preflight account show; mutations confirm-first.",
    "prereq": "Node/npx + az login. Official: microsoft/mcp Azure.Mcp.Server.",
    "env": ["AZURE_SUBSCRIPTION_ID (optional)"],
    "mcp": {
        "azure-mcp": {
            "command": "npx",
            "args": ["-y", "@azure/mcp@latest", "server", "start"]
        }
    },
    "skills": {
        "azure-networking": ("VNets, peering, ExpressRoute/VPN, NSGs, hub-spoke hybrid connectivity.",
            "# azure-networking\n\nHub-spoke, peering, ER/VPN, NSG/ASG design. Prefer read via `az network ... show/list`."),
        "azure-core": ("Subscriptions, resource groups, RBAC.",
            "# azure-core\n\nRG lifecycle, role assignments. Mutations confirm-first."),
        "azure-monitor": ("Log Analytics and KQL basics (non-Sentinel).",
            "# azure-monitor\n\nWorkspace queries, diagnostic settings. Deep hunting → install `sentinel` plugin."),
    },
    "commands": {
        "whoami": ("az account show preflight.",
            "# /azure:whoami\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py\"`"),
        "cli": ("az CLI wrap with confirm for mutations.",
            "# /azure:cli\n\n`$ARGUMENTS` → scripts/cli_wrap.py"),
    },
    "scripts": {
        "preflight.py": r'''#!/usr/bin/env python3
import json, shutil, subprocess, sys
if not shutil.which("az"):
    print("PARTIALLY DOABLE — az not on PATH. https://learn.microsoft.com/cli/azure/install-azure-cli")
    sys.exit(2)
r = subprocess.run(["az", "account", "show", "-o", "json"], capture_output=True, text=True)
if r.returncode != 0:
    print("REFUSING — unauthenticated. Run: az login"); print(r.stderr[:500]); sys.exit(2)
print(r.stdout)
''',
        "cli_wrap.py": r'''#!/usr/bin/env python3
import argparse, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, print_command
MUT = re.compile(r"\b(create|delete|update|set|remove|assign|detach|stop|start|restart)\b", re.I)
ap = argparse.ArgumentParser(); ap.add_argument("args", nargs=argparse.REMAINDER); a = ap.parse_args()
args = a.args[1:] if a.args and a.args[0]=="--" else a.args
cmd=["az", *args]; print_command(cmd)
if MUT.search(" ".join(cmd)):
    if not confirm("Mutating Azure CLI command."): sys.exit(3)
raise SystemExit(subprocess.call(cmd))
''',
    },
    "always_on_tokens": "~1.3k",
    "safety": "az account show preflight. Mutations confirm. Verified MCP: npx @azure/mcp server start (microsoft/mcp).",
})


# --- terraform ---
add({
    "name": "terraform",
    "category": "infra",
    "tags": ["terraform", "iac", "plan", "apply"],
    "pattern": "CLI-wrap + knowledge + PreToolUse hook",
    "desc": "Terraform plan/validate/fmt/init safe; apply/destroy confirm-first with typed destroy confirm. Blocks bare -auto-approve via hook.",
    "prereq": "terraform on PATH",
    "env": [],
    "hooks": True,
    "skills": {
        "terraform-review": ("State hygiene, modules, secrets, drift, provider pinning.",
            "# terraform-review\n\nCheck remote state locking, no secrets in tfstate, pinned providers, module boundaries, drift via plan."),
    },
    "commands": {
        "plan": ("terraform plan (safe).", "# /tf:plan\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/tf.py\" plan -- $ARGUMENTS`"),
        "validate": ("terraform validate.", "# /tf:validate\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/tf.py\" validate`"),
        "fmt": ("terraform fmt.", "# /tf:fmt\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/tf.py\" fmt`"),
        "init": ("terraform init.", "# /tf:init\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/tf.py\" init -- $ARGUMENTS`"),
        "apply": ("terraform apply — confirm + show plan first.", "# /tf:apply\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/tf.py\" apply -- $ARGUMENTS`"),
        "destroy": ("terraform destroy — typed confirmation required.", "# /tf:destroy\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/tf.py\" destroy -- $ARGUMENTS`"),
    },
    "scripts": {
        "tf.py": r'''#!/usr/bin/env python3
import argparse, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, print_command
if not shutil.which("terraform"):
    print("terraform not on PATH — https://developer.hashicorp.com/terraform/install"); sys.exit(2)
ap=argparse.ArgumentParser(); ap.add_argument("action", choices=["plan","validate","fmt","init","apply","destroy"]); ap.add_argument("extra", nargs=argparse.REMAINDER); a=ap.parse_args()
extra=a.extra[1:] if a.extra and a.extra[0]=="--" else a.extra
if a.action in {"plan","validate","fmt","init"}:
    cmd=["terraform", a.action, *extra]; print_command(cmd); raise SystemExit(subprocess.call(cmd))
if a.action=="apply":
    subprocess.call(["terraform","plan",*extra])
    cmd=["terraform","apply",*extra]
    if "-auto-approve" in extra:
        print("REFUSING bare -auto-approve via this wrapper; remove flag and confirm interactively."); sys.exit(3)
    print_command(cmd)
    if not confirm("Apply these Terraform changes?"): sys.exit(3)
    raise SystemExit(subprocess.call(cmd))
# destroy
subprocess.call(["terraform","plan","-destroy",*extra])
cmd=["terraform","destroy",*extra]
print_command(cmd)
if not confirm("DESTROY infrastructure.", typed="DESTROY"):
    sys.exit(3)
raise SystemExit(subprocess.call(cmd))
''',
        "hook_block_tf.py": r'''#!/usr/bin/env python3
import json, sys
raw = sys.stdin.read()
try:
    data = json.loads(raw) if raw.strip() else {}
except Exception:
    data = {}
cmd = ""
for k in ("command", "cmd", "input"):
    v = data.get(k)
    if isinstance(v, str):
        cmd = v
        break
    if isinstance(v, dict):
        cmd = str(v.get("command") or v.get("cmd") or "")
low = cmd.lower()
if "terraform" in low and ("-auto-approve" in low or "destroy" in low and "tf:destroy" not in low):
    if "/tf:apply" in low or "/tf:destroy" in low or "scripts/tf.py" in low:
        sys.exit(0)
    print("Blocked: use /tf:apply or /tf:destroy (confirming wrappers). No bare terraform apply -auto-approve / destroy.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
''',
    },
    "always_on_tokens": "~0.8k + hook",
    "safety": "Hook blocks bare auto-approve/destroy. Typed DESTROY for destroy.",
})


# --- docker ---
add({
    "name": "docker",
    "category": "infra",
    "tags": ["docker", "compose", "containers"],
    "pattern": "CLI-wrap",
    "desc": "Docker/Compose: status, logs, build, up/down; prune/volume-rm/rm -f guarded with confirmation.",
    "prereq": "docker on PATH; optional docker compose",
    "env": [],
    "skills": {
        "docker-ops": ("Safe container operations and compose workflows.",
            "# docker-ops\n\nPrefer `docker ps`, logs, compose ps. Confirm before prune, volume rm, rm -f, push to prod registries."),
    },
    "commands": {
        "status": ("docker ps / compose ps", "# /docker:status\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/docker_cli.py\" status`"),
        "logs": ("docker logs", "# /docker:logs\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/docker_cli.py\" logs -- $ARGUMENTS`"),
        "build": ("docker build", "# /docker:build\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/docker_cli.py\" build -- $ARGUMENTS`"),
        "up": ("compose up", "# /docker:up\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/docker_cli.py\" up -- $ARGUMENTS`"),
        "down": ("compose down (confirm)", "# /docker:down\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/docker_cli.py\" down -- $ARGUMENTS`"),
        "push": ("docker push (confirm)", "# /docker:push\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/docker_cli.py\" push -- $ARGUMENTS`"),
    },
    "scripts": {
        "docker_cli.py": r'''#!/usr/bin/env python3
import argparse, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, print_command
if not shutil.which("docker"):
    print("docker not on PATH"); sys.exit(2)
ap=argparse.ArgumentParser(); ap.add_argument("action"); ap.add_argument("extra", nargs=argparse.REMAINDER); a=ap.parse_args()
extra=a.extra[1:] if a.extra and a.extra[0]=="--" else a.extra
def run(cmd, need=False):
    print_command(cmd)
    if need and not confirm("Potentially destructive docker command."): sys.exit(3)
    raise SystemExit(subprocess.call(cmd))
if a.action=="status":
    subprocess.call(["docker","ps","-a"]); 
    if shutil.which("docker"):
        subprocess.call(["docker","compose","ps"])
    sys.exit(0)
maps={
 "logs": (["docker","logs",*extra], False),
 "build": (["docker","build",*extra], False),
 "up": (["docker","compose","up","-d",*extra], False),
 "down": (["docker","compose","down",*extra], True),
 "push": (["docker","push",*extra], True),
 "prune": (["docker","system","prune",*extra], True),
}
if a.action not in maps:
    print("unknown action"); sys.exit(2)
cmd, need = maps[a.action]
# Hard guard rm -f / volume rm
joined=" ".join(extra)
if "prune" in joined or "volume" in joined and "rm" in joined or "-f" in extra:
    need=True
run(cmd, need)
''',
    },
    "always_on_tokens": "~0.7k",
    "safety": "Confirm prune, volume rm, rm -f, compose down, push.",
})

print(f"Defined {len(PLUGINS)} plugins so far (batch1)...")


def emit_plugin(p: dict) -> Path:
    name = p["name"]
    src = PLUGINS_ROOT / name
    if src.exists():
        # refresh carefully — wipe generated trees only
        for sub in [".claude-plugin", ".cursor-plugin", ".codex-plugin", "skills", "commands", "scripts", "hooks"]:
            d = src / sub
            if d.exists():
                shutil.rmtree(d)
    src.mkdir(parents=True, exist_ok=True)

    mcp = p.get("mcp")
    write(src / ".claude-plugin" / "plugin.json", json.dumps(plugin_json(name, p["desc"], mcp=mcp), indent=2) + "\n")
    cursor = plugin_json(name, p["desc"], mcp=None)
    cursor["skills"] = "./skills/"
    cursor["commands"] = "./commands/"
    if mcp:
        cursor["mcpServers"] = "./mcp.json"
    if p.get("hooks"):
        cursor["hooks"] = "./hooks/hooks.json"
    write(src / ".cursor-plugin" / "plugin.json", json.dumps(cursor, indent=2) + "\n")
    write(src / ".codex-plugin" / "plugin.json", json.dumps({"name": name, "version": "0.1.0", "description": p["desc"], "skills": "./skills/"}, indent=2) + "\n")

    if mcp:
        # Claude uses ${CLAUDE_PLUGIN_ROOT}; for Cursor mcp.json keep same command forms
        write(src / "mcp.json", json.dumps({"mcpServers": mcp}, indent=2) + "\n")

    if p.get("hooks"):
        write(src / "hooks" / "hooks.json", json.dumps(HOOKS_TF, indent=2) + "\n")

    write(src / "scripts" / "safety.py", SAFETY_PY)
    for fname, body in (p.get("scripts") or {}).items():
        write(src / "scripts" / fname, body)

    for sname, (sdesc, sbody) in p["skills"].items():
        write(src / "skills" / sname / "SKILL.md", skill(sname, sdesc, sbody))
        write(src / "skills" / sname / "references" / "README.md", f"# {sname} references\n\nLoad on demand only.\n")

    for cname, (cdesc, cbody) in p["commands"].items():
        write(src / "commands" / f"{cname}.md", cmd(cname, cdesc, cbody))

    write(src / "VERSION", "0.1.0\n")
    write(src / "CHANGELOG.md", f"# Changelog\n\n## 0.1.0\n\n- Initial scaffold for amir_marketplace tooling batch.\n- Pattern: {p['pattern']}\n")
    env_list = ", ".join(f"`{e}`" for e in p.get("env") or []) or "(none — uses local CLI auth)"
    readme = f"""# {name}

{p['desc']}

## Pattern

**{p['pattern']}**

{p.get('verified') and f"Verified: {p['verified']}" or ""}

## Prerequisites

{p['prereq']}

## Environment

{env_list}

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

{p['safety']}

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

{p['always_on_tokens']}

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/{name}:`…).

## Install

Packed into `amir_marketplace` as `{name}`.
"""
    write(src / "README.md", readme)
    return src


def pack_copy(name: str) -> None:
    src = PLUGINS_ROOT / name
    dest = OUT_PLUGINS / name
    if dest.exists():
        shutil.rmtree(dest)
    def ignore(dirpath, names):
        return [n for n in names if n in {".git", ".venv", "__pycache__", ".pytest_cache", ".env"}]
    shutil.copytree(src, dest, ignore=ignore)
    print(f"packed {name} -> {dest}")


if __name__ == "__main__":
    # Continue definitions in sibling module import style — this file will be extended
    for p in PLUGINS:
        emit_plugin(p)
        pack_copy(p["name"])
    print(f"OK batch1: {len(PLUGINS)} plugins")
