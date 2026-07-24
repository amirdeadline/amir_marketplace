#!/usr/bin/env python3
from __future__ import annotations
import argparse, ipaddress, re, shutil, subprocess, sys, xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, print_command
if not shutil.which("nmap"):
    print("nmap not on PATH — https://nmap.org/download.html"); sys.exit(2)

BULK = re.compile(r"0\.0\.0\.0/0|::/0|\d+\.\d+\.\d+\.\d+/\d{1,2}")

def looks_unauthorized_bulk(target: str) -> bool:
    t = target.strip()
    if t in {"0.0.0.0/0", "::/0"}:
        return True
    try:
        net = ipaddress.ip_network(t, strict=False)
        if net.num_addresses > 4096:
            return True
    except Exception:
        pass
    return False

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["scan", "parse"])
ap.add_argument("extra", nargs=argparse.REMAINDER)
a = ap.parse_args()
extra = a.extra[1:] if a.extra and a.extra[0] == "--" else a.extra

if a.mode == "parse":
    if not extra:
        print("usage: parse <file.xml>"); sys.exit(2)
    path = Path(extra[0])
    tree = ET.parse(path)
    rows = []
    for host in tree.findall("host"):
        addr = host.find("address")
        ip = addr.get("addr") if addr is not None else "?"
        for port in host.findall("./ports/port"):
            state = port.find("state")
            svc = port.find("service")
            if state is not None and state.get("state") == "open":
                rows.append(f"{ip}:{port.get('portid')}/{port.get('protocol')} {svc.get('name') if svc is not None else ''}")
    print("\n".join(rows) or "(no open ports)")
    sys.exit(0)

# scan
# expected: target [nmap-flags…]
if not extra:
    print("usage: scan <target> [nmap args]"); sys.exit(2)
target = extra[0]
flags = extra[1:]
if looks_unauthorized_bulk(target):
    print("REFUSING — target looks like bulk internet range; narrow scope."); sys.exit(3)
print("AUTHORIZATION GATE: You must confirm you are authorized to scan this target.")
if not confirm(f"I am authorized to scan {target}", typed=f"AUTHORIZED {target}"):
    sys.exit(3)
aggressive = any(x in flags for x in ["-A", "-T4", "-T5", "-sS", "-O", "--script"])
if aggressive:
    if not confirm("Opt-in to aggressive/privileged nmap options?"):
        sys.exit(3)
cmd = ["nmap", *flags, target]
print_command(cmd)
if not confirm("Run this nmap command?"):
    sys.exit(3)
raise SystemExit(subprocess.call(cmd))
