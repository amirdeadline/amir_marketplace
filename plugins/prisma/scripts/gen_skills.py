#!/usr/bin/env python3
"""Generate SKILL.md files for prisma domains (idempotent template writer)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKILLS = {
    "scm-platform": {
        "title": "SCM Platform",
        "blurb": "Strata Cloud Manager tenancy/folders/snippets, configuration scope, config push, variables, RBAC, licensing, onboarding, dashboards.",
    },
    "prisma-access": {
        "title": "Prisma Access",
        "blurb": "Mobile Users (GlobalProtect + Explicit Proxy), Remote Networks, Service Connections, locations/compute regions, egress IP, autoscaling.",
    },
    "security-policy": {
        "title": "Security Policy",
        "blurb": "Security rules, profiles/profile groups, decryption, App-ID/User-ID in SASE, best-practice rulebase design and ordering.",
    },
    "sdwan": {
        "title": "Prisma SD-WAN",
        "blurb": "ION onboarding, path policy, app SLAs, branch topologies, interop with Prisma Access.",
    },
    "adem": {
        "title": "Autonomous DEM",
        "blurb": "ADEM tests, agent-based visibility, experience scores, symptom → segment → root-cause methodology.",
    },
    "ztna-access-agent": {
        "title": "ZTNA / Access Agent",
        "blurb": "Prisma Access Agent / ZTNA constructs and private app access patterns.",
    },
    "scm-api": {
        "title": "SCM / SASE APIs",
        "blurb": "pan.dev SCM & SASE APIs: TSG service accounts, OAuth2, pagination, config-as-code, curl/Python examples.",
    },
    "troubleshooting": {
        "title": "SASE Troubleshooting",
        "blurb": "Cross-product methodology: where logs live, what to collect first, escalation-ready evidence packages.",
    },
}

TEMPLATE = """---
name: {name}
description: >-
  {blurb} Use when the user asks about {title} in Prisma SASE / SCM.
  Prefer live corpus at PRISMA_DOCS_PATH; fall back to baked references/.
---

# {title}

## Knowledge layers

1. **Live layer (preferred):** read targeted sections from `PRISMA_DOCS_PATH`
   (default `E:\\PC3_Shared\\Palo\\Documents\\Markdowns Prisma SASE`) using
   `references/index.json` for topic → file → line/anchor. Never load entire
   multi‑MB files into context — search/retrieve only matching sections.
2. **Baked layer:** `references/summary.md` + `references/index.json` shipped
   inside this plugin (always available after `/prisma:update-index`).

If `PRISMA_DOCS_PATH` is unset or the path is missing, say clearly:
`Live corpus unavailable — answering from baked references (ingested: see summary header).`

## Honesty (mandatory)

- Label every material claim: `VERIFIED (source file/URL)` | `INFERRED` | `ASSUMED`.
- Cloud products change monthly — verify version-specific UI paths and limits against
  current public docs (docs.paloaltonetworks.com, pan.dev, live.paloaltonetworks.com,
  release notes) before asserting them.
- Prefer amir UNKNOWN / NOT DOABLE formats over guessing.
- Confirm before any destructive or mutating API/config change.

## Behavior

1. Parse the user question; list candidate topics from `references/index.json`.
2. Open live source sections when available; cite `path#line` or Source PDF name.
3. Cross-check freshness for version-specific claims via public docs.
4. Answer with procedures (UI path and/or API), scope implications (folder/snippet/
   push), and risks/trade-offs.
5. If evidence is thin, say what is unknown and what to collect next.

## References

- Baked: `references/summary.md`, `references/index.json`
- Public: docs.paloaltonetworks.com, pan.dev (SCM/SASE), live.paloaltonetworks.com
"""


def main() -> None:
    for name, meta in SKILLS.items():
        d = ROOT / "skills" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "references").mkdir(exist_ok=True)
        path = d / "SKILL.md"
        path.write_text(
            TEMPLATE.format(name=name, title=meta["title"], blurb=meta["blurb"]),
            encoding="utf-8",
        )
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
