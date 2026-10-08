#!/usr/bin/env python3
"""kbq.py - small, read-only lookup helper for the Palo Alto Prisma SASE knowledge base (KB).

It returns only the rows an agent needs, so large index files (source registry,
5 MB Confluence page index, 4 MB PDF-extract containers) never have to be loaded
into the conversation. It never writes to the KB.

Commands:
  root                         where the KB is and how it was found
  brief                        session start: entry points, negative routing, topic routes, authority scale
  src ID [ID ...]              registry record(s): authority, evidence label, freshness, local location
  find WORD [WORD ...]         search registry titles, notes and paths (all words must match)
  pages WORD [...] [--product sd_wan]   search the Confluence page index (titles + headings)
  term WORD                    terminology entry: canonical name, old names, look-alikes
  grep ID PATTERN              regex search inside ONE registered source (embedded PDFs use their line range)
  check-map FILE               verify that every backticked KB path in a Markdown file exists

KB root resolution order: --root, PRISMA_DOCS_PATH, the current folder or a parent,
then "kb_root" in config.json next to this skill. Exit code 2 = KB not found.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

KB_DIR = "palo-alto-knowledge-base"
SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = SKILL_DIR / "config.json"
MARKER_PREFIX = "### Source PDF:"
CONTAINER_DIRS = ("", f"{KB_DIR}/corpus/containers", f"{KB_DIR}/source-material/containers")
TOC_LINE = re.compile(r"\.{6,}\s*\d+\s*$")  # table-of-contents rows ("Add a Rule ........ 448")


class KbNotFound(Exception):
    """Raised when no valid KB root can be located."""


# ---- root resolution -------------------------------------------------------------

def is_kb_root(path: Path | None) -> bool:
    return bool(path) and (Path(path) / KB_DIR / "PaloAlto.md").is_file()


def _config_root(config_path: Path | None) -> Path | None:
    if not config_path or not Path(config_path).is_file():
        return None
    try:
        value = json.loads(Path(config_path).read_text(encoding="utf-8")).get("kb_root")
    except (OSError, ValueError):
        return None
    return Path(value) if value else None


def resolve_root(cli_root=None, env=None, cwd=None, config_path=DEFAULT_CONFIG):
    """Return (root, how). An explicit --root must be valid; other candidates are skipped if invalid."""
    env = os.environ if env is None else env
    if cli_root:
        if is_kb_root(Path(cli_root)):
            return Path(cli_root), "--root"
        raise KbNotFound(f"--root {cli_root} has no {KB_DIR}/PaloAlto.md")
    env_root = env.get("PRISMA_DOCS_PATH")
    if env_root and is_kb_root(Path(env_root)):
        return Path(env_root), "PRISMA_DOCS_PATH"
    here = Path(cwd or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if is_kb_root(candidate):
            return candidate, "current folder"
    cfg = _config_root(config_path)
    if is_kb_root(cfg):
        return cfg, "config.json"
    raise KbNotFound("no candidate contained palo-alto-knowledge-base/PaloAlto.md")


# ---- shared loaders ------------------------------------------------------------------

def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry(root: Path) -> dict:
    return _read_json(root / KB_DIR / "source-registry.json")


def _sources_by_id(registry: dict) -> dict:
    return {s.get("source_id"): s for s in registry.get("sources", [])}


def rank_label(rank) -> str:
    if isinstance(rank, int) and 1 <= rank <= 4:
        return f"rank {rank} official -> may support CONFIRMED"
    if rank == 9:
        return "rank 9 internal -> INTERNAL (verify freshness)"
    if rank == 10:
        return "rank 10 expert inference -> INFERENCE"
    return f"rank {rank} not defined in authority_scale -> treat as INTERNAL until clarified"


def resolve_local(root: Path, rel: str) -> Path | None:
    """Registry and index paths are relative to the repo root or to palo-alto-knowledge-base/."""
    if not rel:
        return None
    for base in (root, root / KB_DIR, root / KB_DIR / "corpus"):
        candidate = base / rel
        if candidate.exists():
            return candidate
    return None


# ---- embedded official PDFs (inside container files) ------------------------------

def _marker_for(src: dict) -> str:
    match = re.search(r"locate via '([^']+)'", src.get("notes") or "")
    if match:
        return match.group(1).strip()
    title = re.sub(r"\.pdf$", "", src.get("title", ""), flags=re.IGNORECASE)
    return f"{MARKER_PREFIX} {title}".strip()


def _container_paths(root: Path, name: str) -> list[Path]:
    return [root / d / name for d in CONTAINER_DIRS if (root / d / name).is_file()]


def locate_embedded(root: Path, src: dict) -> list[tuple[Path, int, int]]:
    """Return (container, start_line, end_line) for each container holding the source's marker."""
    marker = _marker_for(src)
    names = [n for n in src.get("local_path", "")[len("embedded:"):].split("|") if n]
    found = []
    for name in names:
        for path in _container_paths(root, name)[:1]:  # first existing copy is canonical
            span = _marker_span(path, marker)
            if span:
                found.append((path, *span))
    return found


def _lines(path: Path) -> list[str]:
    """Split on '\\n' only, so line numbers match grep -n and editor line numbers."""
    lines = path.read_bytes().decode("utf-8", errors="replace").split("\n")
    return lines[:-1] if lines and lines[-1] == "" else lines


def _marker_span(path: Path, marker: str) -> tuple[int, int] | None:
    lines = _lines(path)
    start = None
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if start is None and stripped == marker:
            start = number
        elif start is not None and stripped.startswith(MARKER_PREFIX):
            return start, number - 1
    return (start, len(lines)) if start else None


# ---- commands --------------------------------------------------------------------------

def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _location_lines(root: Path, src: dict) -> list[str]:
    local = src.get("local_path") or ""
    if local.startswith("embedded:"):
        spans = locate_embedded(root, src)
        if not spans:
            return [f"  location: embedded marker '{_marker_for(src)}' NOT FOUND in {local}"]
        return [f"  location: {_rel(root, p)} lines {a}-{b}" for p, a, b in spans]
    path = resolve_local(root, local)
    if path:
        return [f"  location: {_rel(root, path)} (exists)"]
    if not local:
        return [f"  location: no local copy; external {src.get('canonical_url') or 'URL not recorded'}"]
    return [f"  location: {local} (NOT FOUND locally)"]


def describe_sources(root: Path, ids: list[str]) -> str:
    by_id = _sources_by_id(load_registry(root))
    blocks = []
    for raw in ids:
        sid = raw.strip().upper()
        src = by_id.get(sid)
        if not src:
            blocks.append(f"{sid}: NOT IN REGISTRY (do not cite as a registered source; cite the file path)")
            continue
        lines = [
            f"{sid}: {src.get('title', '')}",
            f"  authority: {rank_label(src.get('authority_rank'))}; type {src.get('source_type')}; "
            f"publisher {src.get('publisher')}",
            f"  freshness: published {src.get('publication_date')}, updated {src.get('last_updated_date')}, "
            f"retrieved {src.get('retrieved_date')}, version '{src.get('document_version', '')}'",
        ]
        if src.get("superseded_by"):
            lines.append(f"  SUPERSEDED BY: {', '.join(src['superseded_by'])}")
        lines += _location_lines(root, src)
        if src.get("notes"):
            lines.append(f"  notes: {src['notes'][:300]}")
        blocks.append("\n".join(lines))
    return "\n".join(blocks)


def _words_match(text: str, words: list[str]) -> bool:
    lowered = text.lower()
    return all(w.lower() in lowered for w in words)


def find_sources(registry: dict, words: list[str], limit: int = 15) -> list[dict]:
    hits = []
    for src in registry.get("sources", []):
        haystack = " ".join(str(src.get(k, "")) for k in ("source_id", "title", "notes", "local_path", "product"))
        if _words_match(haystack, words):
            hits.append(src)
    return hits[:limit]


def search_pages(root: Path, words: list[str], product: str | None = None, limit: int = 15) -> str:
    index = root / KB_DIR / "confluence-index" / "pages-index.jsonl"
    scored = []
    with index.open(encoding="utf-8") as handle:
        for line in handle:
            page = json.loads(line)
            if product and page.get("product") != product:
                continue
            title = page.get("title", "")
            if not _words_match(title + " " + " ".join(page.get("headings") or []), words):
                continue
            scored.append((2 if _words_match(title, words) else 1, page.get("words") or 0, page))
    scored.sort(key=lambda item: (-item[0], -item[1]))
    rows = []
    for _, _, page in scored[:limit]:
        local = "yes" if resolve_local(root, page.get("file", "")) else "NO"
        rows.append(f"{page.get('id')} | {page.get('title')} | {page.get('product')} | {page.get('type')} | "
                    f"{page.get('words')} words | {page.get('file')} | local file: {local}")
    return "\n".join(rows) if rows else "no matching Confluence pages"


def lookup_term(root: Path, word: str) -> str:
    data = _read_json(root / KB_DIR / "terminology.json")
    whole_word = re.compile(rf"(?<![\w-]){re.escape(word)}(?![\w-])", re.IGNORECASE)
    names = ("canonical", "abbreviations", "historical", "confused_with")
    terms = data.get("terms", [])
    hits = [t for t in terms if whole_word.search(json.dumps([t.get(k) for k in names]))]
    hits = hits or [t for t in terms if whole_word.search(json.dumps(t))]
    return "\n".join(json.dumps(t, ensure_ascii=False) for t in hits) if hits else f"no terminology entry for '{word}'"


def grep_source(root: Path, sid: str, pattern: str, context: int = 1, limit: int = 30) -> str:
    src = _sources_by_id(load_registry(root)).get(sid.upper())
    if not src:
        return f"{sid}: NOT IN REGISTRY"
    local = src.get("local_path") or ""
    if local.startswith("embedded:"):
        spans = locate_embedded(root, src)[:1]
    else:
        path = resolve_local(root, local)
        spans = [(path, 1, 10**9)] if path and path.is_file() else []
    if not spans:
        return f"{sid}: no searchable local text"
    path, first, last = spans[0]
    regex = re.compile(pattern, re.IGNORECASE)
    lines = _lines(path)
    last = min(last, len(lines))
    out, hits = [f"{sid} in {_rel(root, path)} lines {first}-{last}:"], 0
    for i in range(first - 1, last):
        if regex.search(lines[i]) and not TOC_LINE.search(lines[i]):
            hits += 1
            lo, hi = max(first - 1, i - context), min(last, i + context + 1)
            out += [f"  {n + 1}: {lines[n][:240]}" for n in range(lo, hi)] + ["  --"]
            if hits >= limit:
                out.append(f"  (stopped at {limit} matches)")
                break
    return "\n".join(out) if hits else f"{sid}: no match for /{pattern}/ in lines {first}-{last}"


def brief(root: Path) -> str:
    kmap = _read_json(root / KB_DIR / "knowledge-map.json")
    registry = load_registry(root)
    ranks: dict = {}
    for src in registry.get("sources", []):
        ranks[src.get("authority_rank")] = ranks.get(src.get("authority_rank"), 0) + 1
    ids = sorted(s.get("source_id", "") for s in registry.get("sources", []))
    lines = [
        f"KB root: {root}",
        f"Retrieval spec (authoritative): {root / '.ai/prompts/kb_use.md'}",
        f"Entry: {KB_DIR}/PaloAlto.md",
        "Product indexes:",
        *[f"  {name}: {KB_DIR}/{p.get('index')}" for name, p in kmap.get("products", {}).items()],
        "Negative routing rules (always apply):",
        *[f"  - {rule}" for rule in kmap.get("negative_routing_rules", [])],
        "Topic routes:",
        *[f"  {k}: {v}" for k, v in kmap.get("corpus_mirror", {}).get("topic_routes", {}).items()],
        "Product dependency edges:",
        *[f"  {e.get('from')} -> {e.get('to')}: {e.get('purpose')}" for e in kmap.get("dependency_graph", [])],
        f"Authority scale: {registry.get('authority_scale')}",
        f"Registry: {len(ids)} sources ({ids[0] if ids else '-'}..{ids[-1] if ids else '-'}); by rank {ranks}",
    ]
    return "\n".join(lines)


def check_map(root: Path, map_file: Path) -> list[str]:
    text = Path(map_file).read_text(encoding="utf-8")
    missing = []
    for ref in re.findall(r"`([^`\n]+)`", text):
        if "/" not in ref or "<" in ref or ref.startswith(("http", "python", "graphify", "SRC-")):
            continue
        ref = ref.strip()
        if "*" in ref or "{" in ref:
            pattern = re.sub(r"\{[^}]+\}", "*", ref)
            if not any(glob.glob(str(base / pattern)) for base in (root, root / KB_DIR)):
                missing.append(ref)
        elif not resolve_local(root, ref.rstrip("/")):
            missing.append(ref)
    return missing


# ---- CLI -----------------------------------------------------------------------------

def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", help="KB root (folder that contains palo-alto-knowledge-base/)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("root")
    sub.add_parser("brief")
    sub.add_parser("src").add_argument("ids", nargs="+")
    find = sub.add_parser("find")
    find.add_argument("words", nargs="+")
    find.add_argument("--limit", type=int, default=15)
    pages = sub.add_parser("pages")
    pages.add_argument("words", nargs="+")
    pages.add_argument("--product", help="e.g. sd_wan, prisma_access, cie, scm")
    pages.add_argument("--limit", type=int, default=15)
    sub.add_parser("term").add_argument("word")
    grep = sub.add_parser("grep")
    grep.add_argument("id")
    grep.add_argument("pattern")
    grep.add_argument("--context", type=int, default=1)
    grep.add_argument("--limit", type=int, default=30)
    sub.add_parser("check-map").add_argument("file")
    return parser


def _run(args, root: Path, how: str) -> int:
    if args.command == "root":
        print(f"{root}  (found via {how})")
    elif args.command == "brief":
        print(brief(root))
    elif args.command == "src":
        print(describe_sources(root, args.ids))
    elif args.command == "find":
        hits = find_sources(load_registry(root), args.words, args.limit)
        print("\n".join(f"{h['source_id']} | rank {h.get('authority_rank')} | {h.get('title')} | "
                        f"{h.get('local_path')}" for h in hits) or "no matching registry entries")
    elif args.command == "pages":
        print(search_pages(root, args.words, args.product, args.limit))
    elif args.command == "term":
        print(lookup_term(root, args.word))
    elif args.command == "grep":
        print(grep_source(root, args.id, args.pattern, args.context, args.limit))
    elif args.command == "check-map":
        missing = check_map(root, Path(args.file))
        print("all map paths exist" if not missing else "MISSING:\n" + "\n".join(f"  {m}" for m in missing))
        return 1 if missing else 0
    return 0


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = _parser().parse_args(argv)
    try:
        root, how = resolve_root(cli_root=args.root)
    except KbNotFound as exc:
        print(f"KB root not found: {exc}. Set PRISMA_DOCS_PATH or kb_root in {DEFAULT_CONFIG}.", file=sys.stderr)
        return 2
    return _run(args, root, how)


if __name__ == "__main__":
    sys.exit(main())
