#!/usr/bin/env python3
"""
Amir_LiteLLM installer / health tool for the Palo Alto LiteLLM MCP gateway.

Registers gateway MCP servers as native remote (streamable HTTP) servers in
Claude Code and/or Cursor. The API key is NEVER written to any config file:
each host config references an environment variable that the host expands
at connect time (Claude: ${VAR}, Cursor: ${env:VAR}).

Stdlib only, so it runs unchanged on Windows, macOS and Linux and from any
host (Claude Code, Cursor, a plain terminal).

Subcommands
  deploy        copy this script + servers.json to ~/.amir/litellm (and skills to Cursor)
  config        show or set base URL
  set-key       store the API key as a user env var (interactive, hidden input)
  list          list known gateway servers and where they are installed
  install       register server(s) in claude / cursor
  uninstall     remove server(s) from claude / cursor
  status        env, config, network and (optionally) live MCP handshake per server
  tools         list a server's tools over MCP
  call          call one tool over MCP (for testing without restarting the host)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import getpass
import json
import os
import shutil
import socket
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
HOME = Path.home()
DEPLOY_DIR = HOME / ".amir" / "litellm"
CONFIG_FILE = DEPLOY_DIR / "config.json"
CURSOR_MCP = HOME / ".cursor" / "mcp.json"
CURSOR_SKILLS = HOME / ".cursor" / "skills"
PROTOCOL_VERSION = "2025-06-18"
HTTP_TIMEOUT_S = 30
SKILL_PREFIX = "litellm_"


# ---------------------------------------------------------------- registry/config

def _registry_path() -> Path:
    for candidate in (HERE / "servers.json", HERE.parent / "servers.json", DEPLOY_DIR / "servers.json"):
        if candidate.exists():
            return candidate
    sys.exit("servers.json not found next to the script or in ~/.amir/litellm")


def load_registry() -> dict[str, Any]:
    return json.loads(_registry_path().read_text(encoding="utf-8"))


def load_config() -> dict[str, Any]:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {}


def base_url(reg: dict[str, Any]) -> str:
    url = os.environ.get("LITELLM_MCP_BASE_URL") or load_config().get("base_url") or reg["default_base_url"]
    return url.rstrip("/")


def server_url(reg: dict[str, Any], key: str) -> str:
    remote = reg["servers"][key]["remote"]
    return f"{base_url(reg)}/{remote}/mcp" if remote else f"{base_url(reg)}/mcp"


def resolve_servers(reg: dict[str, Any], names: list[str]) -> list[str]:
    known = reg["servers"]
    if names == ["all"]:
        return [k for k in known if k != "gateway"]
    out = []
    for n in names:
        k = n.replace("-", "_").lower()
        if k not in known:
            sys.exit(f"unknown server '{n}'. Known: {', '.join(known)}")
        out.append(k)
    return out


def host_entry(reg: dict[str, Any], key: str, host: str) -> dict[str, Any]:
    var = reg["auth_env_var"]
    ref = f"${{{var}}}" if host == "claude" else f"${{env:{var}}}"
    entry: dict[str, Any] = {"url": server_url(reg, key), "headers": {reg["auth_header"]: f"Bearer {ref}"}}
    if host == "claude":
        entry = {"type": "http", **entry}
    return entry


# ---------------------------------------------------------------- file helpers

def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = path.with_name(f"{path.name}.bak-{stamp}")
    shutil.copy2(path, dst)
    return dst


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8-sig").strip()
    return json.loads(text) if text else {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


# ---------------------------------------------------------------- claude host

def claude_cli() -> str | None:
    return shutil.which("claude") or shutil.which("claude.cmd") or shutil.which("claude.exe")


def claude_run(args: list[str]) -> subprocess.CompletedProcess:
    exe = claude_cli()
    if not exe:
        raise RuntimeError("claude CLI not found on PATH")
    return subprocess.run([exe, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")


def claude_project_file(project_dir: Path) -> Path:
    return project_dir / ".mcp.json"


def claude_installed(scope: str, project_dir: Path | None) -> dict[str, Any]:
    if scope == "project" and project_dir:
        return read_json(claude_project_file(project_dir)).get("mcpServers", {})
    path = HOME / ".claude.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("mcpServers", {}) or {}
    except json.JSONDecodeError:
        return {}


def claude_install(reg, key, scope, project_dir) -> str:
    name = reg["servers"][key]["local"]
    entry = host_entry(reg, key, "claude")
    if scope == "project":
        path = claude_project_file(project_dir)
        data = read_json(path)
        backup(path)
        data.setdefault("mcpServers", {})[name] = entry
        write_json(path, data)
        return f"claude(project) {name} -> {path}"
    claude_run(["mcp", "remove", "-s", "user", name])  # idempotent re-install; absent is fine
    res = claude_run(["mcp", "add-json", "-s", "user", name, json.dumps(entry)])
    if res.returncode != 0:
        raise RuntimeError(f"claude mcp add-json failed: {(res.stderr or res.stdout).strip()}")
    return f"claude(user) {name} -> {entry['url']}"


def claude_uninstall(reg, key, scope, project_dir) -> str:
    name = reg["servers"][key]["local"]
    if scope == "project":
        path = claude_project_file(project_dir)
        data = read_json(path)
        if name in data.get("mcpServers", {}):
            backup(path)
            del data["mcpServers"][name]
            write_json(path, data)
            return f"claude(project) removed {name}"
        return f"claude(project) {name} not installed"
    res = claude_run(["mcp", "remove", "-s", "user", name])
    return f"claude(user) removed {name}" if res.returncode == 0 else f"claude(user) {name} not installed"


# ---------------------------------------------------------------- cursor host

def cursor_file(scope: str, project_dir: Path | None) -> Path:
    return (project_dir / ".cursor" / "mcp.json") if scope == "project" and project_dir else CURSOR_MCP


def cursor_install(reg, key, scope, project_dir) -> str:
    path = cursor_file(scope, project_dir)
    data = read_json(path)
    name = reg["servers"][key]["local"]
    backup(path)
    data.setdefault("mcpServers", {})[name] = host_entry(reg, key, "cursor")
    write_json(path, data)
    return f"cursor({scope}) {name} -> {path}"


def cursor_uninstall(reg, key, scope, project_dir) -> str:
    path = cursor_file(scope, project_dir)
    data = read_json(path)
    name = reg["servers"][key]["local"]
    if name not in data.get("mcpServers", {}):
        return f"cursor({scope}) {name} not installed"
    backup(path)
    del data["mcpServers"][name]
    write_json(path, data)
    return f"cursor({scope}) removed {name}"


# ---------------------------------------------------------------- MCP client (streamable HTTP)

class McpError(RuntimeError):
    pass


def _api_key(reg) -> str:
    key = os.environ.get(reg["auth_env_var"]) or _windows_user_env(reg["auth_env_var"])
    if not key:
        raise McpError(f"{reg['auth_env_var']} is not set (run: litellm_mcp.py set-key)")
    return key


def _parse_body(raw: str, content_type: str) -> Any:
    if "text/event-stream" in content_type:
        last = None
        for line in raw.splitlines():
            if line.startswith("data:"):
                payload = line[5:].strip()
                if payload:
                    last = json.loads(payload)
        return last
    return json.loads(raw) if raw.strip() else None


class McpSession:
    def __init__(self, reg: dict[str, Any], key: str):
        self.url = server_url(reg, key)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            reg["auth_header"]: f"Bearer {_api_key(reg)}",
        }
        self.session_id: str | None = None
        self._id = 0
        self.ctx = ssl.create_default_context()

    def _post(self, payload: dict[str, Any]) -> Any:
        headers = dict(self.headers)
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        req = urllib.request.Request(self.url, data=json.dumps(payload).encode(), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S, context=self.ctx) as resp:
                self.session_id = resp.headers.get("Mcp-Session-Id") or self.session_id
                raw = resp.read().decode("utf-8", "replace")
                return _parse_body(raw, resp.headers.get("Content-Type", ""))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            raise McpError(f"HTTP {e.code} from {self.url}: {body}") from e
        except (urllib.error.URLError, socket.timeout, OSError) as e:
            raise McpError(f"cannot reach {self.url}: {e}") from e

    def request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        self._id += 1
        msg = self._post({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}})
        if not isinstance(msg, dict):
            raise McpError(f"unexpected response to {method}: {msg!r}"[:300])
        if "error" in msg:
            raise McpError(f"{method}: {msg['error']}")
        return msg.get("result")

    def open(self) -> dict[str, Any]:
        info = self.request("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "amir-litellm", "version": "0.1.0"},
        })
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return info or {}

    def list_tools(self) -> list[dict[str, Any]]:
        tools, cursor = [], None
        while True:
            res = self.request("tools/list", {"cursor": cursor} if cursor else {})
            tools += res.get("tools", [])
            cursor = res.get("nextCursor")
            if not cursor:
                return tools


# ---------------------------------------------------------------- network + env

def _windows_user_env(name: str) -> str | None:
    """Read a freshly-set user env var that this process did not inherit (Windows only)."""
    if os.name != "nt":
        return None
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return winreg.QueryValueEx(k, name)[0]
    except OSError:
        return None


def tcp_check(url: str) -> tuple[bool, str]:
    p = urlparse(url)
    host, port = p.hostname or "", p.port or (443 if p.scheme == "https" else 80)
    try:
        addr = socket.gethostbyname(host)
    except OSError as e:
        return False, f"DNS failed for {host}: {e}"
    try:
        with socket.create_connection((addr, port), timeout=5):
            return True, f"{host} -> {addr}:{port} reachable"
    except OSError as e:
        private = addr.startswith(("10.", "192.168.", "172."))
        hint = " (internal address: connect to the Palo Alto VPN)" if private else ""
        return False, f"{host} -> {addr}:{port} not reachable{hint}: {e}"


# ---------------------------------------------------------------- commands

def cmd_deploy(args) -> None:
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__).resolve(), DEPLOY_DIR / "litellm_mcp.py")
    shutil.copy2(_registry_path(), DEPLOY_DIR / "servers.json")
    print(f"deployed script + registry -> {DEPLOY_DIR}")
    if args.cursor_skills:
        src = HERE.parent / "skills"
        if not src.exists():
            sys.exit(f"skills folder not found at {src} (run deploy from the plugin checkout)")
        CURSOR_SKILLS.mkdir(parents=True, exist_ok=True)
        count = 0
        for skill in sorted(p for p in src.iterdir() if p.is_dir() and p.name.startswith(SKILL_PREFIX)):
            dst = CURSOR_SKILLS / skill.name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(skill, dst)
            count += 1
        print(f"copied {count} {SKILL_PREFIX}* skills -> {CURSOR_SKILLS}")


def cmd_config(args) -> None:
    reg = load_registry()
    cfg = load_config()
    if args.base_url:
        cfg["base_url"] = args.base_url.rstrip("/")
        DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
        write_json(CONFIG_FILE, cfg)
        print(f"base_url set -> {cfg['base_url']} (re-run install to rewrite host configs)")
    source = "env LITELLM_MCP_BASE_URL" if os.environ.get("LITELLM_MCP_BASE_URL") else (
        "config.json" if cfg.get("base_url") else "servers.json default")
    print(json.dumps({"base_url": base_url(reg), "source": source, "auth_header": reg["auth_header"],
                      "auth_env_var": reg["auth_env_var"]}, indent=2))


def cmd_set_key(args) -> None:
    reg = load_registry()
    var = reg["auth_env_var"]
    if not sys.stdin.isatty():
        sys.exit(f"set-key is interactive. Run it yourself in a terminal: python \"{DEPLOY_DIR / 'litellm_mcp.py'}\" set-key")
    value = getpass.getpass(f"Paste your LiteLLM virtual key for {var} (input hidden): ").strip()
    if not value:
        sys.exit("empty key, nothing stored")
    if os.name == "nt":
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, var, 0, winreg.REG_SZ, value)
        # Broadcast WM_SETTINGCHANGE so newly started apps see the variable.
        import ctypes
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, None)
        print(f"{var} stored as a Windows user environment variable. Fully quit and reopen Claude Code / Cursor.")
    else:
        print(f"Add this line to your shell profile (~/.zshrc or ~/.bashrc), then restart the app:\n"
              f"  export {var}='<your key>'\n"
              f"macOS GUI apps launched from the Dock also need: launchctl setenv {var} '<your key>'")


def cmd_list(args) -> None:
    reg = load_registry()
    claude_user = claude_installed("user", None)
    cursor_user = read_json(CURSOR_MCP).get("mcpServers", {})
    print(f"{'server':18} {'local name':26} {'risk':12} {'claude':7} {'cursor':7} summary")
    for k, s in reg["servers"].items():
        c = "yes" if s["local"] in claude_user else "-"
        u = "yes" if s["local"] in cursor_user else "-"
        print(f"{k:18} {s['local']:26} {s['risk']:12} {c:7} {u:7} {s['summary']}")


def _hosts(h: str) -> list[str]:
    return ["claude", "cursor"] if h == "both" else [h]


def _project_dir(args) -> Path | None:
    if args.scope != "project":
        return None
    return Path(args.project_dir or os.getcwd()).resolve()


def cmd_install(args, remove: bool = False) -> None:
    reg = load_registry()
    pdir = _project_dir(args)
    failures = 0
    for key in resolve_servers(reg, args.servers):
        for host in _hosts(args.host):
            fn = {("claude", False): claude_install, ("claude", True): claude_uninstall,
                  ("cursor", False): cursor_install, ("cursor", True): cursor_uninstall}[(host, remove)]
            try:
                print("OK  ", fn(reg, key, args.scope, pdir))
            except Exception as e:  # report and continue with the other hosts/servers
                failures += 1
                print("FAIL", host, key, "-", e)
    if not remove:
        var = reg["auth_env_var"]
        present = bool(os.environ.get(var) or _windows_user_env(var))
        print(f"\n{var}: {'set' if present else 'NOT SET -> run set-key'} | base URL: {base_url(reg)}")
        print("Restart Claude Code / reload Cursor MCP so the new server connects.")
    sys.exit(1 if failures else 0)


def cmd_status(args) -> None:
    reg = load_registry()
    var = reg["auth_env_var"]
    in_proc, in_user = bool(os.environ.get(var)), bool(_windows_user_env(var))
    ok, net = tcp_check(base_url(reg))
    claude_user = claude_installed("user", None)
    cursor_user = read_json(CURSOR_MCP).get("mcpServers", {})
    report: dict[str, Any] = {
        "base_url": base_url(reg),
        "network": net,
        "api_key_env": {"name": var, "in_this_process": in_proc, "in_windows_user_env": in_user},
        "claude_cli": bool(claude_cli()),
        "servers": {},
    }
    targets = resolve_servers(reg, args.servers) if args.servers else [
        k for k, s in reg["servers"].items() if s["local"] in claude_user or s["local"] in cursor_user]
    for key in targets:
        s = reg["servers"][key]
        row: dict[str, Any] = {
            "url": server_url(reg, key),
            "claude": s["local"] in claude_user,
            "cursor": s["local"] in cursor_user,
        }
        if args.probe:
            if not ok:
                row["live"] = "skipped: network unreachable"
            else:
                try:
                    sess = McpSession(reg, key)
                    info = sess.open()
                    tools = sess.list_tools()
                    row["live"] = {"server": info.get("serverInfo", {}), "tool_count": len(tools),
                                   "tools": [t["name"] for t in tools][: args.max_tools]}
                except McpError as e:
                    row["live"] = f"error: {e}"
        report["servers"][key] = row
    print(json.dumps(report, indent=2))


def cmd_tools(args) -> None:
    reg = load_registry()
    key = resolve_servers(reg, [args.server])[0]
    sess = McpSession(reg, key)
    sess.open()
    for t in sess.list_tools():
        desc = (t.get("description") or "").strip().splitlines()
        print(f"- {t['name']}: {desc[0] if desc else ''}"[:200])


def cmd_call(args) -> None:
    reg = load_registry()
    key = resolve_servers(reg, [args.server])[0]
    params = json.loads(args.arguments) if args.arguments else {}
    sess = McpSession(reg, key)
    sess.open()
    result = sess.request("tools/call", {"name": args.tool, "arguments": params})
    for block in (result or {}).get("content", []):
        print(block.get("text") if block.get("type") == "text" else json.dumps(block)[:500])
    if (result or {}).get("isError"):
        sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("deploy"); p.add_argument("--cursor-skills", action="store_true"); p.set_defaults(fn=cmd_deploy)
    p = sub.add_parser("config"); p.add_argument("--base-url"); p.set_defaults(fn=cmd_config)
    p = sub.add_parser("set-key"); p.set_defaults(fn=cmd_set_key)
    p = sub.add_parser("list"); p.set_defaults(fn=cmd_list)
    for name, remove in (("install", False), ("uninstall", True)):
        p = sub.add_parser(name)
        p.add_argument("servers", nargs="+", help="server key(s) from servers.json, or 'all'")
        p.add_argument("--host", choices=["claude", "cursor", "both"], default="both")
        p.add_argument("--scope", choices=["user", "project"], default="user")
        p.add_argument("--project-dir")
        p.set_defaults(fn=lambda a, r=remove: cmd_install(a, r))
    p = sub.add_parser("status")
    p.add_argument("servers", nargs="*")
    p.add_argument("--probe", action="store_true", help="open a live MCP session and list tools")
    p.add_argument("--max-tools", type=int, default=15)
    p.set_defaults(fn=cmd_status)
    p = sub.add_parser("tools"); p.add_argument("server"); p.set_defaults(fn=cmd_tools)
    p = sub.add_parser("call"); p.add_argument("server"); p.add_argument("tool"); p.add_argument("arguments", nargs="?")
    p.set_defaults(fn=cmd_call)

    args = ap.parse_args()
    try:
        args.fn(args)
    except McpError as e:
        sys.exit(f"MCP error: {e}")


if __name__ == "__main__":
    main()
