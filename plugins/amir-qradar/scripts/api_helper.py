#!/usr/bin/env python3
"""QRadar REST — verified pattern: SEC header token auth."""
from __future__ import annotations
import argparse, json, ssl, sys, urllib.parse, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, mask_secret, print_command, require_env

def call(method, path, params=None, body=None):
    env = require_env(["QRADAR_BASE_URL", "QRADAR_SEC_TOKEN"])
    base = env["QRADAR_BASE_URL"].rstrip("/")
    tok = env["QRADAR_SEC_TOKEN"]
    url = base + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    print(f"SEC={mask_secret(tok)}")
    print_command(f"{method} {url}")
    data = None if body is None else json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("SEC", tok)
    r.add_header("Accept", "application/json")
    r.add_header("Version", os_version())
    if body is not None:
        r.add_header("Content-Type", "application/json")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(r, context=ctx, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")

def os_version():
    import os
    return os.environ.get("QRADAR_API_VERSION", "20.0")  # override per deploy

def main():
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preflight", "aql", "offenses", "mutate"])
    ap.add_argument("--query", default="SELECT * FROM events LIMIT 1")
    args = ap.parse_args()
    if args.mode == "preflight":
        print(call("GET", "/api/system/about")[:3000]); return
    if args.mode == "offenses":
        print(call("GET", "/api/siem/offenses", params={"filter": "status%3DOPEN", "limit": "10"})[:8000]); return
    if args.mode == "aql":
        # create search
        print(call("POST", "/api/ariel/searches", params={"query_expression": args.query})[:8000]); return
    if not confirm("Mutating QRadar offense/rule/reference set."):
        sys.exit(3)
    print("Provide concrete path via future args — refused generic mutate without path")

if __name__ == "__main__":
    main()
