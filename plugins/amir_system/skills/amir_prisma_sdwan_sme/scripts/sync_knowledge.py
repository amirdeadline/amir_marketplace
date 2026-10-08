#!/usr/bin/env python3
"""sync_knowledge.py - one-way copy of the Prisma SD-WAN SME research corpus into this skill.

Source: the research workspace (editing place), by default `research_root` in config.json.
Target: <skill>/knowledge. Copies notes/, scenarios/, index/ and the registers listed in
INCLUDE, then writes MANIFEST.json (path, size, SHA-256 per file). Never touches the source.

  python scripts/sync_knowledge.py            # copy and write the manifest
  python scripts/sync_knowledge.py --check    # report differences only, change nothing
  python scripts/sync_knowledge.py --source <dir> --target <dir>
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = SKILL_DIR / "knowledge"
DEFAULT_CONFIG = SKILL_DIR / "config.json"
INCLUDE_DIRS = ("notes", "scenarios", "index")
INCLUDE_FILES = ("03_SOURCE_CATALOG.md", "04_KNOWLEDGE_GAPS.md", "05_UNRESOLVED_QUESTIONS.md",
                 "06_SME_READINESS_ASSESSMENT.md")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_files(source: Path) -> list[Path]:
    files: list[Path] = []
    for sub in INCLUDE_DIRS:
        folder = source / sub
        if folder.is_dir():
            files.extend(sorted(p for p in folder.rglob("*.md") if p.is_file()))
    for name in INCLUDE_FILES:
        path = source / name
        if path.is_file():
            files.append(path)
    return files


def plan(source: Path, target: Path) -> dict:
    """Return {'copy': [...], 'unchanged': [...], 'stale': [...]} relative paths."""
    wanted = {p.relative_to(source).as_posix(): p for p in source_files(source)}
    existing = {p.relative_to(target).as_posix(): p for p in target.rglob("*.md")} if target.is_dir() else {}
    copy, unchanged = [], []
    for relpath, src in wanted.items():
        dst = existing.get(relpath)
        if dst and sha256_of(dst) == sha256_of(src):
            unchanged.append(relpath)
        else:
            copy.append(relpath)
    stale = sorted(set(existing) - set(wanted))
    return {"copy": sorted(copy), "unchanged": sorted(unchanged), "stale": stale}


def write_manifest(source: Path, target: Path) -> Path:
    files = []
    for path in sorted(target.rglob("*.md")):
        files.append({"path": path.relative_to(target).as_posix(), "size": path.stat().st_size,
                      "sha256": sha256_of(path)})
    meta = {
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_root": str(source),
        "file_count": len(files),
        "files": files,
    }
    manifest = target / "MANIFEST.json"
    manifest.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return manifest


def sync(source: Path, target: Path, check_only: bool) -> int:
    if not (source / "notes").is_dir():
        print(f"source has no notes/ folder: {source}")
        return 2
    result = plan(source, target)
    print(f"copy {len(result['copy'])}, unchanged {len(result['unchanged'])}, stale in target {len(result['stale'])}")
    for relpath in result["copy"]:
        print(f"  COPY   {relpath}")
    for relpath in result["stale"]:
        print(f"  STALE  {relpath}")
    if check_only:
        return 1 if (result["copy"] or result["stale"]) else 0
    for relpath in result["copy"]:
        dst = target / relpath
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relpath, dst)
    for relpath in result["stale"]:
        (target / relpath).unlink()
    manifest = write_manifest(source, target)
    print(f"manifest written: {manifest}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", help="research workspace (default: research_root in config.json)")
    parser.add_argument("--target", default=str(DEFAULT_TARGET))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--check", action="store_true", help="report only; change nothing")
    args = parser.parse_args(argv)
    source = args.source
    if not source and Path(args.config).is_file():
        try:
            source = json.loads(Path(args.config).read_text(encoding="utf-8")).get("research_root")
        except ValueError:
            source = None
    if not source:
        print("no source: pass --source or set research_root in config.json")
        return 2
    return sync(Path(source), Path(args.target), args.check)


if __name__ == "__main__":
    sys.exit(main())
