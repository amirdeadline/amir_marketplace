#!/usr/bin/env python3
"""mddoc.py - keep official Markdown documents numbered, valid and traceable.

Commands:
  number FILE [--check]   renumber headings (## 1., ### 1.1, #### 1.1.1; appendices lettered
                          "## Appendix A." / "### A.1") and update internal #anchor links.
                          --check only reports; exit 1 if numbers would change.
  check FILE [--evidence REGISTER.md] [--registry source-registry.json]
             [--max-section-words N] [--allow-acronyms A,B]
                          structure, links, tables, style and evidence checks.
                          A sibling <stem>.evidence.md is used automatically when present.
  outline FILE            heading tree with line numbers and word counts.

Exit codes: 0 = no errors, 1 = errors found (or numbering would change), 2 = file/usage error.
Only the Python standard library is used.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
CLOSING_HASHES_RE = re.compile(r"(?:^|[ \t]+)#+[ \t]*$")
HEADING_ID_RE = re.compile(r"\s*(\{#([^}\s]+)[^}]*\})\s*$")  # explicit id: "## Title {#my-id}"
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
NUMBER_RE = re.compile(r"^(?:\d+(?:\.\d+)+\.?|\d+\.|[A-Z](?:\.\d+)+\.?)\s+")
APPENDIX_RE = re.compile(r"^(?i:appendix)\b(?:\s+[A-Z]\b)?[\s.:\-]*")
SETEXT_RE = re.compile(r"^ {0,3}(=+|-+)\s*$")
SRC_RE = re.compile(r"\bSRC-\d{6}\b")
INLINE_CODE_RE = re.compile(r"(`+)(?:(?!\1).)+?\1")
LINK_DEST = r"((?:\\.|[^)\s\\])+)"  # link destination; allows escaped characters such as \( \)
LINK_RE = re.compile(r"!?\[[^\]]*\]\(" + LINK_DEST + r"(?:\s+\"[^\"]*\")?\)")
ANCHOR_LINK_RE = re.compile(r"(\]\(#)" + LINK_DEST + r"(\))")
REF_ANCHOR_RE = re.compile(r"^(\s*\[[^\]]+\]:\s*#)(\S+)")
ACRONYM_RE = re.compile(r"(?<![\w-])([A-Z][A-Z0-9&]*(?:-[A-Z0-9]+)*)s?(?![\w-])")
NOTE_RE = re.compile(r"^\s*(?:>\s*)?(?:\[!NOTE\]|\*{0,2}note:?\*{0,2}:?\s)", re.IGNORECASE)
EM_DASH = "—"
LABELS = ("CONFIRMED", "INTERNAL", "INFERENCE", "UNKNOWN")
KB_DIR = "palo-alto-knowledge-base"

FILLER_PHRASES = (
    "it is important to note", "it's important to note", "it is worth noting", "it should be noted",
    "in this section, we will", "in this section we will", "the following section provides",
    "let's dive", "dive into", "delve", "let's take a look", "as you can see", "in today's",
    "rapidly evolving", "game changer", "game-changer", "seamless", "seamlessly", "robust",
    "leverage", "leveraging", "holistic", "cutting-edge", "unlock", "comprehensive", "streamlined",
    "in order to", "when it comes to", "plays a crucial role", "plays a vital role", "a testament to",
    "rest assured", "needless to say", "at the end of the day", "empower", "elevate", "embark",
)
FILLER_RE = re.compile(r"(?<![\w-])(" + "|".join(re.escape(p) for p in FILLER_PHRASES) + r")(?![\w-])",
                       re.IGNORECASE)
COMMON_ACRONYMS = frozenset("""
    API APIS CLI URL URLS IP IPS DNS TCP UDP HTTP HTTPS TLS SSL SSH JSON YAML XML CSV PDF ID IDS UI GUI OS
    CPU RAM USB UTC FAQ OK TBD TBC AND OR NOT ALL NO YES MUST SHOULD MAY NEW SRC AM PM US UK EU AWS GCP
    HTML README PDF
    CONFIRMED INTERNAL INFERENCE UNKNOWN NOTE TIP IMPORTANT WARNING CAUTION SD-WAN PAN-OS
""".split())


@dataclass(frozen=True)
class Heading:
    index: int        # 0-based line index
    level: int
    text: str         # heading text as written, without the leading #s
    title: str        # text without section number / appendix prefix
    appendix: bool
    attr: str = ""    # explicit id attribute such as "{#intro}", kept as written
    anchor_id: str = ""


@dataclass(frozen=True)
class Finding:
    severity: str     # ERROR, WARN or INFO
    code: str
    line: int         # 1-based; 0 = whole document
    message: str


@dataclass(frozen=True)
class Table:
    header_line: int
    header: tuple
    rows: tuple       # ((line_index, cells), ...)


# ---- parsing --------------------------------------------------------------------------

def split_title(text: str, level: int) -> tuple[str, bool]:
    if level == 2:
        match = APPENDIX_RE.match(text)
        if match:
            return text[match.end():].strip(), True
    match = NUMBER_RE.match(text)
    return (text[match.end():].strip(), False) if match else (text, False)


def scan(lines: list[str]) -> tuple[list[Heading], list[bool], int | None]:
    """Return headings, a per-line 'inside fenced code' mask, and the index of an unclosed fence."""
    headings, mask, fence = [], [], None
    for i, line in enumerate(lines):
        match = FENCE_RE.match(line)
        if fence:
            mask.append(True)
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= fence[1] \
                    and not match.group(2).strip():
                fence = None
            continue
        if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
            fence = (match.group(1)[0], len(match.group(1)), i)
            mask.append(True)
            continue
        mask.append(False)
        heading = HEADING_RE.match(line)
        if heading:
            text = CLOSING_HASHES_RE.sub("", heading.group(2) or "").strip()
            explicit = HEADING_ID_RE.search(text)
            attr, anchor_id = (explicit.group(1), explicit.group(2)) if explicit else ("", "")
            text = text[:explicit.start()].strip() if explicit else text
            level = len(heading.group(1))
            headings.append(Heading(i, level, text, *split_title(text, level), attr, anchor_id))
    return headings, mask, (fence[2] if fence else None)


def split_row(line: str) -> list[str]:
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") and not body.endswith("\\|") else body
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", body)]


def is_separator(line: str) -> bool:
    return "|" in line and "-" in line and all(re.fullmatch(r":?-+:?", c) for c in split_row(line))


def parse_tables(lines: list[str], mask: list[bool]) -> list[Table]:
    tables, i = [], 0
    while i < len(lines) - 1:
        if not mask[i] and "|" in lines[i] and not mask[i + 1] and is_separator(lines[i + 1]):
            header, rows, j = tuple(split_row(lines[i])), [], i + 2
            while j < len(lines) and not mask[j] and lines[j].strip() and "|" in lines[j]:
                rows.append((j, tuple(split_row(lines[j]))))
                j += 1
            tables.append(Table(i, header, tuple(rows)))
            i = j
        else:
            i += 1
    return tables


def prose(line: str) -> str:
    """Line text with inline code, link targets and HTML tags removed."""
    text = INLINE_CODE_RE.sub(" ", line)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return text


def norm(title: str) -> str:
    text = split_title(title.strip(), 2)[0]
    text = split_title(text, 3)[0]
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text)).strip().lower()


def read_doc(path: Path) -> tuple[str, bool, bool]:
    data = path.read_bytes()
    bom = data.startswith(b"\xef\xbb\xbf")
    text = data.decode("utf-8-sig")
    return text.replace("\r\n", "\n"), "\r\n" in text, bom


def write_doc(path: Path, text: str, crlf: bool, bom: bool) -> None:
    out = text.replace("\n", "\r\n") if crlf else text
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8"))


# ---- numbering and anchors ---------------------------------------------------------------

def slugger():
    """GitHub-style slugs with -1, -2 suffixes for repeats (same rule as the amir_md viewer)."""
    used: dict[str, int] = {}

    def slug(text: str) -> str:
        base = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text.lower().strip())
        base = re.sub(r"<[^>]*>", "", base)
        base = re.sub(r"[^\w\- ]", "", base).replace(" ", "-")
        count = used.get(base)
        used[base] = 0 if count is None else count + 1
        return base if count is None else f"{base}-{count + 1}"
    return slug


def expected_texts(headings: list[Heading]) -> dict[int, str]:
    counters, letter, in_appendix, out = [0] * 7, 0, False, {}
    for h in headings:
        if h.level == 1:
            out[h.index] = h.text
            continue
        for deeper in range(h.level + 1, 7):
            counters[deeper] = 0
        if h.level == 2 and h.appendix:
            letter, in_appendix = letter + 1, True
            prefix = f"Appendix {chr(64 + letter)}."
        elif h.level == 2:
            counters[2], in_appendix = counters[2] + 1, False
            prefix = f"{counters[2]}."
        else:
            counters[h.level] += 1
            head = chr(64 + letter) if in_appendix else str(counters[2])
            prefix = ".".join([head] + [str(counters[lv]) for lv in range(3, h.level + 1)])
        out[h.index] = f"{prefix} {h.title}".strip()
    return out


def renumber(text: str) -> tuple[str, dict[str, str]]:
    lines = text.split("\n")
    headings, mask, _ = scan(lines)
    expected = expected_texts(headings)
    old, new = slugger(), slugger()
    link_map = {}
    for h in headings:
        before, after = old(h.text), new(expected[h.index])
        if before != after and not h.anchor_id:
            link_map[before] = after
        if expected[h.index] != h.text:
            lines[h.index] = f"{'#' * h.level} {expected[h.index]} {h.attr}".rstrip()
    if link_map:
        swap = lambda m: m.group(1) + link_map.get(m.group(2), m.group(2)) + (m.group(3) if m.lastindex == 3 else "")
        lines = [line if mask[i] else REF_ANCHOR_RE.sub(swap, ANCHOR_LINK_RE.sub(swap, line))
                 for i, line in enumerate(lines)]
    return "\n".join(lines), link_map


# ---- structure checks ------------------------------------------------------------------------

def check_headings(headings: list[Heading]) -> list[Finding]:
    found = []
    titles = [h for h in headings if h.level == 1]
    if len(titles) != 1:
        found.append(Finding("ERROR", "E001", titles[1].index + 1 if len(titles) > 1 else 0,
                             f"document needs exactly one '# Title' heading (found {len(titles)})"))
    previous, seen = 1, {}
    for h in headings:
        if h.level > previous + 1:
            found.append(Finding("ERROR", "E002", h.index + 1, f"heading jumps from level {previous} to {h.level}"))
        previous = h.level
        key = (tuple(norm(p.title) for p in _ancestors(headings, h)), norm(h.title))
        if key in seen:
            found.append(Finding("WARN", "W108", h.index + 1, f"duplicate heading '{h.title}' under the same parent"))
        seen[key] = True
    return found


def check_numbering(headings: list[Heading]) -> list[Finding]:
    expected = expected_texts(headings)
    return [Finding("ERROR", "E003", h.index + 1,
                    f"numbering: expected '{'#' * h.level} {expected[h.index]}' (run: mddoc.py number FILE)")
            for h in headings if expected[h.index] != h.text]


def check_tables(tables: list[Table]) -> list[Finding]:
    return [Finding("ERROR", "E005", line + 1, f"table row has {len(cells)} cells, header has {len(t.header)}")
            for t in tables for line, cells in t.rows if len(cells) != len(t.header)]


def check_links(lines, mask, headings, doc_dir: Path) -> list[Finding]:
    slug = slugger()
    anchors = {slug(h.text) for h in headings} | {h.anchor_id for h in headings if h.anchor_id}
    found = []
    for i, line in enumerate(lines):
        if mask[i]:
            continue
        for raw in LINK_RE.findall(INLINE_CODE_RE.sub(" ", line)):
            target = re.sub(r"\\(.)", r"\1", raw)
            if target.startswith("#"):
                if target[1:] not in anchors:
                    found.append(Finding("ERROR", "E006", i + 1, f"broken internal link '{target}'"))
            elif not re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
                rel = unquote(target.split("#")[0].split("?")[0])
                if rel and not (doc_dir / rel).exists():
                    found.append(Finding("ERROR", "E007", i + 1, f"link target not found: '{rel}'"))
    return found


def check_style(lines, mask) -> list[Finding]:
    found, notes, words = [], 0, 0
    for i, line in enumerate(lines):
        if mask[i]:
            continue
        text = prose(line)
        words += len(text.split())
        notes += bool(NOTE_RE.match(line))
        if EM_DASH in text:
            found.append(Finding("WARN", "W101", i + 1, "em dash in prose; rewrite the sentence"))
        for phrase in sorted({m.group(1).lower() for m in FILLER_RE.finditer(text)}):
            found.append(Finding("WARN", "W102", i + 1, f"filler or AI-style phrase: '{phrase}'"))
    if notes > max(3, words // 800):
        found.append(Finding("WARN", "W106", 0, f"{notes} 'Note' blocks; keep them for things a reader must not miss"))
    for i in range(1, len(lines)):
        prev = lines[i - 1].strip()
        if not mask[i] and SETEXT_RE.match(lines[i]) and prev and not prev.startswith(("|", "-", "*", "#", ">")):
            found.append(Finding("WARN", "W109", i + 1, "setext heading (=== or ---); use '#' headings"))
    return found


def _ancestors(headings: list[Heading], target: Heading) -> list[Heading]:
    chain, level = [], target.level
    for h in reversed(headings[:headings.index(target)]):
        if h.level < level and h.level >= 2:
            chain.insert(0, h)
            level = h.level
    return chain


def section_words(lines, mask, headings, tables) -> dict[int, tuple[int, bool]]:
    """Map heading index -> (direct prose words, has any direct content)."""
    separators = {t.header_line + 1 for t in tables}
    stats = {}
    for pos, h in enumerate(headings):
        end = headings[pos + 1].index if pos + 1 < len(headings) else len(lines)
        body = range(h.index + 1, end)
        words = sum(len(prose(lines[i]).replace("|", " ").split())
                    for i in body if not mask[i] and i not in separators)
        stats[h.index] = (words, any(lines[i].strip() for i in body))
    return stats


def check_sections(headings, stats, max_words: int) -> list[Finding]:
    found = []
    for pos, h in enumerate(headings):
        if h.level < 2:
            continue
        words, has_content = stats[h.index]
        has_children = pos + 1 < len(headings) and headings[pos + 1].level > h.level
        if not has_content and not has_children:
            found.append(Finding("WARN", "W103", h.index + 1, f"empty section '{h.text}'"))
        if words > max_words:
            found.append(Finding("WARN", "W104", h.index + 1,
                                 f"section '{h.text}' has {words} words before its next heading; consider splitting"))
    return found


def _acronym_tokens(text: str):
    for match in ACRONYM_RE.finditer(text):
        token = re.sub(r"(?:-\d+)+$", "", match.group(1))
        if sum(c.isupper() for c in token) >= 2:
            yield token


def _glossary_terms(headings: list[Heading], tables: list[Table]) -> set[str]:
    """First-column terms of tables that sit under a Glossary, Acronyms or Terminology heading."""
    terms = set()
    for table in tables:
        above = [h for h in headings if h.index < table.header_line]
        if above and re.search(r"glossary|acronym|abbreviation|terminology|terms", above[-1].title, re.IGNORECASE):
            terms |= {re.sub(r"[*`]", "", cells[0]).strip() for _, cells in table.rows if cells}
    return terms


def check_acronyms(lines, mask, headings, tables, allow=()) -> list[Finding]:
    heading_lines = {h.index for h in headings}
    glossary = _glossary_terms(headings, tables)
    first_use, defined_at = {}, {}
    for i, line in enumerate(lines):
        if mask[i] or i in heading_lines:
            continue
        text = prose(line)
        for token in _acronym_tokens(text):
            first_use.setdefault(token, i)
            if re.search(rf"\(\s*{re.escape(token)}s?\b[^)]*\)|(?<![\w-]){re.escape(token)}s?\s*\(", text):
                defined_at.setdefault(token, i)
    skip = COMMON_ACRONYMS | {a.strip().upper() for a in allow} | glossary
    found = []
    for token, line in sorted(first_use.items(), key=lambda kv: kv[1]):
        if token in skip:
            continue
        if token not in defined_at:
            found.append(Finding("WARN", "W105", line + 1, f"acronym {token} is never defined; write the full term first"))
        elif defined_at[token] > line:
            found.append(Finding("WARN", "W105", line + 1,
                                 f"acronym {token} is used before it is defined (line {defined_at[token] + 1})"))
    return found


# ---- evidence checks --------------------------------------------------------------------------

def load_ranks(registry_path: Path | None) -> dict[str, object] | None:
    if not registry_path:
        return None
    data = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    return {s.get("source_id"): s.get("authority_rank") for s in data.get("sources", [])}


def kb_root_for(registry_path: Path) -> Path:
    parent = Path(registry_path).resolve().parent
    return parent.parent if parent.name == KB_DIR else parent


def parse_register(text: str) -> tuple[set[str], list[tuple[int, dict]]]:
    lines = text.replace("\r\n", "\n").split("\n")
    headings, mask, _ = scan(lines)
    non_technical = set()
    for pos, h in enumerate(headings):
        if norm(h.title).startswith("non-technical"):
            end = headings[pos + 1].index if pos + 1 < len(headings) else len(lines)
            non_technical |= {norm(re.sub(r"^\s*[-*+]\s+", "", lines[i]).split(">")[-1])
                              for i in range(h.index + 1, end) if re.match(r"^\s*[-*+]\s+\S", lines[i])}
    rows = []
    for table in parse_tables(lines, mask):
        header = [c.lower() for c in table.header]
        if "section" in header and "label" in header:
            rows += [(line + 1, dict(zip(header, cells))) for line, cells in table.rows]
    return non_technical, rows


def resolve_section(section: str, headings: list[Heading]) -> list[Heading]:
    parts = [norm(p) for p in section.split(">") if p.strip()]
    if not parts:
        return []
    matches = []
    for h in headings:
        if h.level < 2 or norm(h.title) != parts[-1]:
            continue
        chain = iter(norm(a.title) for a in _ancestors(headings, h))
        if all(any(part == name for name in chain) for part in parts[:-1]):
            matches.append(h)
    return matches


def _check_row(row: dict, line: int, ranks, kb_root, headings) -> tuple[list[Finding], list[Heading]]:
    found, where = [], f"evidence line {line}"
    label = row.get("label", "").strip().upper()
    sources = row.get("sources", "")
    src_ids = SRC_RE.findall(sources)
    paths = [p for p in re.findall(r"`([^`]+)`", sources) if re.search(r"[/\\]|\.\w{1,5}$", p)]
    has_source = bool(sources.strip())  # SRC IDs, paths, or "user: <what the user supplied>"
    matched = resolve_section(row.get("section", ""), headings)
    if not matched:
        found.append(Finding("ERROR", "E009", line, f"{where}: section '{row.get('section')}' not found in document"))
    elif len(matched) > 1:
        found.append(Finding("WARN", "W112", line, f"{where}: section '{row.get('section')}' is ambiguous; use 'Parent > Child'"))
    if label not in LABELS:
        found.append(Finding("ERROR", "E010", line, f"{where}: label '{label}' must be one of {', '.join(LABELS)}"))
    if label in ("CONFIRMED", "INTERNAL") and not has_source:
        found.append(Finding("ERROR", "E011", line, f"{where}: {label} claim needs at least one source"))
    if label == "INFERENCE" and not has_source:
        found.append(Finding("WARN", "W111", line, f"{where}: INFERENCE should name the evidence it is based on"))
    if label == "UNKNOWN":
        found.append(Finding("INFO", "I201", line,
                             f"open item (must be visible to the reader): {row.get('claim', '').strip()}"))
    if ranks is not None:
        found += [Finding("ERROR", "E008", line, f"{where}: {s} not in source registry") for s in src_ids if s not in ranks]
        official = [s for s in src_ids if isinstance(ranks.get(s), int) and 1 <= ranks[s] <= 4]
        if label == "CONFIRMED" and not official:
            found.append(Finding("WARN", "W110", line,
                                 f"{where}: CONFIRMED but no official (rank 1-4) source; use INTERNAL or add one"))
    if kb_root is not None:
        for rel in paths:
            if not any((base / rel).exists() for base in (kb_root, kb_root / KB_DIR)):
                found.append(Finding("ERROR", "E012", line, f"{where}: source path not found: {rel}"))
    return found, matched


def check_evidence(register_text, headings, stats, ranks, kb_root) -> list[Finding]:
    non_technical, rows = parse_register(register_text)
    found, covered = [], set()
    for line, row in rows:
        row_findings, matched = _check_row(row, line, ranks, kb_root, headings)
        found += row_findings
        covered |= {h.index for h in matched}
    for h in headings:
        if h.level >= 2 and stats[h.index][0] > 0 and h.index not in covered and norm(h.title) not in non_technical:
            found.append(Finding("WARN", "W107", h.index + 1, f"section '{h.text}' has prose but no evidence row"))
    return found


def check_body_sources(lines, ranks) -> list[Finding]:
    return [Finding("ERROR", "E008", i + 1, f"{s} not in source registry")
            for i, line in enumerate(lines) for s in SRC_RE.findall(line) if s not in ranks]


# ---- public entry points ----------------------------------------------------------------------

def check(text: str, path: Path, evidence_text: str | None = None, registry_path: Path | None = None,
          max_section_words: int = 600, allow_acronyms=()) -> list[Finding]:
    lines = text.replace("\r\n", "\n").split("\n")
    headings, mask, open_fence = scan(lines)
    tables = parse_tables(lines, mask)
    stats = section_words(lines, mask, headings, tables)
    found = check_headings(headings) + check_numbering(headings) + check_tables(tables)
    if open_fence is not None:
        found.append(Finding("ERROR", "E004", open_fence + 1, "code fence is never closed"))
    found += check_links(lines, mask, headings, Path(path).parent)
    found += check_style(lines, mask) + check_sections(headings, stats, max_section_words)
    found += check_acronyms(lines, mask, headings, tables, allow_acronyms)
    ranks = load_ranks(registry_path)
    if ranks is not None:
        found += check_body_sources(lines, ranks)
    if evidence_text is not None:
        kb_root = kb_root_for(registry_path) if registry_path else None
        found += check_evidence(evidence_text, headings, stats, ranks, kb_root)
    return sorted(found, key=lambda f: (f.line, f.code))


def outline(text: str) -> str:
    lines = text.replace("\r\n", "\n").split("\n")
    headings, mask, _ = scan(lines)
    stats = section_words(lines, mask, headings, parse_tables(lines, mask))
    rows = []
    for h in headings:
        indent = "  " * max(0, h.level - 2)
        rows.append(f"{indent}{h.text}  (line {h.index + 1}, {stats[h.index][0]} words)")
    return "\n".join(rows)


def _cmd_number(path: Path, check_only: bool) -> int:
    text, crlf, bom = read_doc(path)
    new_text, link_map = renumber(text)
    if new_text == text:
        print(f"numbering OK: {path}")
        return 0
    changed = sum(a != b for a, b in zip(text.split("\n"), new_text.split("\n")))
    if check_only:
        print(f"numbering would change {changed} line(s) in {path}; run without --check to fix")
        return 1
    write_doc(path, new_text, crlf, bom)
    print(f"renumbered {path}: {changed} line(s) changed, {len(link_map)} anchor(s) remapped")
    return 0


def _cmd_check(args) -> int:
    path = Path(args.file)
    text = read_doc(path)[0]
    evidence = Path(args.evidence) if args.evidence else path.with_name(f"{path.stem}.evidence.md")
    evidence_text = read_doc(evidence)[0] if evidence.is_file() else None
    allow = [a for a in (args.allow_acronyms or "").split(",") if a.strip()]
    findings = check(text, path, evidence_text, Path(args.registry) if args.registry else None,
                     args.max_section_words, allow)
    print(f"mddoc check: {path}" + (f" (evidence: {evidence.name})" if evidence_text is not None else " (no evidence register)"))
    for f in findings:
        print(f"{f.severity:<5} {f.code} line {f.line}: {f.message}")
    errors = sum(f.severity == "ERROR" for f in findings)
    warns = sum(f.severity == "WARN" for f in findings)
    print(f"Summary: {errors} error(s), {warns} warning(s). Result: {'FAIL' if errors else 'PASS'}")
    return 1 if errors else 0


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    number = sub.add_parser("number")
    number.add_argument("file")
    number.add_argument("--check", action="store_true")
    chk = sub.add_parser("check")
    chk.add_argument("file")
    chk.add_argument("--evidence")
    chk.add_argument("--registry")
    chk.add_argument("--max-section-words", type=int, default=600)
    chk.add_argument("--allow-acronyms", default="")
    sub.add_parser("outline").add_argument("file")
    args = parser.parse_args(argv)
    try:
        if args.command == "number":
            return _cmd_number(Path(args.file), args.check)
        if args.command == "check":
            return _cmd_check(args)
        print(outline(read_doc(Path(args.file))[0]))
        return 0
    except (OSError, ValueError) as exc:
        print(f"mddoc: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
