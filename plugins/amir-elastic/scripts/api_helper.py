#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, ssl, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, mask_secret, print_command, require_env

def call(method, path, body=None):
    env = require_env(["ELASTIC_BASE_URL", "ELASTIC_API_KEY"])
    base = env["ELASTIC_BASE_URL"].rstrip("/")
    key = env["ELASTIC_API_KEY"]
    url = base + path
    print(f"key={mask_secret(key)}")
    print_command(f"{method} {url}")
    data = None if body is None else json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Authorization", f"ApiKey {key}")
    r.add_header("Content-Type", "application/json")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(r, context=ctx, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preflight", "search", "cat", "delete-index"])
    ap.add_argument("--index", default="*")
    ap.add_argument("--body", default='{"size":5,"query":{"match_all":{}}}')
    args = ap.parse_args()
    if args.mode == "preflight":
        print(call("GET", "/")[:2000]); return
    if args.mode == "cat":
        print(call("GET", "/_cat/indices?v")[:4000]); return
    if args.mode == "search":
        print(call("POST", f"/{args.index}/_search", json.loads(args.body))[:8000]); return
    if args.mode == "delete-index":
        print_command(f"DELETE /{args.index}")
        if not confirm(f"DELETE INDEX {args.index}", typed=f"DELETE {args.index}"):
            sys.exit(3)
        print(call("DELETE", f"/{args.index}"))

if __name__ == "__main__":
    main()
