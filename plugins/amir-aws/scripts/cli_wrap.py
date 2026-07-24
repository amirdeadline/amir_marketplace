#!/usr/bin/env python3
import argparse, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, print_command
MUT = re.compile(r"\b(create|delete|put|update|modify|attach|detach|terminate|revoke|authorize|run-instances|stop-instances)\b", re.I)
ap = argparse.ArgumentParser(); ap.add_argument("args", nargs=argparse.REMAINDER); a = ap.parse_args()
args = a.args[1:] if a.args and a.args[0] == "--" else a.args
if not shutil.which("aws"):
    print("aws CLI missing"); sys.exit(2)
cmd = ["aws", *args]
print_command(cmd)
line = " ".join(cmd)
if MUT.search(line):
    if not confirm("Mutating AWS CLI command."):
        sys.exit(3)
raise SystemExit(subprocess.call(cmd))
