#!/usr/bin/env python3
"""Shared safety helpers: masking, confirm gates, destructive patterns."""
from __future__ import annotations

import os
import re
import sys
from typing import Iterable

DESTRUCTIVE_REMOTE = re.compile(
    r"\b(rm\s+-rf|mkfs|shutdown|reboot|dd\s+if=|:(){:|:&};:)\b",
    re.I,
)

def mask_secret(value: str | None) -> str:
    if not value:
        return "(missing)"
    v = value.strip()
    if len(v) <= 4:
        return "****"
    return f"****{v[-4:]}"

def require_env(names: Iterable[str]) -> dict[str, str]:
    missing = [n for n in names if not (os.environ.get(n) or "").strip()]
    if missing:
        print("REFUSING — missing env var(s) by name only:", ", ".join(missing), file=sys.stderr)
        raise SystemExit(2)
    return {n: os.environ[n].strip() for n in names}

def confirm(prompt: str, *, typed: str | None = None) -> bool:
    print(prompt)
    if typed:
        print(f'Type exactly: {typed}')
        ans = input("> ").strip()
        return ans == typed
    ans = input("Proceed? [y/N] > ").strip().lower()
    return ans in {"y", "yes"}

def print_command(cmd: str | list[str]) -> None:
    if isinstance(cmd, list):
        import shlex
        try:
            s = " ".join(shlex.quote(c) for c in cmd)
        except Exception:
            s = " ".join(cmd)
    else:
        s = cmd
    print("EXACT COMMAND/REQUEST:")
    print(s)
