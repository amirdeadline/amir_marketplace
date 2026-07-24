#!/usr/bin/env python3
import argparse, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, print_command
MUT = re.compile(r"\b(create|delete|update|set|remove|assign|detach|stop|start|restart)\b", re.I)
ap = argparse.ArgumentParser(); ap.add_argument("args", nargs=argparse.REMAINDER); a = ap.parse_args()
args = a.args[1:] if a.args and a.args[0]=="--" else a.args
cmd=["az", *args]; print_command(cmd)
if MUT.search(" ".join(cmd)):
    if not confirm("Mutating Azure CLI command."): sys.exit(3)
raise SystemExit(subprocess.call(cmd))
