#!/usr/bin/env python3
"""Print every value a lab pod SHOULD have, from labs/labs.json, plus registry sanity checks.

Read-only. Used by the lab expert agent before a build, a gold snapshot or a deep review:
compare what is on the VMs against this sheet. Any value on a VM that belongs to another
lab (TSG, lab id, nic1 IP, hostname) is a wrong mapping.

Examples (run from the repo root):
    python $LE/scripts/lab_facts.py lab7
    python $LE/scripts/lab_facts.py 7 --json
    python $LE/scripts/lab_facts.py --all-checks
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import sys
from pathlib import Path

PARENT_TSG = "1479602777"
NIC1_SUBNET = ipaddress.ip_network("10.95.98.128/25")
NIC1_GATEWAY = "10.95.98.129"
DOMAIN = "saselab.paloaltonetworks.com"
SHARED_ROOT = "/opt/gns3/shared/lab"
BUCKET = "gs://sase-lab-sdwan-gns3-shared/lab"
TF_STACK = "labs/lab_automation/terraform/gcp-eve-ng-test-instance-feature-gns3-greenfield-merge"


def find_labs_json(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    # The working folder first (the skill may run from the marketplace copy), then the
    # folders above this script (rendered copy under <project>/.amir/generated/...).
    cwd = Path.cwd().resolve()
    for parent in (cwd, *cwd.parents, *Path(__file__).resolve().parents):
        cand = parent / "labs" / "labs.json"
        if cand.is_file():
            return cand
    raise SystemExit("labs/labs.json not found; run from the lab repo root or pass --labs-json")


def resolve_key(labs: dict, arg: str) -> str:
    a = arg.strip().lower().replace("lab-", "lab")
    if a in ("0", "lab0", "labdev", "dev"):
        return "dev"
    if a in labs:
        return a
    if a.isdigit():
        for key, lab in labs.items():
            if str(lab.get("lab_id")) == a:
                return key
    raise SystemExit(f"unknown lab {arg!r}; known: {', '.join(labs)}")


def iap_formula(lab_id: int, idx: int) -> int:
    return 20000 + 100 * lab_id + 20 + idx


def facts(doc: dict, key: str) -> dict:
    lab = doc["labs"][key]
    lab_id = int(lab["lab_id"])
    workspace = "dev" if key == "dev" else f"lab-{lab_id}"
    vms = []
    for name, vm in lab["vms"].items():
        idx = int(str(vm.get("role", name)).rsplit("-", 1)[-1])
        nics = vm.get("interfaces", {})
        vms.append({
            "name": name,
            "role": vm.get("role"),
            "index": idx,
            "zone": vm.get("zone"),
            "nic1": nics.get("nic1", {}).get("ip"),
            "nic0": nics.get("nic0", {}).get("ip"),
            "iap_port_json": vm.get("access", {}).get("iap_tunnel_ports", {}).get("ssh"),
            "iap_port_formula": iap_formula(lab_id, idx),
            "fqdn": f"srv{idx}.{key}.{DOMAIN}",
            "golden_snapshot": f"gns3-{idx}-lab{lab_id}-snapshot",
            "secret_cert": f"{key}-srv{idx}-cert",
            "secret_cert_password": f"{key}-srv{idx}-cert-password",
            "status": vm.get("status"),
        })
    vms.sort(key=lambda v: v["index"])
    tsg = lab.get("tsg_id")
    foreign = sorted({str(l.get("tsg_id")) for k, l in doc["labs"].items()
                      if k != key and l.get("tsg_id")} | {PARENT_TSG})
    foreign_nic1 = sorted({v.get("interfaces", {}).get("nic1", {}).get("ip")
                           for k, l in doc["labs"].items() if k != key
                           for v in l["vms"].values()} - {None})
    return {
        "lab_key": key,
        "lab_id": lab_id,
        "name": lab.get("name"),
        "enabled": lab.get("enabled"),
        "status": lab.get("status"),
        "tsg_id": tsg,
        "tsg_name": lab.get("tsg_name"),
        "pa_tenant_id": lab.get("pa_tenant_id"),
        "lab_address": lab.get("lab_address"),
        "release_profile": lab.get("release_profile"),
        "deployment_profile": lab.get("deployment_profile"),
        "sc_fqdn": {k: v.get("fqdn") for k, v in (lab.get("scm", {}).get("sc", {}) or {}).items()},
        "terraform_workspace": workspace,
        "tfvars": f"{TF_STACK}/tfvars/{workspace}.tfvars",
        "booking_env": f"{SHARED_ROOT}/docker/labapp/{workspace}/.env",
        "log_dir": f"{SHARED_ROOT}/labs/logs/labs/{lab_id}/",
        "lab_status_files": ["/etc/labapp/lab_status.json (all 4 VMs)",
                             f"{SHARED_ROOT}/labs/logs/labs/{lab_id}/gns3/lab_status.json (NFS copy)"],
        "student_password_secret": f"lab_{lab_id}_pass",
        "labapp_url": f"https://{vms[0]['nic1'] if vms else '?'}/",
        "gns3_api": f"https://{vms[0]['nic1'] if vms else '?'}:3080/v2",
        "vms": vms,
        "foreign_tsgs": foreign,
        "foreign_nic1_ips": foreign_nic1,
        "foreign_lab_keys": sorted(k for k in doc["labs"] if k != key),
        "nic1_gateway": NIC1_GATEWAY,
    }


def registry_checks(doc: dict) -> list[str]:
    """Problems in labs.json itself (not on any VM)."""
    out: list[str] = []
    seen_ip: dict[str, str] = {}
    seen_tsg: dict[str, str] = {}
    for key, lab in doc["labs"].items():
        lab_id = int(lab["lab_id"])
        tsg = lab.get("tsg_id")
        if tsg is None:
            out.append(f"{key}: tsg_id is null (never target it)")
        else:
            if str(tsg) == PARENT_TSG:
                out.append(f"{key}: tsg_id is the PARENT tsg")
            if str(tsg) in seen_tsg:
                out.append(f"{key}: tsg_id {tsg} also used by {seen_tsg[str(tsg)]}")
            seen_tsg[str(tsg)] = key
        if tsg and lab.get("pa_tenant_id") and str(lab["pa_tenant_id"]) != str(tsg):
            out.append(f"{key}: pa_tenant_id {lab['pa_tenant_id']} != tsg_id {tsg} (check)")
        sc = (lab.get("scm", {}) or {}).get("sc", {}) or {}
        f1 = (sc.get("sc1") or {}).get("fqdn")
        f2 = (sc.get("sc2") or {}).get("fqdn")
        if f1 and f2 and f1 == f2 and f1 != "FQDN_NOT_PROVIDED":
            out.append(f"{key}: sc1 and sc2 have the same FQDN {f1} (sc2 should be the dc2 one)")
        for name, vm in lab["vms"].items():
            ip = vm.get("interfaces", {}).get("nic1", {}).get("ip")
            idx = int(str(vm.get("role", name)).rsplit("-", 1)[-1])
            port = vm.get("access", {}).get("iap_tunnel_ports", {}).get("ssh")
            if port and port != iap_formula(lab_id, idx):
                out.append(f"{key}/{name}: IAP port {port} != formula {iap_formula(lab_id, idx)}")
            if not ip:
                out.append(f"{key}/{name}: no nic1 ip")
                continue
            try:
                addr = ipaddress.ip_address(ip)
            except ValueError:
                out.append(f"{key}/{name}: nic1 {ip} is NOT a valid IPv4 address")
                continue
            if addr not in NIC1_SUBNET or str(addr) in (NIC1_GATEWAY, str(NIC1_SUBNET.broadcast_address)):
                out.append(f"{key}/{name}: nic1 {ip} outside usable {NIC1_SUBNET}")
            if ip in seen_ip:
                out.append(f"{key}/{name}: nic1 {ip} also used by {seen_ip[ip]}")
            seen_ip[ip] = f"{key}/{name}"
    return out


def print_text(f: dict) -> None:
    print(f"lab {f['lab_key']}  (lab_id {f['lab_id']}, {f['name']})  enabled={f['enabled']} status={f['status']}")
    print(f"  TSG {f['tsg_id']}  name {f['tsg_name']}  pa_tenant_id {f['pa_tenant_id']}")
    print(f"  workspace {f['terraform_workspace']}   tfvars {f['tfvars']}")
    print(f"  booking .env  {f['booking_env']}")
    print(f"  logs          {f['log_dir']}")
    print(f"  labapp {f['labapp_url']}   GNS3 API {f['gns3_api']}   lab_address {f['lab_address']}")
    print(f"  release_profile {f['release_profile']}   student password secret {f['student_password_secret']}")
    print(f"  SC FQDN {f['sc_fqdn']}")
    print("  VMs:")
    for v in f["vms"]:
        warn = "" if v["iap_port_json"] in (None, v["iap_port_formula"]) else "  <-- IAP port mismatch"
        print(f"    {v['name']:<16} nic1 {v['nic1']:<15} nic0 {v['nic0']:<13} IAP {v['iap_port_formula']}"
              f"  {v['fqdn']:<40} snap {v['golden_snapshot']}  SM {v['secret_cert']}{warn}")
    print(f"  foreign TSGs (must NOT appear on this pod): {' '.join(f['foreign_tsgs'])}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("lab", nargs="?", help="dev, lab7, lab-7 or 7")
    p.add_argument("--labs-json")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--all-checks", action="store_true", help="only print registry sanity problems")
    a = p.parse_args(argv)
    path = find_labs_json(a.labs_json)
    doc = json.loads(path.read_text(encoding="utf-8"))
    if a.all_checks or not a.lab:
        problems = registry_checks(doc)
        print(f"labs.json: {path}")
        print(f"{len(problems)} registry problem(s)" + (":" if problems else ""))
        for line in problems:
            print("  - " + line)
        return 0
    f = facts(doc, resolve_key(doc["labs"], a.lab))
    if a.json:
        print(json.dumps(f, indent=2))
    else:
        print(f"labs.json: {path}")
        print_text(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
