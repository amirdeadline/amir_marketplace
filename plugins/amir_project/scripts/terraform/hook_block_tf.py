#!/usr/bin/env python3
import json, re, sys
from pathlib import Path


def terraform_component_enabled() -> bool:
    # Hook fires for every Bash call whenever the plugin is enabled; only enforce
    # in projects whose .amir/project.yaml selects the terraform component.
    # Dependency-free check (no pyyaml guaranteed at hook time): look for
    # "- terraform" as a list item in the manifest.
    d = Path.cwd()
    for p in [d, *d.parents]:
        m = p / ".amir" / "project.yaml"
        if m.is_file():
            try:
                text = m.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                return False
            return bool(re.search(r'^\s*-\s*["\']?terraform["\']?\s*$', text, re.M))
    return False


if not terraform_component_enabled():
    sys.exit(0)

raw = sys.stdin.read().lstrip("﻿")
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
