#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, print_command
if not shutil.which("tshark"):
    print("tshark not on PATH — install Wireshark"); sys.exit(2)
ap=argparse.ArgumentParser(); ap.add_argument("mode", choices=["analyze","filter","extract","capture"]); ap.add_argument("extra", nargs=argparse.REMAINDER); a=ap.parse_args()
extra=a.extra[1:] if a.extra and a.extra[0]=="--" else a.extra
if a.mode=="analyze":
    if not extra: print("analyze <file>"); sys.exit(2)
    f=extra[0]
    for cmd in (
        ["tshark","-r",f,"-q","-z","io,phs"],
        ["tshark","-r",f,"-q","-z","conv,tcp"],
        ["tshark","-r",f,"-q","-z","expert"],
    ):
        print_command(cmd); subprocess.call(cmd)
    sys.exit(0)
if a.mode=="filter":
    if len(extra)<2: print("filter <file> <display-filter>"); sys.exit(2)
    cmd=["tshark","-r",extra[0],"-Y",extra[1],"-c","200"]; print_command(cmd); raise SystemExit(subprocess.call(cmd))
if a.mode=="extract":
    if len(extra)<2: print("extract <file> <field> [fields…]"); sys.exit(2)
    f, fields = extra[0], extra[1:]
    cmd=["tshark","-r",f,"-T","fields",*[x for fld in fields for x in ("-e",fld)],"-E","header=y","-E","separator=,"]
    print_command(cmd); raise SystemExit(subprocess.call(cmd))
# capture
# expected: -i IFACE [-f BPF] [-c COUNT|-a duration:SEC] -w OUT
print("WARN: live capture may require privileges and can capture others' traffic.")
print_command(["tshark", *extra])
if not confirm("Start live packet capture with these args?"):
    sys.exit(3)
if "-i" not in extra or "-w" not in extra:
    print("REFUSING — require -i <iface> and -w <outfile> and a limit (-c or -a)"); sys.exit(3)
if "-c" not in extra and "-a" not in " ".join(extra):
    print("REFUSING — require packet (-c) or time (-a) limit"); sys.exit(3)
raise SystemExit(subprocess.call(["tshark", *extra]))
