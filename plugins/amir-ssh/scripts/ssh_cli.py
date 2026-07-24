#!/usr/bin/env python3
from __future__ import annotations
import argparse, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import DESTRUCTIVE_REMOTE, confirm, print_command
if not shutil.which("ssh"):
    print("ssh not on PATH (install OpenSSH client)"); sys.exit(2)

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["run", "session", "copy"])
ap.add_argument("extra", nargs=argparse.REMAINDER)
a = ap.parse_args()
extra = a.extra[1:] if a.extra and a.extra[0] == "--" else a.extra

if a.mode == "session":
    if not extra:
        print("usage: session <host>"); sys.exit(2)
    host = extra[0]
    print_command(["ssh", host, *extra[1:]])
    if not confirm(f"Open interactive SSH session to {host}?"):
        sys.exit(3)
    raise SystemExit(subprocess.call(["ssh", host, *extra[1:]]))

if a.mode == "copy":
    print_command(["scp", *extra])
    if not confirm("SCP/SFTP file transfer."):
        sys.exit(3)
    raise SystemExit(subprocess.call(["scp", *extra]))

# run
if len(extra) < 2:
    print("usage: run <host> <command…>"); sys.exit(2)
host, remote = extra[0], " ".join(extra[1:])
if re.search(r"( -p |--password|password=)", remote, re.I):
    print("REFUSING — never pass passwords inline"); sys.exit(3)
print_command(["ssh", host, remote])
if DESTRUCTIVE_REMOTE.search(remote):
    if not confirm(f"DESTRUCTIVE remote command on {host}", typed=host):
        sys.exit(3)
elif not confirm(f"Run on {host}: {remote}"):
    sys.exit(3)
raise SystemExit(subprocess.call(["ssh", host, remote]))
