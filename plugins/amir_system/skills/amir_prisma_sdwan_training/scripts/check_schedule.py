#!/usr/bin/env python3
"""check_schedule.py - quality gates for Prisma SD-WAN training plans written in Markdown.

Gate 1  basic  : every day's session table (Start | End | ...) sums to the expected scheduled hours,
                 contact time and breaks are reported separately, and the week totals match.
Gate 2  advanced: the module table (| ID | ... | Theory h | Demo h | Lab h | Assessment h | Total h |)
                 has rows whose parts sum to their Total, and the grand total line matches.

Usage:
  python check_schedule.py basic 01_BASIC_5_DAY_PLAN.md [--days 5] [--hours-per-day 8]
  python check_schedule.py advanced 02_ADVANCED_TRAINING_PATH.md

Session table rows look like:  | 09:00 | 10:30 | Theory | ... |
Rows whose Type contains "break" or "lunch" count as break time. A day starts at a heading that
contains the word "Day" followed by its number (e.g. "## Day 3").
Exit code 0 = all gates pass, 1 = a gate failed, 2 = file or table not found.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TIME = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*$")
DAY_HEADING = re.compile(r"^#{1,4}\s.*\bDay\s+(\d+)\b", re.I)


def minutes(cell: str) -> int | None:
    m = TIME.match(cell)
    if not m:
        return None
    return int(m.group(1)) * 60 + int(m.group(2))


def parse_basic(text: str) -> dict[int, list[tuple[int, int, str]]]:
    """Return {day: [(start_min, end_min, type), ...]}."""
    days: dict[int, list[tuple[int, int, str]]] = {}
    current = None
    for line in text.splitlines():
        head = DAY_HEADING.match(line)
        if head:
            current = int(head.group(1))
            days.setdefault(current, [])
            continue
        if current is None or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        start, end = minutes(cells[0]), minutes(cells[1])
        if start is None or end is None:
            continue
        days[current].append((start, end, cells[2]))
    return days


def check_basic(path: Path, expected_days: int, hours_per_day: float) -> int:
    text = path.read_text(encoding="utf-8")
    days = parse_basic(text)
    if not days:
        print("no day session tables found (need '## Day N' headings and | HH:MM | HH:MM | Type | rows)")
        return 2
    status = 0
    total_sched = total_contact = total_break = 0
    print("| Day | Sessions | Scheduled h | Contact h | Break h | Gaps/overlaps |")
    for day in sorted(days):
        rows = sorted(days[day])
        sched = contact = brk = 0
        problems = []
        for i, (s, e, kind) in enumerate(rows):
            if e <= s:
                problems.append(f"row {i + 1} ends before it starts")
            dur = max(0, e - s)
            sched += dur
            if re.search(r"break|lunch", kind, re.I):
                brk += dur
            else:
                contact += dur
            if i and s != rows[i - 1][1]:
                problems.append(f"gap/overlap before {s // 60:02d}:{s % 60:02d}")
        ok = abs(sched / 60 - hours_per_day) < 0.01 and not problems
        if not ok:
            status = 1
        print(f"| {day} | {len(rows)} | {sched / 60:.2f} | {contact / 60:.2f} | {brk / 60:.2f} | {'; '.join(problems) or ('OK' if ok else f'expected {hours_per_day} h')} |")
        total_sched += sched
        total_contact += contact
        total_break += brk
    if len(days) != expected_days:
        print(f"FAIL: {len(days)} day(s) found, expected {expected_days}")
        status = 1
    print(f"Total scheduled {total_sched / 60:.2f} h (expected {expected_days * hours_per_day:.2f}); contact {total_contact / 60:.2f} h; breaks {total_break / 60:.2f} h")
    if abs(total_sched / 60 - expected_days * hours_per_day) > 0.01:
        status = 1
    print("PASS" if status == 0 else "FAIL")
    return status


HOURS_HEADER = re.compile(r"theory\s*h", re.I)


def parse_advanced(text: str):
    """Return (rows, grand_total) where rows = [(id, theory, demo, lab, assess, total)]."""
    rows = []
    grand = None
    header_idx = None
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        lowered = [c.lower() for c in cells]
        if header_idx is None and any(HOURS_HEADER.search(c) for c in cells):
            header_idx = {}
            for name, key in (("theory", "theory"), ("demo", "demo"), ("lab", "lab"), ("assess", "assess"), ("total", "total")):
                for i, c in enumerate(lowered):
                    if c.startswith(name) and "h" in c:
                        header_idx[key] = i
                        break
            continue
        if header_idx is None or set(cells[0]) <= set("-: "):
            continue
        try:
            vals = {k: float(cells[i]) for k, i in header_idx.items()}
        except (ValueError, IndexError):
            if cells[0].lower().startswith("total") or "total" in lowered[0]:
                for c in cells[1:]:
                    try:
                        grand = float(c.replace("h", "").strip())
                    except ValueError:
                        continue
            continue
        if cells[0].lower().startswith("total"):
            grand = vals.get("total")
            continue
        rows.append((cells[0], vals.get("theory", 0), vals.get("demo", 0), vals.get("lab", 0), vals.get("assess", 0), vals.get("total", 0)))
    return rows, grand


def check_advanced(path: Path) -> int:
    rows, grand = parse_advanced(path.read_text(encoding="utf-8"))
    if not rows:
        print("no module hours table found (header must contain 'Theory h' ... 'Total h')")
        return 2
    status = 0
    total = 0.0
    for ident, th, de, la, asmt, tot in rows:
        parts = th + de + la + asmt
        total += tot
        if abs(parts - tot) > 0.01:
            print(f"FAIL {ident}: parts {parts:g} h != total {tot:g} h")
            status = 1
    print(f"{len(rows)} modules; sum of module totals {total:g} h; declared grand total {grand if grand is not None else 'missing'}")
    if grand is None or abs(grand - total) > 0.01:
        print("FAIL: grand total line missing or different from the sum of modules")
        status = 1
    print("PASS" if status == 0 else "FAIL")
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="mode", required=True)
    b = sub.add_parser("basic")
    b.add_argument("file")
    b.add_argument("--days", type=int, default=5)
    b.add_argument("--hours-per-day", type=float, default=8.0)
    a = sub.add_parser("advanced")
    a.add_argument("file")
    args = parser.parse_args(argv)
    path = Path(args.file)
    if not path.is_file():
        print(f"file not found: {path}")
        return 2
    if args.mode == "basic":
        return check_basic(path, args.days, args.hours_per_day)
    return check_advanced(path)


if __name__ == "__main__":
    sys.exit(main())
