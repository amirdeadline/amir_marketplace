#!/usr/bin/env python3
"""Build-time / on-demand corpus ingestion for the prisma plugin.

Walks PRISMA_DOCS_PATH (markdown only), classifies files into domain skills,
writes references/index.json + references/summary.md per skill.

Never uploads content. Never invents domains for unclassifiable files —
they are listed in references/_unclassified.json at the plugin root.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]  # scripts/prisma/ -> plugin root
SKILLS_ROOT = PLUGIN_ROOT / "skills"

SKILL_DIRS = {  # old domain id -> renamed skill folder (amir_project)
    'adem': 'prisma_adem',
    'prisma-access': 'prisma_access',
    'scm-api': 'prisma_scm_api',
    'scm-platform': 'prisma_scm_platform',
    'sdwan': 'prisma_sdwan',
    'security-policy': 'prisma_security_policy',
    'troubleshooting': 'prisma_troubleshooting',
    'ztna-access-agent': 'prisma_ztna_access_agent',
}

DEFAULT_DOCS = Path(os.environ.get("PRISMA_DOCS_PATH", r"E:\PC3_Shared\Palo\Documents\Markdowns Prisma SASE"))

DOMAINS = [
    "scm-platform",
    "prisma-access",
    "security-policy",
    "sdwan",
    "adem",
    "ztna-access-agent",
    "scm-api",
    "troubleshooting",
]

# Filename / path keywords → domains (ordered; first matches win for primary)
FILENAME_RULES: list[tuple[re.Pattern[str], list[str]]] = [
    (re.compile(r"prisma_access", re.I), ["prisma-access", "adem", "ztna-access-agent", "security-policy", "troubleshooting"]),
    (re.compile(r"prisma_sase_architec", re.I), ["scm-platform", "security-policy", "ztna-access-agent", "troubleshooting"]),
    (re.compile(r"ai_prisma_sdwan", re.I), ["sdwan", "troubleshooting"]),
    (re.compile(r"prisma_sdwan|ai_prisma_sdwan", re.I), ["sdwan", "troubleshooting"]),
    (re.compile(r"prisma_sase_sdk|api_reference|user_guide|architecture\.md", re.I), ["scm-api"]),
    (re.compile(r"project\.md", re.I), ["scm-platform", "prisma-access", "sdwan", "scm-api"]),
    (re.compile(r"README\.md", re.I), ["scm-platform"]),
]

# Heading / Source-PDF keywords for secondary domain tagging inside large files
SECTION_KEYWORDS: dict[str, list[str]] = {
    "adem": [r"autonomous.?dem", r"\badem\b", r"experience.?score", r"synthetic.?test"],
    "ztna-access-agent": [r"access.?agent", r"\bztna\b", r"private.?application", r"prisma.?access.?agent"],
    "security-policy": [r"security.?polic", r"url.?filter", r"decryption", r"app-id", r"profile.?group", r"wildfire"],
    "scm-platform": [r"strata.?cloud.?manager", r"\bscm\b", r"folder", r"snippet", r"config.?push", r"tenanc"],
    "prisma-access": [r"prisma.?access", r"globalprotect", r"explicit.?proxy", r"mobile.?user", r"remote.?network", r"service.?connection"],
    "sdwan": [r"sd-?wan", r"\bion\b", r"cloudblade", r"path.?policy", r"app.?sla"],
    "scm-api": [r"openapi", r"oauth", r"tsg", r"service.?account", r"api.?reference", r"sdk"],
    "troubleshooting": [r"troubleshoot", r"incident", r"alert", r"log", r"diagnostic"],
}

HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$")
SOURCE_PDF_RE = re.compile(r"^###\s+Source PDF:\s*(.+?)\s*$", re.I)


def docs_path() -> Path:
    raw = os.environ.get("PRISMA_DOCS_PATH", str(DEFAULT_DOCS))
    return Path(raw).expanduser()


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\-]+", "-", text.strip().lower())
    return re.sub(r"-+", "-", s).strip("-")[:80] or "section"


def extract_structure(path: Path, max_bytes: int = 8_000_000) -> dict:
    """Extract title, headings, source-pdf blocks, key terms — without loading forever."""
    size = path.stat().st_size
    text = path.read_text(encoding="utf-8", errors="replace")
    if size > max_bytes:
        text = text[:max_bytes]

    lines = text.splitlines()
    title = path.stem.replace("_", " ")
    for line in lines[:40]:
        if line.startswith("# ") and not line.startswith("##"):
            title = line[2:].strip()
            break

    headings: list[dict] = []
    sources: list[str] = []
    for i, line in enumerate(lines):
        m = SOURCE_PDF_RE.match(line)
        if m:
            sources.append(m.group(1).strip())
            headings.append(
                {
                    "level": 3,
                    "text": f"Source PDF: {m.group(1).strip()}",
                    "anchor": slugify(m.group(1)),
                    "line": i + 1,
                }
            )
            continue
        hm = HEADING_RE.match(line)
        if hm and len(hm.group(1)) <= 3:
            level = len(hm.group(1))
            htext = hm.group(2).strip()
            if htext.lower().startswith("source pdf:"):
                continue
            headings.append(
                {
                    "level": level,
                    "text": htext,
                    "anchor": slugify(htext),
                    "line": i + 1,
                }
            )

    # Key terms: capitalized multi-word + known product tokens
    blob = text[:200_000].lower()
    terms = sorted(
        {
            t
            for t in [
                "prisma access",
                "prisma sd-wan",
                "strata cloud manager",
                "globalprotect",
                "explicit proxy",
                "adem",
                "ion",
                "ztna",
                "service connection",
                "remote network",
                "app-id",
                "decryption",
            ]
            if t in blob
        }
    )

    return {
        "title": title,
        "headings": headings[:400],
        "sources": sources[:200],
        "terms": terms,
        "bytes": size,
        "truncated": size > max_bytes,
    }


def classify_file(rel: str, meta: dict) -> list[str]:
    domains: list[str] = []
    for pat, doms in FILENAME_RULES:
        if pat.search(rel.replace("\\", "/")):
            for d in doms:
                if d not in domains:
                    domains.append(d)
            break

    # Content-based enrichment from source PDF names + heading text
    hay = " ".join(meta.get("sources", []) + [h["text"] for h in meta.get("headings", [])[:80]])
    hay_l = hay.lower()
    for domain, pats in SECTION_KEYWORDS.items():
        if any(re.search(p, hay_l) for p in pats):
            if domain not in domains:
                domains.append(domain)

    return domains


def section_matches_domain(heading_text: str, domain: str) -> bool:
    pats = SECTION_KEYWORDS.get(domain, [])
    if not pats:
        return True
    return any(re.search(p, heading_text, re.I) for p in pats)


def distill_summary(domain: str, entries: list[dict], ingested: str) -> str:
    lines = [
        f"# {domain} — baked reference summary",
        "",
        f"ingested: {ingested}",
        "",
        "This summary is a **distilled index** of the local corpus. Prefer the live",
        "layer (`PRISMA_DOCS_PATH`) for full procedures. Label claims:",
        "`VERIFIED (source file/URL) | INFERRED | ASSUMED`.",
        "",
        "## Corpus map",
        "",
    ]
    for e in entries:
        lines.append(f"### {e['title']}")
        lines.append(f"- path: `{e['rel']}`")
        lines.append(f"- size: {e['bytes']} bytes")
        if e.get("terms"):
            lines.append(f"- terms: {', '.join(e['terms'][:12])}")
        # Claims as pointers — not pasted corpus bodies
        relevant = [
            h
            for h in e.get("headings", [])
            if h["level"] <= 3 and section_matches_domain(h["text"], domain)
        ][:25]
        if not relevant:
            relevant = [h for h in e.get("headings", []) if h["level"] <= 2][:15]
        for h in relevant:
            lines.append(
                f"- topic: {h['text']} — source: `{e['rel']}`#{h['anchor']} (line {h['line']})"
            )
        if e.get("sources"):
            lines.append("- Source PDFs (sample):")
            for s in e["sources"][:12]:
                lines.append(f"  - {s} — source: `{e['rel']}`")
        lines.append("")
    lines.extend(
        [
            "## Gotchas",
            "",
            f"- Large PDF-extract files must be **searched**, never read whole — source: corpus README.",
            f"- Version-specific SCM/SASE UI paths change often — verify on docs.paloaltonetworks.com / pan.dev before asserting.",
            f"- Filename typo `prisma_sase_architecure.md` is intentional in the corpus.",
            "",
            "## Live layer",
            "",
            "Set `PRISMA_DOCS_PATH` (machine-specific default documented in the amir_project plugin README, section 'Prisma docs corpus').",
            "Use `references/index.json` to open only matching sections.",
            "",
        ]
    )
    return "\n".join(lines)


def write_domain(domain: str, files_meta: list[dict], ingested: str) -> None:
    ref = SKILLS_ROOT / SKILL_DIRS.get(domain, domain) / "references"
    ref.mkdir(parents=True, exist_ok=True)
    index = {
        "domain": domain,
        "ingested": ingested,
        "topic_index": [],
    }
    for e in files_meta:
        topics = []
        for h in e.get("headings", []):
            if h["level"] > 3:
                continue
            if domain not in ("scm-platform", "troubleshooting") and not section_matches_domain(
                h["text"], domain
            ):
                # Still index top-level file entry once
                continue
            topics.append(
                {
                    "topic": h["text"],
                    "file": e["rel"],
                    "anchor": h["anchor"],
                    "line": h["line"],
                }
            )
        if not topics:
            topics.append(
                {
                    "topic": e["title"],
                    "file": e["rel"],
                    "anchor": "top",
                    "line": 1,
                }
            )
        index["topic_index"].extend(topics[:80])
        index.setdefault("files", []).append(
            {"path": e["rel"], "title": e["title"], "bytes": e["bytes"]}
        )

    (ref / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    (ref / "summary.md").write_text(
        distill_summary(domain, files_meta, ingested), encoding="utf-8"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest Prisma SASE markdown corpus into skill references")
    ap.add_argument("--docs", type=Path, default=None, help="Override PRISMA_DOCS_PATH")
    ap.add_argument("--json-report", action="store_true")
    args = ap.parse_args()

    root = args.docs or docs_path()
    if not root.is_dir():
        print(f"[prisma:ingest] NOT DOABLE — docs path missing: {root}", file=sys.stderr)
        print(
            "Set PRISMA_DOCS_PATH or pass --docs. Baked references (if any) left unchanged.",
            file=sys.stderr,
        )
        return 2

    ingested = date.today().isoformat()
    classified: dict[str, list[dict]] = {d: [] for d in DOMAINS}
    unclassified: list[dict] = []
    all_md = sorted(root.rglob("*.md"))
    print(f"[prisma:ingest] root={root}")
    print(f"[prisma:ingest] markdown files={len(all_md)}")

    for path in all_md:
        rel = str(path.relative_to(root)).replace("\\", "/")
        meta = extract_structure(path)
        meta["rel"] = rel
        domains = classify_file(rel, meta)
        if not domains:
            unclassified.append({"path": rel, "title": meta["title"], "reason": "no rule matched"})
            continue
        for d in domains:
            classified[d].append(meta)

    for d in DOMAINS:
        write_domain(d, classified[d], ingested)

    report = {
        "ingested": ingested,
        "docs_path": str(root),
        "total_md": len(all_md),
        "classified": {d: len(classified[d]) for d in DOMAINS},
        "unclassified": unclassified,
        "coverage": round((len(all_md) - len(unclassified)) / len(all_md), 4) if all_md else 0,
    }
    (PLUGIN_ROOT / "references_unclassified.json").write_text(
        json.dumps({"unclassified": unclassified, "ingested": ingested}, indent=2) + "\n",
        encoding="utf-8",
    )
    report_path = PLUGIN_ROOT / "ingest-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"[prisma:ingest] coverage={report['coverage']*100:.1f}%")
    print(f"[prisma:ingest] unclassified={len(unclassified)}")
    for u in unclassified:
        print(f"  - {u['path']}: {u['reason']}")
    for d in DOMAINS:
        print(f"  {d}: {len(classified[d])} file(s)")
    print(f"[prisma:ingest] report -> {report_path}")
    if args.json_report:
        print(json.dumps(report))
    if report["coverage"] < 0.95:
        print("[prisma:ingest] WARN: coverage < 95%", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
