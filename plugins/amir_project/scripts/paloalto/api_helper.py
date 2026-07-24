#!/usr/bin/env python3
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
