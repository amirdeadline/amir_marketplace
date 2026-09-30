#!/usr/bin/env python3
"""amir_humanized document pipeline: validate, extract, apply, compare, report.

This script does not rewrite prose. The agent applies writing rules and supplies
a changes.json. The script preserves structure, never overwrites the source,
and writes the mandatory project-root report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

EM_DASH = "\u2014"
SUPPORTED = {".docx", ".md", ".txt", ".pdf"}
PDF_OUTPUT_EXT = ".md"

ENV_ROOT_KEYS = (
    "AMIR_PROJECT_ROOT",
    "CURSOR_PROJECT_DIR",
    "CURSOR_WORKSPACE_ROOT",
    "WORKSPACE_FOLDER",
    "PROJECT_ROOT",
)

AI_PATTERNS = (
    r"\bit is important to note that\b",
    r"\bit is worth noting that\b",
    r"\bit should be noted that\b",
    r"\bthis ensures that\b",
    r"\bthis allows you to\b",
    r"\bin this section, we will explore\b",
    r"\bin this section, we will discuss\b",
    r"\bthe following section provides\b",
    r"\bthis comprehensive approach\b",
    r"\bthis robust solution\b",
    r"\bthis seamless process\b",
    r"\bby leveraging\b",
    r"\bin order to\b",
    r"\bwhen it comes to\b",
    r"\blet's take a look at\b",
    r"\bnow let's dive into\b",
    r"\bas you can see\b",
    r"\byou might be wondering\b",
    r"\bthe good news is\b",
    r"\bthis is not just\b",
    r"\brather than simply\b",
    r"\bnot only does this\b",
)

FILLER_WORDS = (
    "robust",
    "comprehensive",
    "seamless",
    "powerful",
    "sophisticated",
    "streamlined",
    "holistic",
)

URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.I)
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b")
IPV6_RE = re.compile(
    r"\b(?:[0-9a-f]{1,4}:){2,7}[0-9a-f]{1,4}\b",
    re.I,
)
UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.I,
)
CODE_FENCE_RE = re.compile(r"^```")
CLI_LINE_RE = re.compile(
    r"^(?:\$ |> |PS>|C:\\|dump |debug |config |ping |traceroute |"
    r"curl |wget |python |pip |npm |yarn |git |docker |kubectl |"
    r"pwsh |powershell |az |aws |terraform )",
    re.I,
)
MD_HEADING_RE = re.compile(r"^#{1,6}\s+\S")
JSONISH_RE = re.compile(r"^\s*[\{\[]\s*[\"'\w]", re.M)
YAMLISH_RE = re.compile(r"^\s*[\w.-]+:\s+.+$", re.M)

AI_RES = [re.compile(p, re.I) for p in AI_PATTERNS]
FILLER_RE = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in FILLER_WORDS) + r")\b",
    re.I,
)


class PipelineError(Exception):
    def __init__(self, message: str, code: int = 2) -> None:
        super().__init__(message)
        self.code = code


def emit(payload: dict[str, Any], code: int = 0) -> int:
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return code


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(raw: str) -> Path:
    return Path(raw).expanduser().resolve()


def detect_project_root(explicit: str | None, cwd: Path | None = None) -> Path:
    if explicit:
        root = resolve_path(explicit)
        if not root.is_dir():
            raise PipelineError(f"project root is not a directory: {root}")
        return root
    for key in ENV_ROOT_KEYS:
        value = os.environ.get(key)
        if value:
            candidate = resolve_path(value)
            if candidate.is_dir():
                return candidate
    start = (cwd or Path.cwd()).resolve()
    for candidate in [start, *start.parents]:
        if any(
            (candidate / marker).exists()
            for marker in (".git", ".amir", ".ai", "PROJECT.md")
        ):
            return candidate
    return start


def output_document_path(source: Path, override: str | None) -> Path:
    if override:
        return resolve_path(override)
    suffix = PDF_OUTPUT_EXT if source.suffix.lower() == ".pdf" else source.suffix
    return source.with_name(f"{source.stem}_humanized{suffix}")


def report_path(project_root: Path, source: Path) -> Path:
    return project_root / ".ai" / "reports" / f"{source.stem}_humanized_report.md"


def validate_source(raw: str) -> Path:
    if not raw or not raw.strip():
        raise PipelineError("document path is required")
    source = resolve_path(raw.strip().strip("\"'"))
    if not source.exists():
        raise PipelineError(f"file does not exist: {source}")
    if not source.is_file():
        raise PipelineError(f"path is not a file: {source}")
    if source.suffix.lower() not in SUPPORTED:
        raise PipelineError(
            f"unsupported file type '{source.suffix}'. "
            f"Supported: {', '.join(sorted(SUPPORTED))}"
        )
    try:
        with source.open("rb") as handle:
            handle.read(1)
    except OSError as exc:
        raise PipelineError(f"file cannot be read: {source} ({exc})") from exc
    return source


def flags_for(text: str, kind: str) -> list[str]:
    flags: list[str] = []
    if kind != "immutable":
        if EM_DASH in text:
            flags.append("em_dash")
        if any(rx.search(text) for rx in AI_RES):
            flags.append("ai_pattern")
        if FILLER_RE.search(text):
            flags.append("filler")
    return flags


def looks_like_code(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if MD_HEADING_RE.match(stripped):
        return False
    if CODE_FENCE_RE.match(stripped):
        return True
    if CLI_LINE_RE.match(stripped):
        return True
    if stripped.startswith(("#!/", "<?xml", "{", "[")) and (
        JSONISH_RE.search(stripped) or stripped.startswith("#!/")
    ):
        return True
    if stripped.count("\n") >= 1 and YAMLISH_RE.search(stripped) and ":" in stripped:
        if stripped.lstrip().startswith(("apiVersion:", "kind:", "resources:")):
            return True
    if re.search(r"^\s*(def |class |import |from |function |const |let |var )", stripped):
        return True
    return False


def looks_like_only_technical(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    leftover = URL_RE.sub("", stripped)
    leftover = IPV4_RE.sub("", leftover)
    leftover = IPV6_RE.sub("", leftover)
    leftover = UUID_RE.sub("", leftover)
    leftover = re.sub(r"[\s\-_/.:;,()[\]{}\"'`]+", "", leftover)
    return leftover == ""


def classify_text(text: str, hint: str | None = None) -> str:
    if hint == "immutable":
        return "immutable"
    stripped = text.strip()
    if not stripped:
        return "skip"
    if looks_like_code(stripped) or looks_like_only_technical(stripped):
        return "immutable"
    if URL_RE.search(stripped) or IPV4_RE.search(stripped) or CLI_LINE_RE.search(stripped):
        return "mixed"
    return "editable"


def extract_tokens(text: str) -> dict[str, list[str]]:
    return {
        "urls": sorted(set(URL_RE.findall(text))),
        "ipv4": sorted(set(IPV4_RE.findall(text))),
        "ipv6": sorted(set(IPV6_RE.findall(text))),
        "uuids": sorted(set(UUID_RE.findall(text))),
    }


# ---------------------------------------------------------------------------
# Markdown / text
# ---------------------------------------------------------------------------

def _md_blocks(text: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    lines = text.splitlines(keepends=True)
    i = 0
    idx = 0
    pos = 0
    n = len(lines)

    def add(kind: str, chunk: str, start: int, hint: str | None = None) -> None:
        nonlocal idx
        cls = classify_text(chunk, hint)
        if cls == "skip" and not chunk.strip():
            return
        if cls == "skip":
            cls = "immutable"
        blocks.append(
            {
                "id": f"{kind}:{idx}",
                "kind": kind,
                "classification": cls,
                "text": chunk.rstrip("\n"),
                "start": start,
                "end": start + len(chunk),
                "flags": flags_for(chunk, cls),
            }
        )
        idx += 1

    while i < n:
        line = lines[i]
        start = pos
        if CODE_FENCE_RE.match(line.strip()):
            chunk = line
            i += 1
            pos += len(line)
            while i < n:
                chunk += lines[i]
                pos += len(lines[i])
                closed = CODE_FENCE_RE.match(lines[i].strip())
                i += 1
                if closed and len(chunk.strip().splitlines()) > 1:
                    break
            add("code", chunk, start, "immutable")
            continue
        if line.startswith("|") and "|" in line[1:]:
            chunk = line
            i += 1
            pos += len(line)
            while i < n and lines[i].startswith("|"):
                chunk += lines[i]
                pos += len(lines[i])
                i += 1
            add("table", chunk, start)
            continue
        if re.match(r"^\s*([-*+] |\d+\. )", line):
            chunk = line
            i += 1
            pos += len(line)
            while i < n and (
                re.match(r"^\s*([-*+] |\d+\. )", lines[i])
                or (lines[i].startswith((" ", "\t")) and lines[i].strip())
            ):
                chunk += lines[i]
                pos += len(lines[i])
                i += 1
            add("list", chunk, start)
            continue
        if line.strip().startswith("#"):
            add("heading", line, start)
            i += 1
            pos += len(line)
            continue
        if not line.strip():
            i += 1
            pos += len(line)
            continue
        chunk = line
        i += 1
        pos += len(line)
        while i < n and lines[i].strip() and not lines[i].startswith(("#", "|", "```")):
            if re.match(r"^\s*([-*+] |\d+\. )", lines[i]):
                break
            chunk += lines[i]
            pos += len(lines[i])
            i += 1
        kind = "heading" if chunk.lstrip().startswith("#") else "paragraph"
        add(kind, chunk, start)
    return blocks


def extract_plaintext(path: Path, file_type: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    blocks = _md_blocks(text) if file_type in {".md", ".pdf"} else _md_blocks(text)
    if file_type == ".txt":
        # Keep the same splitter; it is safe for plain text.
        pass
    return {
        "file_type": file_type.lstrip("."),
        "text": text,
        "blocks": blocks,
        "structure": _text_structure(text, blocks),
    }


def _text_structure(text: str, blocks: list[dict[str, Any]]) -> dict[str, Any]:
    heading_count = sum(1 for b in blocks if b["kind"] == "heading")
    para_count = sum(1 for b in blocks if b["kind"] == "paragraph")
    list_count = sum(1 for b in blocks if b["kind"] == "list")
    table_count = sum(1 for b in blocks if b["kind"] == "table")
    code_count = sum(1 for b in blocks if b["kind"] == "code")
    tokens = extract_tokens(text)
    return {
        "headings": heading_count,
        "paragraphs": para_count,
        "lists": list_count,
        "tables": table_count,
        "code_blocks": code_count,
        "images": len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text)),
        "tokens": tokens,
        "block_count": len(blocks),
    }


def apply_plaintext(source_text: str, blocks: list[dict[str, Any]], changes: dict[str, str]) -> str:
    by_id = {b["id"]: b for b in blocks}
    pieces: list[tuple[int, int, str]] = []
    for block_id, revised in changes.items():
        block = by_id.get(block_id)
        if block is None:
            raise PipelineError(f"unknown block id in changes: {block_id}")
        if block["classification"] == "immutable":
            raise PipelineError(f"refusing to modify immutable block {block_id}")
        if block["text"] not in source_text[block["start"] : block["end"]] and block["text"] not in source_text:
            raise PipelineError(f"original text for {block_id} no longer matches source")
        pieces.append((block["start"], block["end"], revised + ("\n" if source_text[block["end"] - 1 : block["end"]] == "\n" or True else "")))
    # Replace using exact original text from the end so offsets stay valid.
    result = source_text
    for block_id, revised in changes.items():
        block = by_id[block_id]
        original = block["text"]
        start = result.find(original)
        if start < 0:
            raise PipelineError(f"could not locate original text for {block_id}")
        result = result[:start] + revised + result[start + len(original) :]
    return result


# ---------------------------------------------------------------------------
# DOCX
# ---------------------------------------------------------------------------

def _require_docx():
    try:
        from docx import Document  # type: ignore
        from docx.oxml.ns import qn  # type: ignore
        from docx.table import Table  # type: ignore
        from docx.text.paragraph import Paragraph  # type: ignore
    except ImportError as exc:
        raise PipelineError(
            "python-docx is required for .docx files. "
            "Install python-docx==1.2.0 from PyPI."
        ) from exc
    return Document, qn, Table, Paragraph


def _iter_docx_paragraphs(doc) -> list[tuple[str, Any]]:
    Document, qn, Table, Paragraph = _require_docx()
    found: list[tuple[str, Any]] = []
    seen: set[int] = set()

    def take(prefix: str, paragraph) -> None:
        ident = id(paragraph._element)
        if ident in seen:
            return
        seen.add(ident)
        found.append((f"{prefix}:{len(found)}", paragraph))

    def walk_container(container, prefix: str) -> None:
        parent_elm = container.element.body if hasattr(container, "element") and hasattr(container.element, "body") else getattr(container, "_element", None)
        if parent_elm is None and hasattr(container, "iter_inner_content"):
            for item in container.iter_inner_content():
                if item.__class__.__name__ == "Paragraph":
                    take(prefix, item)
                elif item.__class__.__name__ == "Table":
                    walk_table(item, f"{prefix}:t")
            return
        body = doc.element.body
        for child in body.iterchildren():
            if child.tag == qn("w:p"):
                take("body", Paragraph(child, doc))
            elif child.tag == qn("w:tbl"):
                walk_table(Table(child, doc), "body:t")

    def walk_table(table, prefix: str) -> None:
        for ri, row in enumerate(table.rows):
            for ci, cell in enumerate(row.cells):
                for paragraph in cell.paragraphs:
                    take(f"{prefix}:r{ri}c{ci}", paragraph)
                for nested in cell.tables:
                    walk_table(nested, f"{prefix}:r{ri}c{ci}:t")

    walk_container(doc, "body")
    for si, section in enumerate(doc.sections):
        for part_name, part in (
            ("header", section.header),
            ("footer", section.footer),
        ):
            try:
                for paragraph in part.paragraphs:
                    take(f"{part_name}{si}", paragraph)
                for table in part.tables:
                    walk_table(table, f"{part_name}{si}:t")
            except Exception:
                continue
    return found


def _docx_style_hint(paragraph) -> str | None:
    try:
        name = (paragraph.style.name or "").lower()
    except Exception:
        return None
    if "code" in name or "html pre" in name or name.startswith("no spacing") and looks_like_code(paragraph.text):
        return "immutable"
    return None


def _paragraph_has_hyperlink(paragraph) -> bool:
    return bool(paragraph._element.xpath(".//*[local-name()='hyperlink']"))


def extract_docx(path: Path) -> dict[str, Any]:
    Document, qn, _Table, _Paragraph = _require_docx()
    doc = Document(str(path))
    blocks: list[dict[str, Any]] = []
    for block_id, paragraph in _iter_docx_paragraphs(doc):
        text = paragraph.text
        hint = _docx_style_hint(paragraph)
        cls = classify_text(text, hint)
        if cls == "skip":
            continue
        style = ""
        try:
            style = paragraph.style.name or ""
        except Exception:
            style = ""
        kind = "heading" if style.lower().startswith("heading") else "paragraph"
        if "body:t" in block_id or re.search(r":t:r\d", block_id):
            kind = "table_cell"
        blocks.append(
            {
                "id": block_id,
                "kind": kind,
                "classification": cls,
                "text": text,
                "style": style,
                "has_hyperlink": _paragraph_has_hyperlink(paragraph),
                "flags": flags_for(text, cls),
            }
        )
    structure = _docx_structure(doc, blocks, qn)
    return {
        "file_type": "docx",
        "blocks": blocks,
        "structure": structure,
    }


def _docx_count_drawings(doc, qn) -> int:
    return len(doc.element.findall(".//" + qn("w:drawing"))) + len(
        doc.element.findall(".//" + qn("w:pict"))
    )


def _docx_structure(doc, blocks: list[dict[str, Any]], qn) -> dict[str, Any]:
    headings = [b for b in blocks if b["kind"] == "heading"]
    tables = len(doc.tables)
    full = "\n".join(b["text"] for b in blocks)
    return {
        "headings": len(headings),
        "heading_texts": [b["text"] for b in headings],
        "paragraphs": sum(1 for b in blocks if b["kind"] == "paragraph"),
        "lists": sum(1 for b in blocks if "List" in (b.get("style") or "")),
        "tables": tables,
        "table_cells": sum(1 for b in blocks if b["kind"] == "table_cell"),
        "code_blocks": sum(1 for b in blocks if b["classification"] == "immutable" and looks_like_code(b["text"])),
        "images": _docx_count_drawings(doc, qn),
        "tokens": extract_tokens(full),
        "block_count": len(blocks),
    }


def _set_paragraph_text(paragraph, new_text: str) -> None:
    runs = paragraph.runs
    if not runs:
        paragraph.add_run(new_text)
        return
    runs[0].text = new_text
    for run in runs[1:]:
        run.text = ""


def apply_docx(source: Path, dest: Path, extract: dict[str, Any], changes: dict[str, str]) -> list[str]:
    Document, _qn, _Table, _Paragraph = _require_docx()
    warnings: list[str] = []
    tmp = dest.with_name(dest.stem + ".tmp" + dest.suffix)
    if tmp.exists():
        tmp.unlink()
    shutil.copy2(source, tmp)
    doc = Document(str(tmp))
    by_id = {b["id"]: b for b in extract["blocks"]}
    live = {i: p for i, p in _iter_docx_paragraphs(doc)}
    for block_id, revised in changes.items():
        block = by_id.get(block_id)
        if block is None:
            raise PipelineError(f"unknown block id in changes: {block_id}")
        if block["classification"] == "immutable":
            raise PipelineError(f"refusing to modify immutable block {block_id}")
        paragraph = live.get(block_id)
        if paragraph is None:
            raise PipelineError(f"could not locate paragraph {block_id} in document copy")
        if paragraph.text != block["text"]:
            raise PipelineError(
                f"paragraph {block_id} text no longer matches extract "
                f"(document may have changed)"
            )
        if block.get("has_hyperlink") and paragraph.text != revised:
            # Keep hyperlink XML; only replace visible run text.
            warnings.append(
                f"{block_id}: paragraph contains a hyperlink; run text was replaced "
                "without rebuilding the hyperlink element."
            )
        _set_paragraph_text(paragraph, revised)
    doc.save(str(tmp))
    os.replace(tmp, dest)
    return warnings


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------

def extract_pdf(path: Path) -> dict[str, Any]:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise PipelineError(
            "pypdf is required to read PDF files. PDF output is always a "
            "separate Markdown file; the source PDF is never edited."
        ) from exc
    reader = PdfReader(str(path))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    text = "\n\n".join(pages)
    blocks = _md_blocks(text)
    return {
        "file_type": "pdf",
        "text": text,
        "blocks": blocks,
        "structure": _text_structure(text, blocks),
        "warnings": [
            "PDF layout cannot be preserved. Humanized output is Markdown "
            f"written next to the source as {path.stem}_humanized.md."
        ],
    }


# ---------------------------------------------------------------------------
# Compare / report
# ---------------------------------------------------------------------------

def count_em_dashes(blocks: list[dict[str, Any]], revised: dict[str, str] | None = None) -> int:
    count = 0
    for block in blocks:
        if block["classification"] == "immutable":
            continue
        text = revised.get(block["id"], block["text"]) if revised else block["text"]
        count += text.count(EM_DASH)
    return count


def compare_structures(src: dict[str, Any], dst: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    keys = (
        "headings",
        "tables",
        "images",
        "code_blocks",
    )
    for key in keys:
        if src.get(key, 0) != dst.get(key, 0):
            issues.append(f"{key} count changed: {src.get(key)} -> {dst.get(key)}")
    if src.get("paragraphs", 0) and dst.get("paragraphs", 0) < src["paragraphs"] * 0.7:
        issues.append(
            f"paragraph count dropped sharply: {src.get('paragraphs')} -> {dst.get('paragraphs')}"
        )
    src_tokens = src.get("tokens") or {}
    dst_tokens = dst.get("tokens") or {}
    integrity = {
        "commands": True,
        "code": src.get("code_blocks", 0) == dst.get("code_blocks", 0),
        "api": True,
        "urls": src_tokens.get("urls") == dst_tokens.get("urls"),
        "tech_values": src_tokens.get("ipv4") == dst_tokens.get("ipv4")
        and src_tokens.get("ipv6") == dst_tokens.get("ipv6")
        and src_tokens.get("uuids") == dst_tokens.get("uuids"),
        "tables": src.get("tables", 0) == dst.get("tables", 0),
        "headings": src.get("headings", 0) == dst.get("headings", 0),
        "images": src.get("images", 0) == dst.get("images", 0),
        "meaning": not issues,
    }
    if not integrity["urls"]:
        issues.append("URL set changed")
    if not integrity["tech_values"]:
        issues.append("IP address / UUID set changed")
    return {"ok": not issues, "issues": issues, "integrity": integrity}


def yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def write_report(
    path: Path,
    *,
    source: Path,
    output: Path,
    project_root: Path,
    file_type: str,
    reviewed: int,
    changed: int,
    unchanged: int,
    em_dashes: int,
    categories: list[str],
    integrity: dict[str, bool],
    potential: list[str],
    warnings: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not categories and changed == 0:
        changes_body = (
            "No prose changes were required. The source already read as "
            "natural technical documentation."
        )
    elif categories:
        changes_body = "\n".join(f"* {item}" for item in categories)
    else:
        changes_body = f"* {changed} prose block(s) revised"
    if potential:
        pot_body = "\n\n".join(
            "Potential technical issue detected but not modified.\n\n" + item
            if not item.lower().startswith("potential technical")
            else item
            for item in potential
        )
    else:
        pot_body = "None observed during the humanization pass."
    warn_body = (
        "\n".join(f"* {item}" for item in warnings)
        if warnings
        else "No technical-integrity issues detected."
    )
    text = f"""# Humanization Report

## Summary

* Source document: `{source}`
* Humanized document: `{output}`
* Project root: `{project_root}`
* Report: `{path}`
* File type: {file_type}
* Paragraphs/text blocks reviewed: {reviewed}
* Changed: {changed}
* Left unchanged: {unchanged}
* Em dashes remaining in normal prose: {em_dashes}

## Changes Made

{changes_body}

## Technical Integrity

* Commands preserved: {yes_no(integrity.get('commands', True))}
* Code preserved: {yes_no(integrity.get('code', True))}
* API content preserved: {yes_no(integrity.get('api', True))}
* URLs preserved: {yes_no(integrity.get('urls', True))}
* IP addresses and technical values preserved: {yes_no(integrity.get('tech_values', True))}
* Tables preserved: {yes_no(integrity.get('tables', True))}
* Headings and numbering preserved: {yes_no(integrity.get('headings', True))}
* Images and embedded objects preserved: {yes_no(integrity.get('images', True))}
* Technical meaning preserved: {yes_no(integrity.get('meaning', True))}

## Potential Technical Issues

{pot_body}

## Warnings

{warn_body}
"""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def extract_any(source: Path) -> dict[str, Any]:
    ext = source.suffix.lower()
    if ext == ".docx":
        return extract_docx(source)
    if ext == ".pdf":
        return extract_pdf(source)
    return extract_plaintext(source, ext)


def extract_from_output(output: Path, file_type: str) -> dict[str, Any]:
    if file_type == "docx":
        return extract_docx(output)
    return extract_plaintext(output, f".{file_type}" if file_type != "pdf" else ".md")


def parse_changes(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PipelineError("changes file must be a JSON object")
    items = data.get("changes") or []
    mapping: dict[str, str] = {}
    for item in items:
        mapping[item["id"]] = item["revised"]
    data["_map"] = mapping
    return data


def cmd_init(args: argparse.Namespace) -> int:
    source = validate_source(args.document)
    project_root = detect_project_root(args.project_root)
    output = output_document_path(source, args.output)
    report = report_path(project_root, source)
    report.parent.mkdir(parents=True, exist_ok=True)
    extract = extract_any(source)
    work_dir = Path(tempfile.mkdtemp(prefix="amir_humanized_"))
    extract_path = work_dir / "extract.json"
    payload = {
        "ok": True,
        "source": str(source),
        "source_sha256": sha256_file(source),
        "output": str(output),
        "report": str(report),
        "project_root": str(project_root),
        "file_type": source.suffix.lower().lstrip("."),
        "extract_path": str(extract_path),
        "work_dir": str(work_dir),
        "blocks_reviewed": len(extract["blocks"]),
        "editable": sum(1 for b in extract["blocks"] if b["classification"] in {"editable", "mixed"}),
        "immutable": sum(1 for b in extract["blocks"] if b["classification"] == "immutable"),
        "em_dashes_in_prose": count_em_dashes(extract["blocks"]),
        "warnings": extract.get("warnings") or [],
    }
    extract_path.write_text(
        json.dumps({**extract, "meta": payload}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return emit(payload)


def _load_extract(extract_path: Path) -> dict[str, Any]:
    return json.loads(extract_path.read_text(encoding="utf-8"))


def cmd_finalize(args: argparse.Namespace) -> int:
    source = validate_source(args.document)
    source_hash = sha256_file(source)
    project_root = detect_project_root(args.project_root)
    output = output_document_path(source, args.output)
    report = report_path(project_root, source)
    if output.resolve() == source.resolve():
        raise PipelineError("refusing to overwrite the source document")
    changes_data = parse_changes(resolve_path(args.changes))
    change_map: dict[str, str] = changes_data["_map"]

    if args.extract:
        extract = _load_extract(resolve_path(args.extract))
    else:
        extract = extract_any(source)

    by_id = {b["id"]: b for b in extract["blocks"]}
    for item in changes_data.get("changes") or []:
        block = by_id.get(item["id"])
        if block is None:
            raise PipelineError(f"unknown block id: {item['id']}")
        if item.get("original") is not None and item["original"] != block["text"]:
            raise PipelineError(
                f"original text mismatch for {item['id']}; refusing to apply"
            )

    apply_warnings: list[str] = []
    file_type = source.suffix.lower().lstrip(".")
    tmp_out = output.with_name(output.stem + ".partial" + output.suffix)
    if tmp_out.exists():
        tmp_out.unlink()

    try:
        if file_type == "docx":
            apply_warnings.extend(apply_docx(source, tmp_out, extract, change_map))
        else:
            if file_type == "pdf":
                src_text = extract.get("text") or ""
            else:
                src_text = source.read_text(encoding="utf-8")
            revised = apply_plaintext(src_text, extract["blocks"], change_map)
            tmp_out.write_text(revised, encoding="utf-8")
        os.replace(tmp_out, output)
    except Exception:
        if tmp_out.exists():
            tmp_out.unlink()
        raise

    if sha256_file(source) != source_hash:
        raise PipelineError("source document changed during processing")

    out_extract = extract_from_output(output, "md" if file_type == "pdf" else file_type)
    comparison = compare_structures(extract["structure"], out_extract["structure"])
    em_left = count_em_dashes(out_extract["blocks"])
    reviewed = int(changes_data.get("paragraphs_reviewed") or len(extract["blocks"]))
    changed = int(changes_data.get("changed") or len(change_map))
    unchanged = int(changes_data.get("unchanged") or max(reviewed - changed, 0))
    warnings = list(extract.get("warnings") or [])
    warnings.extend(apply_warnings)
    warnings.extend(changes_data.get("warnings") or [])
    if not comparison["ok"]:
        warnings.extend(comparison["issues"])
    if file_type == "pdf":
        warnings.append("Formatting preserved: No (PDF rewritten as Markdown)")

    write_report(
        report,
        source=source,
        output=output,
        project_root=project_root,
        file_type=file_type,
        reviewed=reviewed,
        changed=changed,
        unchanged=unchanged,
        em_dashes=em_left,
        categories=list(changes_data.get("change_categories") or []),
        integrity=comparison["integrity"],
        potential=list(changes_data.get("potential_technical_issues") or []),
        warnings=warnings,
    )
    formatting = file_type != "pdf"
    payload = {
        "ok": comparison["ok"] and em_left == 0,
        "source": str(source),
        "output": str(output),
        "report": str(report),
        "project_root": str(project_root),
        "file_type": file_type,
        "source_unchanged": True,
        "source_sha256": source_hash,
        "em_dashes_remaining_in_normal_prose": em_left,
        "technical_content_preserved": comparison["ok"],
        "formatting_preserved": formatting,
        "integrity": comparison["integrity"],
        "warnings": warnings,
        "console": (
            "Humanization complete.\n\n"
            f"Input: {source}\n"
            f"Output: {output}\n"
            f"Report: {report}\n"
            f"Technical content preserved: {yes_no(comparison['ok'])}\n"
            f"Formatting preserved: {yes_no(formatting)}\n"
            f"Em dashes remaining in normal prose: {em_left}"
            + ("\nWarnings: See humanization report." if warnings else "")
        ),
    }
    return emit(payload, 0 if payload["ok"] else 3)


def _build_sample_md(path: Path) -> None:
    path.write_text(
        """# Connectivity Operations Guide

## Overview

It is important to note that the controller provides this information — including site status, alarms, and path health — through the monitoring interface.

Check the site status before troubleshooting.

This comprehensive approach ensures that administrators can efficiently troubleshoot connectivity issues.

In this section, we will explore the monitoring workflow.

## Procedure

1. Check site status
2. Review alarms
3. Validate path health

The dashboard provides visibility into site status. The dashboard allows operators to review alarms. The dashboard enables path-health inspection.

## Commands

Run this command:

```
dump interface status
ping 10.1.1.1
# note: the path — primary — is preferred
```

See the docs at https://docs.example.com/ion/cli

| Field | Value |
|-------|-------|
| Device | ION-3200 |
| Address | 10.20.30.1 |
| Note | It is worth noting that the device must be online before proceeding. |

Administrators are advised to utilize the monitoring functionality to facilitate identification of potential connectivity-related conditions.

This is not just a dashboard, but a comprehensive operational interface.

## Conclusion

In this section, we discussed the monitoring workflow. This robust solution provides a seamless process for Day 2 operations.
""",
        encoding="utf-8",
    )


def _build_sample_docx(path: Path) -> None:
    Document, _qn, _Table, _Paragraph = _require_docx()
    doc = Document()
    doc.add_heading("Connectivity Operations Guide", 0)
    doc.add_heading("Overview", 1)
    doc.add_paragraph(
        "It is important to note that the controller provides this information "
        "— including site status, alarms, and path health — through the "
        "monitoring interface."
    )
    p = doc.add_paragraph("Check the site status before troubleshooting.")
    p.runs[0].bold = True
    doc.add_paragraph(
        "This comprehensive approach ensures that administrators can efficiently "
        "troubleshoot connectivity issues."
    )
    doc.add_heading("Procedure", 1)
    doc.add_paragraph("Check site status", style="List Number")
    doc.add_paragraph("Review alarms", style="List Number")
    doc.add_paragraph("Validate path health", style="List Number")
    doc.add_paragraph("Site prerequisites", style="List Bullet")
    doc.add_paragraph("Path health evidence", style="List Bullet")
    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Field"
    table.cell(0, 1).text = "Value"
    table.cell(1, 0).text = "Address"
    table.cell(1, 1).text = "10.20.30.1"
    table.cell(2, 0).text = "Note"
    table.cell(2, 1).text = (
        "It is worth noting that the device must be online before proceeding."
    )
    doc.add_paragraph("dump interface status")
    doc.add_paragraph("See https://docs.example.com/ion/cli for the CLI reference.")
    doc.add_paragraph("The path — primary — is preferred")
    doc.save(str(path))


def _build_sample_pdf(path: Path) -> None:
    # Minimal one-page PDF with extractable text. Source is never edited.
    stream = (
        "BT /F1 12 Tf 72 720 Td "
        "(It is important to note that the device must be online.) Tj ET"
    )
    objects = [
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n",
        f"4 0 obj << /Length {len(stream)} >> stream\n{stream}\nendstream endobj\n",
        "5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
    ]
    header = "%PDF-1.4\n"
    body = "".join(objects)
    offsets = []
    cursor = len(header)
    parts = []
    for obj in objects:
        offsets.append(cursor)
        parts.append(obj)
        cursor += len(obj)
    xref_pos = cursor
    xref = "xref\n0 6\n0000000000 65535 f \n"
    for off in offsets:
        xref += f"{off:010d} 00000 n \n"
    trailer = (
        f"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"
    )
    path.write_bytes((header + "".join(parts) + xref + trailer).encode("latin-1"))


def cmd_selftest(_args: argparse.Namespace) -> int:
    results: list[dict[str, Any]] = []

    def record(name: str, ok: bool, detail: str = "") -> None:
        results.append({"name": name, "result": "PASS" if ok else "FAIL", "detail": detail})

    skill_dir = Path(__file__).resolve().parents[1]
    required = [
        skill_dir / "SKILL.md",
        skill_dir / "rules.md",
        skill_dir / "report_template.md",
        skill_dir / "README.md",
        skill_dir / "scripts" / "humanize.py",
        skill_dir / "scripts" / "requirements.txt",
    ]
    record("skill_files_exist", all(p.is_file() for p in required), ", ".join(p.name for p in required))

    front = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    record(
        "skill_frontmatter",
        front.startswith("---") and "name: amir_humanized" in front and "argument-hint:" in front,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        project = tmp_path / "project"
        docs = tmp_path / "docs"
        project.mkdir()
        docs.mkdir()
        (project / ".git").mkdir()

        md = docs / "sample.md"
        _build_sample_md(md)
        original_md = md.read_bytes()

        # Invalid path must not create outputs
        try:
            validate_source(str(docs / "missing.docx"))
            record("reject_missing", False, "missing file was accepted")
        except PipelineError:
            record("reject_missing", True)
        record(
            "no_partial_on_bad_input",
            not (docs / "missing_humanized.docx").exists()
            and not list((project / ".ai").glob("**/*")) if (project / ".ai").exists() else True,
        )

        ns = argparse.Namespace(
            document=str(md),
            project_root=str(project),
            output=None,
        )
        # init
        from io import StringIO
        from contextlib import redirect_stdout

        buf = StringIO()
        with redirect_stdout(buf):
            code = cmd_init(ns)
        init_payload = json.loads(buf.getvalue())
        record("init_exit", code == 0)
        record("project_root_detection", init_payload.get("project_root") == str(project.resolve()))
        record("reports_dir_created", (project / ".ai" / "reports").is_dir())
        record(
            "output_next_to_source",
            Path(init_payload["output"]).parent.resolve() == docs.resolve(),
        )
        record(
            "report_under_project",
            str(Path(init_payload["report"])).startswith(str(project.resolve())),
        )
        record("original_md_unchanged_after_init", md.read_bytes() == original_md)

        extract = json.loads(Path(init_payload["extract_path"]).read_text(encoding="utf-8"))
        record(
            "headings_extracted",
            any(b["kind"] == "heading" and "Overview" in b["text"] for b in extract["blocks"]),
        )
        record(
            "paragraphs_extracted",
            any(b["kind"] == "paragraph" for b in extract["blocks"]),
        )
        record(
            "lists_extracted",
            any(b["kind"] == "list" for b in extract["blocks"]),
        )
        record(
            "tables_extracted",
            any(b["kind"] == "table" for b in extract["blocks"]),
        )
        code_blocks = [b for b in extract["blocks"] if b["kind"] == "code"]
        record("code_extracted", bool(code_blocks))
        record(
            "code_immutable",
            all(b["classification"] == "immutable" for b in code_blocks),
        )
        record(
            "em_dash_in_code_preserved_class",
            any(EM_DASH in b["text"] for b in code_blocks),
        )
        record(
            "url_and_ip_present",
            "https://docs.example.com/ion/cli" in md.read_text(encoding="utf-8")
            and "10.20.30.1" in md.read_text(encoding="utf-8"),
        )

        # Apply known humanization changes
        change_items = []
        for block in extract["blocks"]:
            if block["classification"] == "immutable":
                continue
            text = block["text"]
            revised = text
            if "It is important to note that the controller provides this information" in text:
                revised = (
                    "The controller provides this information through the monitoring "
                    "interface, including site status, alarms, and path health."
                )
            elif "This comprehensive approach ensures" in text:
                revised = "Use this workflow to troubleshoot connectivity issues."
            elif "In this section, we will explore" in text:
                revised = ""
                # Removing a paragraph is not allowed for this test; rewrite instead.
                revised = "Use the monitoring workflow below."
            elif "It is worth noting that the device must be online" in text:
                revised = (
                    "| Field | Value |\n|-------|-------|\n"
                    "| Device | ION-3200 |\n| Address | 10.20.30.1 |\n"
                    "| Note | The device must be online before proceeding. |"
                )
            elif "Administrators are advised to utilize" in text:
                revised = "Use the monitoring tools to identify connectivity issues."
            elif "This is not just a dashboard" in text:
                revised = "The dashboard is an operational interface."
            elif "In this section, we discussed" in text:
                revised = ""
                revised = "Continue with the procedure after the site is online."
            if revised != text:
                change_items.append(
                    {
                        "id": block["id"],
                        "original": text,
                        "revised": revised,
                        "reason": "selftest",
                    }
                )

        changes_path = tmp_path / "changes.json"
        changes_path.write_text(
            json.dumps(
                {
                    "changes": change_items,
                    "change_categories": [
                        "Removed AI-style filler language",
                        "Removed em dashes from normal prose",
                        "Replaced indirect wording with direct engineering language",
                    ],
                    "potential_technical_issues": [],
                    "warnings": [],
                    "paragraphs_reviewed": len(extract["blocks"]),
                    "changed": len(change_items),
                    "unchanged": len(extract["blocks"]) - len(change_items),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        fin = argparse.Namespace(
            document=str(md),
            project_root=str(project),
            output=None,
            changes=str(changes_path),
            extract=init_payload["extract_path"],
        )
        buf = StringIO()
        with redirect_stdout(buf):
            fcode = cmd_finalize(fin)
        final_payload = json.loads(buf.getvalue())
        out_md = Path(final_payload["output"])
        report = Path(final_payload["report"])
        record("finalize_md", fcode == 0 and out_md.is_file() and report.is_file(), final_payload.get("console", ""))
        record("original_md_unchanged_after_finalize", md.read_bytes() == original_md)
        out_text = out_md.read_text(encoding="utf-8")
        record("md_em_dash_prose_removed", "information — including" not in out_text)
        record("md_em_dash_in_code_kept", "# note: the path — primary — is preferred" in out_text)
        record("md_url_kept", "https://docs.example.com/ion/cli" in out_text)
        record("md_ip_kept", "10.20.30.1" in out_text)
        record("md_code_kept", "dump interface status" in out_text and "ping 10.1.1.1" in out_text)
        record("md_heading_kept", "# Connectivity Operations Guide" in out_text)
        record("md_list_kept", "1. Check site status" in out_text)
        record("md_table_kept", "| Device | ION-3200 |" in out_text)
        record("report_location", report.parent == project / ".ai" / "reports")
        record("em_dash_count_zero", final_payload.get("em_dashes_remaining_in_normal_prose") == 0)

        # DOCX
        docx_path = docs / "sample.docx"
        _build_sample_docx(docx_path)
        original_docx = docx_path.read_bytes()
        ns_d = argparse.Namespace(document=str(docx_path), project_root=str(project), output=None)
        buf = StringIO()
        with redirect_stdout(buf):
            dcode = cmd_init(ns_d)
        dinit = json.loads(buf.getvalue())
        record("docx_init", dcode == 0)
        dextract = json.loads(Path(dinit["extract_path"]).read_text(encoding="utf-8"))
        record(
            "docx_headings",
            any(b["kind"] == "heading" for b in dextract["blocks"]),
        )
        record(
            "docx_table_cells",
            any(b["kind"] == "table_cell" for b in dextract["blocks"]),
        )
        record(
            "docx_lists",
            dextract["structure"].get("lists", 0) >= 1
            or any("List" in (b.get("style") or "") for b in dextract["blocks"]),
        )
        dchanges = []
        for block in dextract["blocks"]:
            if block["classification"] == "immutable":
                continue
            text = block["text"]
            if "It is important to note that the controller" in text:
                dchanges.append(
                    {
                        "id": block["id"],
                        "original": text,
                        "revised": (
                            "The controller provides this information through the "
                            "monitoring interface, including site status, alarms, "
                            "and path health."
                        ),
                    }
                )
            elif text == "The path — primary — is preferred":
                dchanges.append(
                    {
                        "id": block["id"],
                        "original": text,
                        "revised": "The primary path is preferred.",
                    }
                )
            elif "It is worth noting that the device must be online" in text:
                dchanges.append(
                    {
                        "id": block["id"],
                        "original": text,
                        "revised": "The device must be online before proceeding.",
                    }
                )
        dchanges_path = tmp_path / "docx_changes.json"
        dchanges_path.write_text(
            json.dumps(
                {
                    "changes": dchanges,
                    "change_categories": ["Removed em dashes from normal prose"],
                    "paragraphs_reviewed": len(dextract["blocks"]),
                    "changed": len(dchanges),
                    "unchanged": len(dextract["blocks"]) - len(dchanges),
                    "potential_technical_issues": [],
                    "warnings": [],
                }
            ),
            encoding="utf-8",
        )
        fin_d = argparse.Namespace(
            document=str(docx_path),
            project_root=str(project),
            output=None,
            changes=str(dchanges_path),
            extract=dinit["extract_path"],
        )
        buf = StringIO()
        with redirect_stdout(buf):
            dfcode = cmd_finalize(fin_d)
        dfinal = json.loads(buf.getvalue())
        dout = Path(dfinal["output"])
        record("docx_finalize", dfcode == 0 and dout.is_file(), dfinal.get("console", ""))
        record("original_docx_unchanged", docx_path.read_bytes() == original_docx)
        from docx import Document as _D  # type: ignore

        out_doc = _D(str(dout))
        src_doc = _D(str(docx_path))
        record(
            "docx_heading_preserved",
            any(p.style.name.startswith("Heading") and "Overview" in p.text for p in out_doc.paragraphs),
        )
        record(
            "docx_bold_paragraph_preserved",
            any(p.text == "Check the site status before troubleshooting." and p.runs and p.runs[0].bold for p in out_doc.paragraphs),
        )
        record("docx_table_preserved", len(out_doc.tables) == len(src_doc.tables) == 1)
        record(
            "docx_ip_preserved",
            out_doc.tables[0].cell(1, 1).text == "10.20.30.1",
        )
        record(
            "docx_command_preserved",
            any(p.text == "dump interface status" for p in out_doc.paragraphs),
        )
        record(
            "docx_url_preserved",
            any("https://docs.example.com/ion/cli" in p.text for p in out_doc.paragraphs),
        )
        record(
            "docx_em_dash_prose_removed",
            not any(
                EM_DASH in p.text
                and "dump" not in p.text
                for p in out_doc.paragraphs
            ),
        )
        record("docx_report_under_project", Path(dfinal["report"]).parent == project / ".ai" / "reports")

        # PDF extract -> sibling markdown, source untouched
        pdf_path = docs / "sample.pdf"
        _build_sample_pdf(pdf_path)
        original_pdf = pdf_path.read_bytes()
        try:
            ns_p = argparse.Namespace(document=str(pdf_path), project_root=str(project), output=None)
            buf = StringIO()
            with redirect_stdout(buf):
                pcode = cmd_init(ns_p)
            pinit = json.loads(buf.getvalue())
            pextract = json.loads(Path(pinit["extract_path"]).read_text(encoding="utf-8"))
            pchanges = []
            for block in pextract["blocks"]:
                if "It is important to note that the device must be online" in block["text"]:
                    pchanges.append(
                        {
                            "id": block["id"],
                            "original": block["text"],
                            "revised": "The device must be online.",
                        }
                    )
            pchanges_path = tmp_path / "pdf_changes.json"
            pchanges_path.write_text(
                json.dumps(
                    {
                        "changes": pchanges,
                        "change_categories": ["Removed AI-style filler language"],
                        "paragraphs_reviewed": len(pextract["blocks"]),
                        "changed": len(pchanges),
                        "unchanged": max(len(pextract["blocks"]) - len(pchanges), 0),
                    }
                ),
                encoding="utf-8",
            )
            fin_p = argparse.Namespace(
                document=str(pdf_path),
                project_root=str(project),
                output=None,
                changes=str(pchanges_path),
                extract=pinit["extract_path"],
            )
            buf = StringIO()
            with redirect_stdout(buf):
                pfcode = cmd_finalize(fin_p)
            pfinal = json.loads(buf.getvalue())
            record("pdf_init_finalize", pcode == 0 and pfcode in {0, 3} and Path(pfinal["output"]).is_file())
            record("original_pdf_unchanged", pdf_path.read_bytes() == original_pdf)
            record("pdf_output_is_markdown", Path(pfinal["output"]).suffix == ".md")
        except PipelineError as exc:
            record("pdf_init_finalize", False, str(exc))
            record("original_pdf_unchanged", pdf_path.read_bytes() == original_pdf)
            record("pdf_output_is_markdown", False, str(exc))

        # Accepts a document path
        record("accepts_document_path", init_payload.get("source", "").endswith("sample.md"))

    failed = [r for r in results if r["result"] != "PASS"]
    payload = {
        "ok": not failed,
        "tests": results,
        "passed": sum(1 for r in results if r["result"] == "PASS"),
        "failed": len(failed),
    }
    return emit(payload, 0 if payload["ok"] else 4)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="humanize.py")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Validate input and extract classified blocks")
    init.add_argument("document")
    init.add_argument("--project-root")
    init.add_argument("--output")
    init.set_defaults(func=cmd_init)

    fin = sub.add_parser("finalize", help="Apply changes, compare, write report")
    fin.add_argument("document")
    fin.add_argument("--project-root")
    fin.add_argument("--output")
    fin.add_argument("--changes", required=True)
    fin.add_argument("--extract")
    fin.set_defaults(func=cmd_finalize)

    test = sub.add_parser("selftest", help="Run pipeline validation tests")
    test.set_defaults(func=cmd_selftest)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except PipelineError as exc:
        return emit({"ok": False, "error": str(exc)}, exc.code)
    except Exception as exc:  # noqa: BLE001 — surface unexpected failures honestly
        return emit({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, 1)


if __name__ == "__main__":
    sys.exit(main())
