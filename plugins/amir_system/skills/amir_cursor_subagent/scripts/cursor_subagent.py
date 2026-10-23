#!/usr/bin/env python3
"""cursor_subagent.py - run ONE bounded task on the local Cursor agent (Cursor SDK).

Default model: composer-2.5 with the "fast" parameter on (Cursor's own default
variant for Composer 2.5). Any model id the SDK lists can be used instead
(``--list-models``), with per-model parameters via ``--param id=value``.

Reads CURSOR_API_KEY from the environment. Never prints the key.
Exit codes: 0 finished, 1 setup/startup problem, 2 the agent run ended in error.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

DEFAULT_MODEL = "composer-2.5"
FAST_DEFAULT_PREFIXES = ("composer",)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass


def _fail(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _patch_win32_bridge_discovery() -> None:
    """cursor-sdk 1.0.35: selectors.select() on stderr pipes raises WinError 10038."""
    if sys.platform != "win32":
        return

    import cursor_sdk._bridge as bridge_mod
    from cursor_sdk.errors import CursorSDKError

    parse_discovery_line = bridge_mod.parse_discovery_line

    def _read_discovery(process, timeout: float):
        if process.stderr is None:
            raise CursorSDKError("Bridge process stderr is unavailable")
        deadline = time.monotonic() + timeout
        stderr_lines: list[str] = []
        while time.monotonic() < deadline:
            line = process.stderr.readline()
            if line:
                stderr_lines.append(line)
                discovery = parse_discovery_line(line)
                if discovery is not None:
                    return discovery
            else:
                exit_code = process.poll()
                if exit_code is not None:
                    raise CursorSDKError(
                        f"Bridge exited before discovery with status {exit_code}: " + "".join(stderr_lines)
                    )
                time.sleep(0.05)
        raise CursorSDKError("Timed out waiting for bridge discovery")

    bridge_mod._read_discovery = _read_discovery


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Delegate one bounded task to a local Cursor agent.")
    p.add_argument("prompt", nargs="?", help="task text; or use --task-file / stdin")
    p.add_argument("--task-file", help="UTF-8 file holding the full task text (preferred)")
    p.add_argument("--cwd", default=os.getcwd(), help="repo root the agent works in (default: cwd)")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Cursor model id (default {DEFAULT_MODEL})")
    p.add_argument("--param", action="append", default=[], metavar="ID=VALUE",
                   help="model parameter, repeatable (fast=true, effort=high, context=1m)")
    p.add_argument("--no-fast", action="store_true", help="turn the default fast=true off for Composer")
    p.add_argument("--json", action="store_true", help="emit one JSON object instead of plain text")
    p.add_argument("--events", metavar="FILE", help="append one line per stream event to FILE (diagnostics)")
    p.add_argument("--list-models", action="store_true", help="list model ids, parameters and defaults; exit")
    p.add_argument("--store-root", default=os.environ.get("CURSOR_SDK_STORE_ROOT"),
                   help="short dir for the agent store (default ~/.amir/composer-store)")
    return p.parse_args(argv)


def build_model_params(model: str, params: list[str], no_fast: bool) -> list[dict[str, str]]:
    values: dict[str, str] = {}
    if model.startswith(FAST_DEFAULT_PREFIXES):
        values["fast"] = "false" if no_fast else "true"
    elif no_fast:
        values["fast"] = "false"
    for item in params:
        if "=" not in item:
            _fail(f"--param needs ID=VALUE, got {item!r}", 1)
        key, value = item.split("=", 1)
        values[key.strip()] = value.strip()
    return [{"id": k, "value": v} for k, v in values.items()]


def read_prompt(args: argparse.Namespace) -> str:
    if args.task_file:
        with open(args.task_file, encoding="utf-8-sig") as fh:
            text = fh.read()
    elif args.prompt:
        text = args.prompt
    else:
        text = sys.stdin.read()
    text = text.strip()
    if not text:
        _fail("No task text: pass it as an argument, --task-file, or on stdin.", 2)
    return text


def list_models() -> None:
    from cursor_sdk import Cursor

    for m in Cursor.models.list():
        params = ",".join(p.id for p in m.parameters) or "-"
        default = next((v for v in m.variants if v.is_default), None)
        dflt = " ".join(f"{x.id}={x.value}" for x in default.params) if default else "-"
        print(f"{m.id:<22} {m.display_name:<22} params={params:<30} default: {dflt}")


def _redact(text: str, key: str) -> str:
    return text.replace(key, "[REDACTED]") if key else text


def _event_line(ev, key: str) -> str:
    msg = getattr(ev, "sdk_message", None)
    if msg is None:
        return _redact(f"{ev.kind}", key)
    kind = getattr(msg, "type", "?")
    text = getattr(msg, "text", None) or getattr(msg, "message", None) or ""
    tool = getattr(msg, "tool_name", None) or getattr(msg, "name", None) or ""
    status = getattr(msg, "status", "") or ""
    return _redact(f"{kind} {status} {tool} {text}".strip()[:400], key)


def run(args: argparse.Namespace, prompt: str):
    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

    store_root = args.store_root or os.path.join(os.path.expanduser("~"), ".amir", "composer-store")
    os.makedirs(store_root, exist_ok=True)
    key = os.environ["CURSOR_API_KEY"]
    params = build_model_params(args.model, args.param, args.no_fast)
    model = {"id": args.model, "params": params} if params else args.model
    opts = AgentOptions(
        api_key=key,
        model=model,
        local=LocalAgentOptions(cwd=os.path.abspath(args.cwd), store={"type": "jsonl", "rootDir": store_root}),
    )
    # Always stream: the final RunResult carries no error text, the ERROR status event does.
    last_error = ""
    agent = Agent.create(opts)
    try:
        handle = agent.send(prompt)
        fh = open(args.events, "a", encoding="utf-8") if args.events else None
        try:
            if fh:
                fh.write(f"# {time.strftime('%Y-%m-%dT%H:%M:%S')} model={args.model} cwd={args.cwd}\n")
            for ev in handle.events():
                msg = getattr(ev, "sdk_message", None)
                if msg is not None and getattr(msg, "type", "") == "status" and getattr(msg, "status", "") == "ERROR":
                    last_error = _redact(getattr(msg, "message", "") or "", key)
                if fh:
                    fh.write(_event_line(ev, key) + "\n")
                    fh.flush()
        finally:
            if fh:
                fh.close()
        return handle.wait(), params, last_error
    finally:
        agent.close()


def main() -> None:
    args = parse_args()
    if not os.environ.get("CURSOR_API_KEY"):
        _fail("CURSOR_API_KEY is not set (see the skill's setup section).", 1)
    try:
        _patch_win32_bridge_discovery()
        from cursor_sdk import CursorAgentError
        from cursor_sdk.errors import CursorSDKError
    except ImportError:
        _fail("cursor-sdk is not installed in this interpreter. Run: pip install cursor-sdk", 1)

    if args.list_models:
        list_models()
        return

    prompt = read_prompt(args)
    started = time.monotonic()
    try:
        result, params, last_error = run(args, prompt)
    except (CursorAgentError, CursorSDKError) as err:
        _fail(f"Cursor agent startup failed: {getattr(err, 'message', err)}", 1)

    elapsed_ms = int((time.monotonic() - started) * 1000)
    text = getattr(result, "result", None) or ""
    if result.status == "error":
        detail = last_error or getattr(result, "error", None) or text or "(no detail; rerun with --events FILE)"
        print(f"Cursor agent run failed: run_id={getattr(result, 'id', None)} model={args.model}: {detail}",
              file=sys.stderr)
        raise SystemExit(2)
    if args.json:
        print(json.dumps({
            "status": result.status,
            "result": text,
            "run_id": getattr(result, "id", None),
            "model": args.model,
            "params": params,
            "duration_ms": getattr(result, "duration_ms", None) or elapsed_ms,
            "cwd": os.path.abspath(args.cwd),
        }, ensure_ascii=False))
    else:
        print(text)


if __name__ == "__main__":
    main()
