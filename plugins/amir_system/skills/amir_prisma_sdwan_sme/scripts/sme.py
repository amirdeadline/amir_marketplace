#!/usr/bin/env python3
"""sme.py - read-only lookup helper for the amir_prisma_sdwan_sme knowledge layer.

The knowledge layer is a synced copy of the Prisma SD-WAN SME research corpus
(notes with claims registers, worked scenarios, indexes, source catalog, gap register).
This helper returns only the rows an agent needs, so the agent never has to load the
whole corpus into the conversation. It never writes anything except through
sync_knowledge.py (a separate script).

Commands:
  brief                      where the knowledge is, its manifest date, counts, label scheme, KB helper status
  route WORD [...]           router rows (intent -> notes -> sources -> label ceiling) matching all words
  find WORD [...] [--limit N] lines in notes/scenarios/indexes containing all words (titles ranked first)
  note FRAGMENT [--section TEXT]   print one note resolved by a unique path fragment (e.g. 02-network/08)
  scenario ID                print one scenario (S01..S14) or the scenario index with "index"
  term WORD [...]            rows of the term index matching the words
  gap KG-NNN                 every register and question row that mentions the gap ID
  src SRC-NNNNNN [--kb]      source-catalog rows; with --kb also run the sibling kbq.py for the live KB record
  verify                     compare knowledge files with MANIFEST.json (exit 1 on drift or missing files)

Exit codes: 0 ok, 1 not found / drift, 2 knowledge folder missing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_KNOWLEDGE = SKILL_DIR / "knowledge"
DEFAULT_CONFIG = SKILL_DIR / "config.json"
LABELS = ("VERIFIED", "CORROBORATED", "INFERRED", "UNVERIFIED", "CONFLICTED", "OBSOLETE")
EVIDENCE_TYPES = ("DOC", "SCENARIO", "LAB")
SEARCH_DIRS = ("notes", "scenarios", "index")
TEXT_FILES = ("03_SOURCE_CATALOG.md", "04_KNOWLEDGE_GAPS.md", "05_UNRESOLVED_QUESTIONS.md",
              "06_SME_READINESS_ASSESSMENT.md")


class KnowledgeNotFound(Exception):
    """Raised when the knowledge folder does not exist."""


# ---- configuration -----------------------------------------------------------------

def load_config(config_path: Path = DEFAULT_CONFIG) -> dict:
    if not Path(config_path).is_file():
        return {}
    try:
        return json.loads(Path(config_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def resolve_knowledge(cli_root: str | None = None) -> Path:
    root = Path(cli_root) if cli_root else DEFAULT_KNOWLEDGE
    if not (root / "index" / "00_NOTE_INDEX.md").is_file():
        raise KnowledgeNotFound(f"knowledge folder not found or incomplete: {root}")
    return root


def kbq_path(config: dict) -> Path | None:
    candidates = []
    if config.get("kbq_path"):
        candidates.append(Path(config["kbq_path"]))
    candidates.append(SKILL_DIR.parent / "amir_prisma_sdwan" / "scripts" / "kbq.py")
    candidates.append(Path.home() / ".claude" / "skills" / "amir_prisma_sdwan" / "scripts" / "kbq.py")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def kbq_command(kbq: Path, config: dict, src_ids: list[str]) -> list[str]:
    """kbq.py takes --root as a global option, so it must come before the subcommand."""
    command = [sys.executable, str(kbq)]
    if config.get("kb_root"):
        command.extend(["--root", config["kb_root"]])
    command.extend(["src", *src_ids])
    return command


# ---- helpers -------------------------------------------------------------------------

def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_text_files(root: Path):
    for sub in SEARCH_DIRS:
        folder = root / sub
        if folder.is_dir():
            for path in sorted(folder.rglob("*.md")):
                yield path
    for name in TEXT_FILES:
        path = root / name
        if path.is_file():
            yield path


def words_match(text: str, words: list[str]) -> bool:
    lowered = text.lower()
    return all(word.lower() in lowered for word in words)


def table_rows(path: Path):
    """Yield (line_number, line) for Markdown table body rows."""
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("|") and not line.startswith("|---") and not re.match(r"^\|\s*(ID|Term|Intent|Note|Claim)\s*\|", line):
            yield number, line


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


# ---- commands --------------------------------------------------------------------------

def cmd_brief(root: Path, config: dict) -> int:
    manifest = root / "MANIFEST.json"
    meta = {}
    if manifest.is_file():
        try:
            meta = json.loads(manifest.read_text(encoding="utf-8"))
        except ValueError:
            meta = {}
    notes = list((root / "notes").rglob("*.md")) if (root / "notes").is_dir() else []
    scenarios = [p for p in (root / "scenarios").glob("S*.md")] if (root / "scenarios").is_dir() else []
    print(f"Knowledge root: {root}")
    print(f"Manifest: generated {meta.get('generated_at', 'unknown')} from {meta.get('source_root', 'unknown')}; "
          f"{len(meta.get('files', []))} files listed")
    print(f"Notes: {len(notes)} | Scenarios: {len(scenarios)} | Indexes: index/00_NOTE_INDEX.md, 01_TERM_INDEX.md, 02_ROUTER.md")
    print("Registers: 03_SOURCE_CATALOG.md (SRC/WS IDs), 04_KNOWLEDGE_GAPS.md (KG IDs), 05_UNRESOLVED_QUESTIONS.md, "
          "06_SME_READINESS_ASSESSMENT.md")
    print("Claim labels: " + " / ".join(LABELS) + "; evidence types: " + " / ".join(EVIDENCE_TYPES)
          + " (nothing is LAB until lab access is granted)")
    print("Sibling label map: VERIFIED~CONFIRMED, UNVERIFIED(internal)~INTERNAL, INFERRED~INFERENCE, OPEN gap~UNKNOWN")
    kbq = kbq_path(config)
    print(f"KB helper (kbq.py): {kbq if kbq else 'NOT FOUND - KB lookups unavailable; answer from the knowledge layer only'}")
    research = config.get("research_root")
    if research:
        state = "present" if Path(research).is_dir() else "absent on this machine"
        print(f"Research workspace (editing place, not needed to answer): {research} ({state})")
    print("Start: `route <intent words>` -> `note <fragment>` -> `src SRC-... --kb` when the primary text is needed.")
    return 0


def cmd_route(root: Path, words: list[str]) -> int:
    router = root / "index" / "02_ROUTER.md"
    hits = [line for _, line in table_rows(router) if words_match(line, words)]
    if not hits:
        print(f"No router row matches {' '.join(words)!r}. Try `find` or open index/02_ROUTER.md.")
        return 1
    print("| Intent | Open first | Then | Primary sources | Label ceiling today |")
    for line in hits:
        print(line)
    return 0


def cmd_find(root: Path, words: list[str], limit: int) -> int:
    title_hits, line_hits = [], []
    for path in iter_text_files(root):
        lines = path.read_text(encoding="utf-8").splitlines()
        title = lines[0] if lines else ""
        if words_match(title, words):
            title_hits.append(f"{rel(path, root)}:1: {title[:160]}")
        for number, line in enumerate(lines, 1):
            if words_match(line, words):
                line_hits.append(f"{rel(path, root)}:{number}: {line.strip()[:220]}")
    if not title_hits and not line_hits:
        print(f"No match for {' '.join(words)!r} in the knowledge layer.")
        return 1
    shown = 0
    for block, label in ((title_hits, "Title matches"), (line_hits, "Line matches")):
        if block:
            print(f"== {label} ({len(block)}) ==")
        for item in block:
            if shown >= limit:
                print(f"... truncated; {len(title_hits) + len(line_hits) - shown} more. Narrow the words or raise --limit.")
                return 0
            print(item)
            shown += 1
    return 0


def resolve_note(root: Path, fragment: str) -> Path:
    fragment_norm = fragment.replace("\\", "/").lower()
    candidates = [p for p in (root / "notes").rglob("*.md") if fragment_norm in rel(p, root).lower()]
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise FileNotFoundError(f"no note matches {fragment!r}")
    names = "\n  ".join(rel(p, root) for p in candidates)
    raise FileNotFoundError(f"{len(candidates)} notes match {fragment!r}; be more specific:\n  {names}")


def cmd_note(root: Path, fragment: str, section: str | None) -> int:
    try:
        path = resolve_note(root, fragment)
    except FileNotFoundError as exc:
        print(exc)
        return 1
    text = path.read_text(encoding="utf-8")
    if section:
        parts = re.split(r"(?m)^(## .*)$", text)
        # parts: [preamble, heading, body, heading, body, ...]
        for index in range(1, len(parts) - 1, 2):
            if section.lower() in parts[index].lower():
                print(f"# {rel(path, root)}\n{parts[index]}{parts[index + 1].rstrip()}")
                return 0
        print(f"section {section!r} not found in {rel(path, root)}")
        return 1
    print(f"# {rel(path, root)}\n{text}")
    return 0


def cmd_scenario(root: Path, ident: str) -> int:
    folder = root / "scenarios"
    if ident.lower() == "index":
        path = folder / "00_SCENARIO_INDEX.md"
    else:
        matches = list(folder.glob(f"{ident.upper()}-*.md"))
        if len(matches) != 1:
            print(f"scenario {ident!r} not found; use S01..S14 or 'index'")
            return 1
        path = matches[0]
    print(f"# {rel(path, root)}\n{path.read_text(encoding='utf-8')}")
    return 0


def cmd_term(root: Path, words: list[str]) -> int:
    hits = [line for _, line in table_rows(root / "index" / "01_TERM_INDEX.md") if words_match(line, words)]
    if not hits:
        print(f"No term-index row matches {' '.join(words)!r}; try `find`.")
        return 1
    for line in hits:
        print(line)
    return 0


def cmd_gap(root: Path, gap_id: str) -> int:
    gap_id = gap_id.upper()
    if not re.fullmatch(r"KG-\d{3}[A-Z]?", gap_id):
        print("gap ID must look like KG-079")
        return 1
    found = False
    for name in ("04_KNOWLEDGE_GAPS.md", "05_UNRESOLVED_QUESTIONS.md"):
        path = root / name
        if not path.is_file():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if gap_id in line:
                print(f"{name}:{number}: {line.strip()[:400]}")
                found = True
    notes_with_gap = [rel(p, root) for p in iter_text_files(root)
                      if gap_id in p.read_text(encoding="utf-8") and p.parts[-3:-1] != ()]
    notes_with_gap = [n for n in notes_with_gap if n.startswith(("notes/", "scenarios/"))]
    if notes_with_gap:
        print("Referenced by: " + ", ".join(notes_with_gap))
        found = True
    if not found:
        print(f"{gap_id} not found in the registers.")
        return 1
    return 0


def cmd_src(root: Path, config: dict, src_ids: list[str], use_kb: bool) -> int:
    catalog = root / "03_SOURCE_CATALOG.md"
    status = 0
    for src_id in src_ids:
        rows = [line for _, line in table_rows(catalog) if src_id.upper() in line.upper()]
        if rows:
            print(f"== {src_id} in 03_SOURCE_CATALOG.md ==")
            for line in rows:
                print(line[:400])
        else:
            print(f"== {src_id}: not in 03_SOURCE_CATALOG.md ==")
            status = 1
    if use_kb:
        kbq = kbq_path(config)
        if not kbq:
            print("kbq.py not found; cannot query the live KB registry.")
            return 1
        command = kbq_command(kbq, config, src_ids)
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(f"== live KB registry via {kbq.name} (exit {result.returncode}) ==")
        print(result.stdout.strip() or result.stderr.strip())
        status = status or (1 if result.returncode else 0)
    return status


def cmd_verify(root: Path) -> int:
    manifest = root / "MANIFEST.json"
    if not manifest.is_file():
        print("MANIFEST.json missing; run scripts/sync_knowledge.py")
        return 1
    meta = json.loads(manifest.read_text(encoding="utf-8"))
    listed = {item["path"]: item["sha256"] for item in meta.get("files", [])}
    problems = 0
    for path_str, digest in listed.items():
        path = root / path_str
        if not path.is_file():
            print(f"MISSING  {path_str}")
            problems += 1
        elif sha256_of(path) != digest:
            print(f"CHANGED  {path_str}")
            problems += 1
    present = {rel(p, root) for p in root.rglob("*.md")}
    for extra in sorted(present - set(listed)):
        print(f"UNLISTED {extra}")
        problems += 1
    if problems:
        print(f"{problems} problem(s); run sync_knowledge.py (or sync_knowledge.py --check) to reconcile")
        return 1
    print(f"OK: {len(listed)} files match MANIFEST.json (generated {meta.get('generated_at')})")
    return 0


# ---- entry point ------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--knowledge", help="knowledge folder (default: <skill>/knowledge)")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="config.json path")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("brief")
    p = sub.add_parser("route"); p.add_argument("words", nargs="+")
    p = sub.add_parser("find"); p.add_argument("words", nargs="+"); p.add_argument("--limit", type=int, default=40)
    p = sub.add_parser("note"); p.add_argument("fragment"); p.add_argument("--section")
    p = sub.add_parser("scenario"); p.add_argument("ident")
    p = sub.add_parser("term"); p.add_argument("words", nargs="+")
    p = sub.add_parser("gap"); p.add_argument("gap_id")
    p = sub.add_parser("src"); p.add_argument("src_ids", nargs="+"); p.add_argument("--kb", action="store_true")
    sub.add_parser("verify")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(Path(args.config))
    try:
        root = resolve_knowledge(args.knowledge)
    except KnowledgeNotFound as exc:
        print(exc)
        return 2
    if args.command == "brief":
        return cmd_brief(root, config)
    if args.command == "route":
        return cmd_route(root, args.words)
    if args.command == "find":
        return cmd_find(root, args.words, args.limit)
    if args.command == "note":
        return cmd_note(root, args.fragment, args.section)
    if args.command == "scenario":
        return cmd_scenario(root, args.ident)
    if args.command == "term":
        return cmd_term(root, args.words)
    if args.command == "gap":
        return cmd_gap(root, args.gap_id)
    if args.command == "src":
        return cmd_src(root, config, args.src_ids, args.kb)
    if args.command == "verify":
        return cmd_verify(root)
    return 1


if __name__ == "__main__":
    if os.name == "nt":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    sys.exit(main())
