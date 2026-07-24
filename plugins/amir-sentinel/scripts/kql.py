#!/usr/bin/env python3
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, print_command
ap=argparse.ArgumentParser(); ap.add_argument("--query", required=True); ap.add_argument("--mutate", action="store_true"); a=ap.parse_args()
ws=os.environ.get("SENTINEL_WORKSPACE_ID","").strip()
if not ws:
    print("missing SENTINEL_WORKSPACE_ID"); sys.exit(2)
if a.mutate and not confirm("Mutating Sentinel rule/incident."):
    sys.exit(3)
cmd=["az","monitor","log-analytics","query","--workspace",ws,"--analytics-query",a.query,"-o","json"]
print_command(cmd)
raise SystemExit(subprocess.call(cmd))
