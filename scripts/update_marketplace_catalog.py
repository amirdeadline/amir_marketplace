#!/usr/bin/env python3
"""Rewrite marketplace manifests — all plugin names amir / amir-* for /amir slash UX."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENTRIES = [
    {"name": "amir", "source": "./plugins/amir", "description": "Portable multi-agent project-execution harness.", "version": "0.1.0", "category": "integrations", "tags": ["multi-agent", "orchestrator"]},
    {"name": "amir-asana", "source": "./plugins/amir-asana", "description": "Asana MCP + task skills.", "version": "0.2.0", "category": "integrations", "tags": ["asana", "mcp"]},
    {"name": "amir-prisma", "source": "./plugins/amir-prisma", "description": "INTERNAL Prisma SASE/SCM corpus skills.", "version": "0.1.0", "category": "security", "tags": ["prisma", "sase", "internal"]},
    {"name": "amir-litellm", "source": "./plugins/amir-litellm", "description": "Org LiteLLM proxy session launcher + MCP.", "version": "0.1.0", "category": "integrations", "tags": ["litellm", "proxy"]},
    {"name": "amir-paloalto", "source": "./plugins/amir-paloalto", "description": "PAN-OS/Panorama/GlobalProtect companion to amir-prisma.", "version": "0.1.0", "category": "security", "tags": ["pan-os", "panorama"]},
    {"name": "amir-aws", "source": "./plugins/amir-aws", "description": "AWS official MCP + aws CLI fallback.", "version": "0.1.0", "category": "infra", "tags": ["aws", "mcp"]},
    {"name": "amir-azure", "source": "./plugins/amir-azure", "description": "Azure MCP + az CLI.", "version": "0.1.0", "category": "infra", "tags": ["azure", "mcp"]},
    {"name": "amir-terraform", "source": "./plugins/amir-terraform", "description": "Terraform plan/apply/destroy with confirm + hooks.", "version": "0.1.0", "category": "infra", "tags": ["terraform", "iac"]},
    {"name": "amir-docker", "source": "./plugins/amir-docker", "description": "Docker/Compose CLI wrappers with guards.", "version": "0.1.0", "category": "infra", "tags": ["docker"]},
    {"name": "amir-splunk", "source": "./plugins/amir-splunk", "description": "Splunk REST/SPL helper.", "version": "0.1.0", "category": "security", "tags": ["splunk", "spl"]},
    {"name": "amir-elastic", "source": "./plugins/amir-elastic", "description": "Elasticsearch/Kibana API + ES|QL skills.", "version": "0.1.0", "category": "security", "tags": ["elastic"]},
    {"name": "amir-sentinel", "source": "./plugins/amir-sentinel", "description": "Microsoft Sentinel KQL hunting + analytics.", "version": "0.1.0", "category": "security", "tags": ["sentinel", "kql"]},
    {"name": "amir-qradar", "source": "./plugins/amir-qradar", "description": "QRadar AQL/offenses REST helper.", "version": "0.1.0", "category": "security", "tags": ["qradar"]},
    {"name": "amir-cortex-xdr", "source": "./plugins/amir-cortex-xdr", "description": "Cortex XDR API + IR; typed response confirms.", "version": "0.1.0", "category": "security", "tags": ["cortex", "xdr"]},
    {"name": "amir-ssh", "source": "./plugins/amir-ssh", "description": "OpenSSH wrappers with host/command confirmation.", "version": "0.1.0", "category": "network", "tags": ["ssh"]},
    {"name": "amir-nmap", "source": "./plugins/amir-nmap", "description": "Authorized nmap scanning + parse.", "version": "0.1.0", "category": "network", "tags": ["nmap"]},
    {"name": "amir-wireshark", "source": "./plugins/amir-wireshark", "description": "tshark pcap analysis; live capture opt-in.", "version": "0.1.0", "category": "network", "tags": ["tshark", "pcap"]},
]


def main() -> None:
    claude_plugins = []
    cursor_plugins = []
    codex_plugins = []
    for e in ENTRIES:
        claude_plugins.append({
            "name": e["name"],
            "source": e["source"],
            "description": e["description"],
            "version": e["version"],
            "author": {"name": "Amir"},
            "category": e["category"],
            "tags": e["tags"],
            "keywords": e["tags"],
        })
        cursor_plugins.append({
            "name": e["name"],
            "source": e["name"],
            "description": e["description"],
            "version": e["version"],
            "author": {"name": "Amir"},
            "category": e["category"],
            "tags": e["tags"],
            "keywords": e["tags"],
        })
        codex_plugins.append({
            "name": e["name"],
            "source": {"source": "local", "path": e["source"]},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": e["category"],
            "description": e["description"],
            "version": e["version"],
        })

    meta = {
        "description": "amir marketplace — all slash commands under /amir…",
        "version": "0.3.1",
    }
    (ROOT / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps({"name": "amir-marketplace", "owner": {"name": "amir"}, "metadata": meta, "plugins": claude_plugins}, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / ".cursor-plugin" / "marketplace.json").write_text(
        json.dumps({"name": "amir-marketplace", "owner": {"name": "amir"}, "metadata": {**meta, "pluginRoot": "./plugins"}, "plugins": cursor_plugins}, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / ".agents" / "plugins" / "marketplace.json").write_text(
        json.dumps({"name": "amir-marketplace", "interface": {"displayName": "amir marketplace"}, "plugins": codex_plugins}, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "VERSION").write_text("0.3.1\n", encoding="utf-8")
    print(f"catalog: {len(ENTRIES)} plugins (all amir*)")


if __name__ == "__main__":
    main()
