#!/usr/bin/env python3
"""Cortex XDR Advanced API — headers x-xdr-auth-id + Authorization."""
from __future__ import annotations
import argparse, json, ssl, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, mask_secret, print_command, require_env

def call(path, body):
    env = require_env(["XDR_FQDN", "XDR_API_KEY_ID", "XDR_API_KEY"])
    fqdn = env["XDR_FQDN"].rstrip("/")
    if not fqdn.startswith("http"):
        fqdn = "https://" + fqdn
    url = f"{fqdn}/public_api/v1/{path.lstrip('/')}"
    print(f"key_id={mask_secret(env['XDR_API_KEY_ID'])} key={mask_secret(env['XDR_API_KEY'])}")
    print_command(f"POST {url} body={json.dumps(body)[:500]}")
    data = json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method="POST")
    r.add_header("x-xdr-auth-id", env["XDR_API_KEY_ID"])
    r.add_header("Authorization", env["XDR_API_KEY"])
    r.add_header("Content-Type", "application/json")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(r, context=ctx, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preflight", "incidents", "alerts", "endpoints", "respond"])
    ap.add_argument("--action", default="")
    ap.add_argument("--endpoint-id", default="")
    args = ap.parse_args()
    if args.mode == "preflight":
        # get_incidents with empty filter is a common probe
        print(call("incidents/get_incidents", {"request_data": {"search_from": 0, "search_to": 1}})[:3000]); return
    if args.mode == "incidents":
        print(call("incidents/get_incidents", {"request_data": {"search_from": 0, "search_to": 20}})[:8000]); return
    if args.mode == "alerts":
        print(call("alerts/get_alerts_multi_events", {"request_data": {"search_from": 0, "search_to": 20}})[:8000]); return
    if args.mode == "endpoints":
        print(call("endpoints/get_endpoints", {"request_data": {}})[:8000]); return
    # respond
    action = args.action or "isolate"
    eid = args.endpoint_id or "UNKNOWN"
    print_command(f"response action={action} endpoint={eid}")
    if not confirm(f"HIGH IMPACT XDR action {action} on {eid}", typed=f"{action} {eid}"):
        sys.exit(3)
    if action == "isolate":
        print(call("endpoints/isolate", {"request_data": {"endpoint_id": eid}}))
    elif action == "unisolate":
        print(call("endpoints/unisolate", {"request_data": {"endpoint_id": eid}}))
    else:
        print("Unknown action — extend api_helper for quarantine/script explicitly")

if __name__ == "__main__":
    main()
