#!/usr/bin/env python3
import argparse, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, print_command
if not shutil.which("docker"):
    print("docker not on PATH"); sys.exit(2)
ap=argparse.ArgumentParser(); ap.add_argument("action"); ap.add_argument("extra", nargs=argparse.REMAINDER); a=ap.parse_args()
extra=a.extra[1:] if a.extra and a.extra[0]=="--" else a.extra
def run(cmd, need=False):
    print_command(cmd)
    if need and not confirm("Potentially destructive docker command."): sys.exit(3)
    raise SystemExit(subprocess.call(cmd))
if a.action=="status":
    subprocess.call(["docker","ps","-a"]); 
    if shutil.which("docker"):
        subprocess.call(["docker","compose","ps"])
    sys.exit(0)
maps={
 "logs": (["docker","logs",*extra], False),
 "build": (["docker","build",*extra], False),
 "up": (["docker","compose","up","-d",*extra], False),
 "down": (["docker","compose","down",*extra], True),
 "push": (["docker","push",*extra], True),
 "prune": (["docker","system","prune",*extra], True),
}
if a.action not in maps:
    print("unknown action"); sys.exit(2)
cmd, need = maps[a.action]
# Hard guard rm -f / volume rm
joined=" ".join(extra)
if "prune" in joined or "volume" in joined and "rm" in joined or "-f" in extra:
    need=True
run(cmd, need)
