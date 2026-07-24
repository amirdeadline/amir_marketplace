#!/usr/bin/env python3
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
