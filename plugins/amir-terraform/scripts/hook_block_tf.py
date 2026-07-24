#!/usr/bin/env python3
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
