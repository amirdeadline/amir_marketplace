#!/usr/bin/env python3
"""Splunk REST helper — search jobs (read); mutating knowledge objects confirm-first."""
from __future__ import annotations
import argparse, json, os, sys, time, urllib.parse, urllib.request, ssl
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, mask_secret, print_command, require_env

def req(method, path, data=None, params=None):
    env = require_env(["SPLUNK_BASE_URL", "SPLUNK_TOKEN"])
    base = env["SPLUNK_BASE_URL"].rstrip("/")
    token = env["SPLUNK_TOKEN"]
    url = base + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    print(f"auth={mask_secret(token)}")
    print_command(f"{method} {url}")
    body = urllib.parse.urlencode(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    r.add_header("Authorization", f"Bearer {token}")
    if data:
        r.add_header("Content-Type", "application/x-www-form-urlencoded")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(r, context=ctx, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preflight", "search", "mutate"])
    ap.add_argument("--query", default="| rest /services/server/info | head 1")
    ap.add_argument("--path", default="")
    ap.add_argument("--count", type=int, default=20)
    args = ap.parse_args()
    if args.mode == "preflight":
        print(req("GET", "/services/server/info", params={"output_mode": "json"})[:3000])
        return
    if args.mode == "search":
        # oneshot search
        print(req("POST", "/services/search/jobs/oneshot", data={
            "search": args.query if args.query.startswith("search") or args.query.startswith("|") else f"search {args.query}",
            "output_mode": "json",
            "count": str(args.count),
        })[:8000])
        return
    if not confirm("Mutating Splunk knowledge object / saved search / alert."):
        sys.exit(3)
    print(req("POST", args.path or "/services/saved/searches", data={"name": "amir_placeholder", "search": "index=_internal | head 1"}))

if __name__ == "__main__":
    main()
