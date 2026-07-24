#!/usr/bin/env python3
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
