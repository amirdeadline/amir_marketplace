#!/usr/bin/env python3
"""Scaffold remaining tooling plugins: splunk, elastic, sentinel, qradar, cortex-xdr, ssh-terminal, nmap, wireshark."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

# Reuse emit helpers by importing from batch1
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("batch1", HERE / "scaffold_tooling_batch.py")
batch1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch1)

add = batch1.add
PLUGINS = []  # local list — we'll call emit directly


def emit_pack(p: dict) -> None:
    batch1.emit_plugin(p)
    batch1.pack_copy(p["name"])


# --- splunk ---
emit_pack({
    "name": "splunk",
    "category": "security",
    "tags": ["splunk", "spl", "siem"],
    "pattern": "Knowledge+API (local REST). Splunk MCP exists as on-platform app — optional remote URL, not bundled.",
    "desc": "Splunk REST/search helper + SPL authoring skill. Saved-search/alert mutations confirm-first. PARTIALLY DOABLE: enterprise MCP is host-installed (Splunkbase app), not a local npm.",
    "prereq": "SPLUNK_BASE_URL + SPLUNK_TOKEN (bearer). Optional Splunk MCP if admin enabled on platform.",
    "env": ["SPLUNK_BASE_URL", "SPLUNK_TOKEN"],
    "skills": {
        "spl": ("SPL authoring: search-time patterns, stats/tstats, data models, performance, detections.",
            "# spl\n\nAuthor SPL for investigations/detections. Prefer `tstats` on accelerated DM when available.\nPerformance: earliest filters, avoid `*` joins, limit fields.\nDeep KQL → sentinel plugin; ES|QL → elastic plugin."),
    },
    "commands": {
        "preflight": ("Check Splunk auth.",
            "# /splunk:preflight\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/api_helper.py\" preflight`"),
        "search": ("Run a Splunk search (read, limited).",
            "# /splunk:search\n\n`$ARGUMENTS` → api_helper.py search"),
        "ask": ("SPL / Splunk how-to via spl skill.",
            "# /splunk:ask\n\n`$ARGUMENTS`"),
    },
    "scripts": {
        "api_helper.py": r'''#!/usr/bin/env python3
"""Splunk REST helper — search jobs (read); mutating knowledge objects confirm-first."""
from __future__ import annotations
import argparse, json, os, sys, time, urllib.parse, urllib.request, ssl
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, mask_secret, print_command, require_env

def req(method, path, data=None, params=None):
    env = require_env(["SPLUNK_BASE_URL", "SPLUNK_TOKEN"])
    base = env["SPLUNK_BASE_URL"].rstrip("/")
    token = env["SPLUNK_TOKEN"]
    url = base + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    print(f"auth={mask_secret(token)}")
    print_command(f"{method} {url}")
    body = urllib.parse.urlencode(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    r.add_header("Authorization", f"Bearer {token}")
    if data:
        r.add_header("Content-Type", "application/x-www-form-urlencoded")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(r, context=ctx, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preflight", "search", "mutate"])
    ap.add_argument("--query", default="| rest /services/server/info | head 1")
    ap.add_argument("--path", default="")
    ap.add_argument("--count", type=int, default=20)
    args = ap.parse_args()
    if args.mode == "preflight":
        print(req("GET", "/services/server/info", params={"output_mode": "json"})[:3000])
        return
    if args.mode == "search":
        # oneshot search
        print(req("POST", "/services/search/jobs/oneshot", data={
            "search": args.query if args.query.startswith("search") or args.query.startswith("|") else f"search {args.query}",
            "output_mode": "json",
            "count": str(args.count),
        })[:8000])
        return
    if not confirm("Mutating Splunk knowledge object / saved search / alert."):
        sys.exit(3)
    print(req("POST", args.path or "/services/saved/searches", data={"name": "amir_placeholder", "search": "index=_internal | head 1"}))

if __name__ == "__main__":
    main()
''',
    },
    "always_on_tokens": "~0.9k",
    "safety": "Search reads limited. Saved search/alert edits confirm. Token masked. PLATFORM MCP: https://splunkbase.splunk.com/app/7931 — not bundled.",
})


# --- elastic ---
emit_pack({
    "name": "elastic",
    "category": "security",
    "tags": ["elasticsearch", "kibana", "esql", "detections"],
    "pattern": "Knowledge+API + optional Kibana Agent Builder MCP (mcp-remote) when ELASTIC_KIBANA_URL set",
    "desc": "Elasticsearch/Kibana REST helper + ES|QL/DSL and detections skills. Index delete requires typed confirmation. Optional MCP to Kibana Agent Builder.",
    "prereq": "ELASTIC_BASE_URL + ELASTIC_API_KEY. Optional Kibana MCP via npx mcp-remote.",
    "env": ["ELASTIC_BASE_URL", "ELASTIC_API_KEY", "ELASTIC_KIBANA_URL (optional for MCP)"],
    "mcp": {
        "elastic-agent-builder": {
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote",
                "${env:ELASTIC_KIBANA_URL}/api/agent_builder/mcp",
                "--header",
                "Authorization:${env:ELASTIC_AUTH_HEADER}"
            ]
        }
    },
    "skills": {
        "esql-and-dsl": ("Query DSL + ES|QL authoring.",
            "# esql-and-dsl\n\nAuthor `_search` DSL and ES|QL. Prefer filters over scripts. Size limits. SPL → splunk; KQL → sentinel."),
        "elastic-detections": ("Detection rules and ECS field mapping.",
            "# elastic-detections\n\nRule design against ECS. Confirm before creating/updating rules via API."),
    },
    "commands": {
        "preflight": ("Cluster info / auth check.",
            "# /elastic:preflight\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/api_helper.py\" preflight`"),
        "search": ("_search or ES|QL (read).",
            "# /elastic:search\n\n`$ARGUMENTS`"),
        "ask": ("Query/detection help.",
            "# /elastic:ask\n\n`$ARGUMENTS`"),
    },
    "scripts": {
        "api_helper.py": r'''#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, ssl, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, mask_secret, print_command, require_env

def call(method, path, body=None):
    env = require_env(["ELASTIC_BASE_URL", "ELASTIC_API_KEY"])
    base = env["ELASTIC_BASE_URL"].rstrip("/")
    key = env["ELASTIC_API_KEY"]
    url = base + path
    print(f"key={mask_secret(key)}")
    print_command(f"{method} {url}")
    data = None if body is None else json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Authorization", f"ApiKey {key}")
    r.add_header("Content-Type", "application/json")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(r, context=ctx, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preflight", "search", "cat", "delete-index"])
    ap.add_argument("--index", default="*")
    ap.add_argument("--body", default='{"size":5,"query":{"match_all":{}}}')
    args = ap.parse_args()
    if args.mode == "preflight":
        print(call("GET", "/")[:2000]); return
    if args.mode == "cat":
        print(call("GET", "/_cat/indices?v")[:4000]); return
    if args.mode == "search":
        print(call("POST", f"/{args.index}/_search", json.loads(args.body))[:8000]); return
    if args.mode == "delete-index":
        print_command(f"DELETE /{args.index}")
        if not confirm(f"DELETE INDEX {args.index}", typed=f"DELETE {args.index}"):
            sys.exit(3)
        print(call("DELETE", f"/{args.index}"))

if __name__ == "__main__":
    main()
''',
    },
    "always_on_tokens": "~1.0k",
    "safety": "Deletes typed confirm. MCP optional (Kibana Agent Builder). Verified: elastic.co Agent Builder MCP endpoint.",
    "notes_partial": "If ELASTIC_KIBANA_URL unset, MCP entry may fail to connect — API helper still works. Document in README.",
})


# --- sentinel ---
emit_pack({
    "name": "sentinel",
    "category": "security",
    "tags": ["sentinel", "kql", "azure", "hunting"],
    "pattern": "Knowledge+API via Azure (az / Log Analytics REST)",
    "desc": "Microsoft Sentinel: KQL hunting skill + analytics/incidents helpers. Queries read-free; rule/incident mutations confirm-first. Reuses az auth.",
    "prereq": "az login; workspace IDs via env SENTINEL_WORKSPACE_ID, SENTINEL_RESOURCE (optional ARM id)",
    "env": ["SENTINEL_WORKSPACE_ID", "SENTINEL_RESOURCE (optional)"],
    "skills": {
        "kql-hunting": ("KQL for hunting and detections (core value).",
            "# kql-hunting\n\nAuthor KQL: summarize, join, let, materialize. Time filters first. SPL→splunk; ES|QL→elastic."),
        "sentinel-analytics": ("Analytic rules, watchlists, incidents.",
            "# sentinel-analytics\n\nRule tuning and incident triage. Confirm before create/update/delete rules or closing incidents."),
    },
    "commands": {
        "preflight": ("az account show + workspace check.",
            "# /sentinel:preflight\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py\"`"),
        "query": ("Run KQL (read).",
            "# /sentinel:query\n\n`$ARGUMENTS` → scripts/kql.py"),
        "ask": ("Hunting/analytics help.",
            "# /sentinel:ask\n\n`$ARGUMENTS`"),
    },
    "scripts": {
        "preflight.py": r'''#!/usr/bin/env python3
import shutil, subprocess, sys
if not shutil.which("az"):
    print("az missing — install Azure CLI"); sys.exit(2)
r=subprocess.run(["az","account","show","-o","json"], capture_output=True, text=True)
if r.returncode!=0:
    print("REFUSING — az login required"); sys.exit(2)
print(r.stdout)
''',
        "kql.py": r'''#!/usr/bin/env python3
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
''',
    },
    "always_on_tokens": "~1.0k",
    "safety": "KQL reads free. Rule/incident writes confirm. Uses az credentials (no keys in files).",
})


# --- qradar ---
emit_pack({
    "name": "qradar",
    "category": "security",
    "tags": ["qradar", "aql", "ibm", "siem"],
    "pattern": "Knowledge+API (QRadar REST)",
    "desc": "QRadar REST: AQL searches + offense reads; offense/rule/reference-set writes confirm-first. SEC token masked.",
    "prereq": "QRADAR_BASE_URL + QRADAR_SEC_TOKEN",
    "env": ["QRADAR_BASE_URL", "QRADAR_SEC_TOKEN"],
    "skills": {
        "aql-and-offenses": ("AQL authoring, offense triage, log-source health.",
            "# aql-and-offenses\n\nAQL SELECT/FROM/WHERE patterns, offense triage methodology, log source status checks.\nAPI version: use Accept: application/json for /api/* (verify deployment version)."),
    },
    "commands": {
        "preflight": ("GET /api/system/about",
            "# /qradar:preflight\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/api_helper.py\" preflight`"),
        "aql": ("Run AQL search (read).",
            "# /qradar:aql\n\n`$ARGUMENTS`"),
        "ask": ("AQL/offense help.",
            "# /qradar:ask\n\n`$ARGUMENTS`"),
    },
    "scripts": {
        "api_helper.py": r'''#!/usr/bin/env python3
"""QRadar REST — verified pattern: SEC header token auth."""
from __future__ import annotations
import argparse, json, ssl, sys, urllib.parse, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, mask_secret, print_command, require_env

def call(method, path, params=None, body=None):
    env = require_env(["QRADAR_BASE_URL", "QRADAR_SEC_TOKEN"])
    base = env["QRADAR_BASE_URL"].rstrip("/")
    tok = env["QRADAR_SEC_TOKEN"]
    url = base + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    print(f"SEC={mask_secret(tok)}")
    print_command(f"{method} {url}")
    data = None if body is None else json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("SEC", tok)
    r.add_header("Accept", "application/json")
    r.add_header("Version", os_version())
    if body is not None:
        r.add_header("Content-Type", "application/json")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(r, context=ctx, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")

def os_version():
    import os
    return os.environ.get("QRADAR_API_VERSION", "20.0")  # override per deploy

def main():
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preflight", "aql", "offenses", "mutate"])
    ap.add_argument("--query", default="SELECT * FROM events LIMIT 1")
    args = ap.parse_args()
    if args.mode == "preflight":
        print(call("GET", "/api/system/about")[:3000]); return
    if args.mode == "offenses":
        print(call("GET", "/api/siem/offenses", params={"filter": "status%3DOPEN", "limit": "10"})[:8000]); return
    if args.mode == "aql":
        # create search
        print(call("POST", "/api/ariel/searches", params={"query_expression": args.query})[:8000]); return
    if not confirm("Mutating QRadar offense/rule/reference set."):
        sys.exit(3)
    print("Provide concrete path via future args — refused generic mutate without path")

if __name__ == "__main__":
    main()
''',
    },
    "always_on_tokens": "~0.9k",
    "safety": "Writes confirm. SEC token masked. Default API Version header 20.0 (override QRADAR_API_VERSION).",
})


# --- cortex-xdr ---
emit_pack({
    "name": "cortex-xdr",
    "category": "security",
    "tags": ["cortex", "xdr", "palo-alto", "ir"],
    "pattern": "Knowledge+API (Cortex XDR)",
    "desc": "Cortex XDR API: read incidents/alerts/endpoints; response actions require typed confirmation.",
    "prereq": "XDR_FQDN + XDR_API_KEY_ID + XDR_API_KEY (Advanced API)",
    "env": ["XDR_FQDN", "XDR_API_KEY_ID", "XDR_API_KEY"],
    "skills": {
        "xdr-ir": ("Incident triage, alert-to-endpoint pivot, evidence collection.",
            "# xdr-ir\n\nTriage flow: incident → alerts → endpoint → causality.\nResponse actions (isolate/quarantine/script) are HIGH IMPACT — typed confirm via api_helper."),
    },
    "commands": {
        "preflight": ("Validate XDR API auth.",
            "# /cortex-xdr:preflight\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/api_helper.py\" preflight`"),
        "incidents": ("List/get incidents (read).",
            "# /cortex-xdr:incidents\n\n`$ARGUMENTS`"),
        "respond": ("Response action — typed confirmation required.",
            "# /cortex-xdr:respond\n\n`$ARGUMENTS` → api_helper.py respond"),
        "ask": ("IR methodology help.",
            "# /cortex-xdr:ask\n\n`$ARGUMENTS`"),
    },
    "scripts": {
        "api_helper.py": r'''#!/usr/bin/env python3
"""Cortex XDR Advanced API — headers x-xdr-auth-id + Authorization."""
from __future__ import annotations
import argparse, json, ssl, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from safety import confirm, mask_secret, print_command, require_env

def call(path, body):
    env = require_env(["XDR_FQDN", "XDR_API_KEY_ID", "XDR_API_KEY"])
    fqdn = env["XDR_FQDN"].rstrip("/")
    if not fqdn.startswith("http"):
        fqdn = "https://" + fqdn
    url = f"{fqdn}/public_api/v1/{path.lstrip('/')}"
    print(f"key_id={mask_secret(env['XDR_API_KEY_ID'])} key={mask_secret(env['XDR_API_KEY'])}")
    print_command(f"POST {url} body={json.dumps(body)[:500]}")
    data = json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method="POST")
    r.add_header("x-xdr-auth-id", env["XDR_API_KEY_ID"])
    r.add_header("Authorization", env["XDR_API_KEY"])
    r.add_header("Content-Type", "application/json")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(r, context=ctx, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preflight", "incidents", "alerts", "endpoints", "respond"])
    ap.add_argument("--action", default="")
    ap.add_argument("--endpoint-id", default="")
    args = ap.parse_args()
    if args.mode == "preflight":
        # get_incidents with empty filter is a common probe
        print(call("incidents/get_incidents", {"request_data": {"search_from": 0, "search_to": 1}})[:3000]); return
    if args.mode == "incidents":
        print(call("incidents/get_incidents", {"request_data": {"search_from": 0, "search_to": 20}})[:8000]); return
    if args.mode == "alerts":
        print(call("alerts/get_alerts_multi_events", {"request_data": {"search_from": 0, "search_to": 20}})[:8000]); return
    if args.mode == "endpoints":
        print(call("endpoints/get_endpoints", {"request_data": {}})[:8000]); return
    # respond
    action = args.action or "isolate"
    eid = args.endpoint_id or "UNKNOWN"
    print_command(f"response action={action} endpoint={eid}")
    if not confirm(f"HIGH IMPACT XDR action {action} on {eid}", typed=f"{action} {eid}"):
        sys.exit(3)
    if action == "isolate":
        print(call("endpoints/isolate", {"request_data": {"endpoint_id": eid}}))
    elif action == "unisolate":
        print(call("endpoints/unisolate", {"request_data": {"endpoint_id": eid}}))
    else:
        print("Unknown action — extend api_helper for quarantine/script explicitly")

if __name__ == "__main__":
    main()
''',
    },
    "always_on_tokens": "~1.0k",
    "safety": "Response actions require typed confirmation action+endpoint_id. Keys masked.",
})


# --- ssh-terminal ---
emit_pack({
    "name": "ssh-terminal",
    "category": "network",
    "tags": ["ssh", "scp", "openssh"],
    "pattern": "CLI-wrap (OpenSSH)",
    "desc": "SSH/SCP via system OpenSSH. Confirm host+command before run; block destructive remote commands unless host-named typed confirm; no password inline; no multi-host loops without per-host confirm.",
    "prereq": "ssh/scp on PATH (Windows OpenSSH client).",
    "env": [],
    "skills": {
        "ssh-safety": ("Key hygiene, jump hosts, never paste secrets.",
            "# ssh-safety\n\nUse agent/keys only. No passwords in args/files. JumpHost via ProxyJump. Authorized systems only."),
    },
    "commands": {
        "run": ("Run one remote command (confirm).",
            "# /ssh:run\n\n`$ARGUMENTS` as `<host> <command…>` → scripts/ssh_cli.py run"),
        "session": ("Open interactive ssh (human-driven).",
            "# /ssh:session\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/ssh_cli.py\" session -- $ARGUMENTS`\nClaude must not drive interactive session blind."),
        "copy": ("scp/sftp confirm-first.",
            "# /ssh:copy\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/ssh_cli.py\" copy -- $ARGUMENTS`"),
    },
    "scripts": {
        "ssh_cli.py": r'''#!/usr/bin/env python3
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
''',
    },
    "always_on_tokens": "~0.7k",
    "safety": "Authorized systems only. Per-host confirm. Destructive needs typed hostname. No multi-host auto loops.",
})


# --- nmap ---
emit_pack({
    "name": "nmap",
    "category": "network",
    "tags": ["nmap", "scanning", "defensive"],
    "pattern": "CLI-wrap (authorized-use only)",
    "desc": "Authorized nmap scanning: interview→command print→auth gate→confirm. Parse XML/gnmap to tables. Aggressive modes opt-in.",
    "prereq": "nmap on PATH",
    "env": [],
    "skills": {
        "nmap-methodology": ("Scanning stages, reading results, remediation for defending your estate.",
            "# nmap-methodology\n\nHost discovery → ports → service/version → scripts. Remediate findings. Only scan systems you are authorized to test."),
    },
    "commands": {
        "scan": ("Build+confirm an authorized scan.",
            "# /nmap:scan\n\n`$ARGUMENTS` → scripts/nmap_cli.py scan"),
        "parse": ("Parse nmap XML/gnmap.",
            "# /nmap:parse\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/nmap_cli.py\" parse -- $ARGUMENTS`"),
    },
    "scripts": {
        "nmap_cli.py": r'''#!/usr/bin/env python3
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
''',
    },
    "always_on_tokens": "~0.8k",
    "safety": "Authz typed gate AUTHORIZED <target>. Bulk /0 refused. Aggressive opt-in.",
})


# --- wireshark ---
emit_pack({
    "name": "wireshark",
    "category": "network",
    "tags": ["tshark", "pcap", "packets"],
    "pattern": "CLI-wrap (tshark)",
    "desc": "tshark analysis of existing pcaps (default). Live capture opt-in with interface, filter, limits, confirm.",
    "prereq": "tshark on PATH (Wireshark install).",
    "env": [],
    "skills": {
        "packet-analysis": ("Display filters, TCP handshake/retx, TLS/DNS/DHCP triage, latency vs loss.",
            "# packet-analysis\n\nRead captures the user already has. Author display filters. Diagnose latency vs loss."),
    },
    "commands": {
        "analyze": ("Protocol hierarchy / conversations / expert on a file.",
            "# /pcap:analyze\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/tshark_cli.py\" analyze -- $ARGUMENTS`"),
        "filter": ("Apply display filter; summarize.",
            "# /pcap:filter\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/tshark_cli.py\" filter -- $ARGUMENTS`"),
        "extract": ("Extract fields to table.",
            "# /pcap:extract\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/tshark_cli.py\" extract -- $ARGUMENTS`"),
        "capture": ("Opt-in live capture (confirm).",
            "# /pcap:capture\n\n`python \"${CLAUDE_PLUGIN_ROOT}/scripts/tshark_cli.py\" capture -- $ARGUMENTS`"),
    },
    "scripts": {
        "tshark_cli.py": r'''#!/usr/bin/env python3
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
''',
    },
    "always_on_tokens": "~0.8k",
    "safety": "Default=file analysis. Live capture opt-in with iface+outfile+limit+confirm.",
})

print("batch2 complete: splunk elastic sentinel qradar cortex-xdr ssh-terminal nmap wireshark")
