#!/usr/bin/env python3
"""
Amir_Workspace_MCP — install local stdio MCP servers (Confluence, Jira, Asana)
that read personal API tokens from the palo workspace .env or OS environment.

Tokens are NEVER written to MCP config files. Runners merge palo/.env at startup.

  deploy [--cursor-skills]
  list
  install <server...|all> [--host claude|cursor|codex|both|all-hosts]
  uninstall ...
  status [server...] [--probe]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parent
HOME = Path.home()
DEPLOY_DIR = HOME / ".amir" / "workspace_mcp"
CURSOR_MCP = HOME / ".cursor" / "mcp.json"
CODEX_MCP = HOME / ".codex" / "mcp.json"
CURSOR_SKILLS = HOME / ".cursor" / "skills"
SKILL_PREFIX = "workspace_mcp_"


def _registry_path() -> Path:
    for candidate in (DEPLOY_DIR / "servers.json", PLUGIN_ROOT / "servers.json"):
        if candidate.exists():
            return candidate
    sys.exit("servers.json not found in plugin or ~/.amir/workspace_mcp")


def load_registry() -> dict[str, Any]:
    return json.loads(_registry_path().read_text(encoding="utf-8"))


def plugin_root() -> Path:
    if (DEPLOY_DIR / "mcp").is_dir():
        return DEPLOY_DIR
    return PLUGIN_ROOT


def runner_js(key: str) -> Path:
    path = plugin_root() / "mcp" / key / "run-mcp.js"
    if not path.is_file():
        sys.exit(f"Missing runner: {path} (run: workspace_mcp.py deploy)")
    return path


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


def backup(path: Path) -> None:
    if path.exists():
        stamp = __import__("datetime").datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(path, path.with_name(f"{path.name}.bak-{stamp}"))


def host_entry(key: str, host: str) -> dict[str, Any]:
    runner = str(runner_js(key))
    entry: dict[str, Any] = {"command": "node", "args": [runner]}
    if host == "claude":
        entry = {"type": "stdio", **entry}
    return entry


def resolve_servers(reg: dict[str, Any], names: list[str]) -> list[str]:
    known = reg["servers"]
    if names == ["all"]:
        return list(known.keys())
    out: list[str] = []
    for n in names:
        k = n.replace("-", "_").lower()
        if k not in known:
            sys.exit(f"unknown server '{n}'. Known: {', '.join(known)}")
        out.append(k)
    return out


def claude_cli() -> str | None:
    return shutil.which("claude") or shutil.which("claude.cmd") or shutil.which("claude.exe")


def claude_run(args: list[str]) -> subprocess.CompletedProcess:
    exe = claude_cli()
    if not exe:
        raise RuntimeError("claude CLI not found on PATH")
    return subprocess.run([exe, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")


def claude_installed(scope: str, project_dir: Path | None) -> dict[str, Any]:
    if scope == "project" and project_dir:
        return read_json(project_dir / ".mcp.json").get("mcpServers", {}) or {}
    path = HOME / ".claude.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("mcpServers", {}) or {}


def claude_install(reg, key: str, scope: str, project_dir: Path | None) -> str:
    name = reg["servers"][key]["local"]
    entry = host_entry(key, "claude")
    if scope == "project":
        path = (project_dir or Path.cwd()) / ".mcp.json"
        data = read_json(path)
        backup(path)
        data.setdefault("mcpServers", {})[name] = entry
        write_json(path, data)
        return f"claude(project) {name} -> {path}"
    claude_run(["mcp", "remove", "-s", "user", name])
    res = claude_run(["mcp", "add-json", "-s", "user", name, json.dumps(entry)])
    if res.returncode != 0:
        raise RuntimeError((res.stderr or res.stdout or "claude mcp add-json failed").strip())
    return f"claude(user) {name}"


def claude_uninstall(reg, key: str, scope: str, project_dir: Path | None) -> str:
    name = reg["servers"][key]["local"]
    if scope == "project":
        path = (project_dir or Path.cwd()) / ".mcp.json"
        data = read_json(path)
        if name in data.get("mcpServers", {}):
            backup(path)
            del data["mcpServers"][name]
            write_json(path, data)
            return f"claude(project) removed {name}"
        return f"claude(project) {name} not installed"
    res = claude_run(["mcp", "remove", "-s", "user", name])
    return f"claude(user) removed {name}" if res.returncode == 0 else f"claude(user) {name} not installed"


def json_host_install(path: Path, reg, key: str, label: str) -> str:
    data = read_json(path)
    name = reg["servers"][key]["local"]
    backup(path)
    data.setdefault("mcpServers", {})[name] = host_entry(key, label)
    write_json(path, data)
    return f"{label} {name} -> {path}"


def json_host_uninstall(path: Path, reg, key: str, label: str) -> str:
    data = read_json(path)
    name = reg["servers"][key]["local"]
    if name not in data.get("mcpServers", {}):
        return f"{label} {name} not installed"
    backup(path)
    del data["mcpServers"][name]
    write_json(path, data)
    return f"{label} removed {name}"


def _env_present(names: list[str]) -> dict[str, bool]:
    palo = palo_env_map()
    out: dict[str, bool] = {}
    for n in names:
        out[n] = bool((os.environ.get(n) or "").strip() or (palo.get(n) or "").strip())
    return out


def palo_env_path() -> Path:
    root = (os.environ.get("WORKSPACES_ROOT") or "").strip()
    if not root:
        root = r"E:\PC3_Shared\workspaces" if os.name == "nt" else str(HOME / "workspaces")
    rel = load_registry().get("palo_env_file", "virtual_envs/palo/.env")
    return Path(root) / rel


def palo_env_map() -> dict[str, str]:
    path = palo_env_path()
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def cmd_deploy(args) -> None:
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PLUGIN_ROOT / "servers.json", DEPLOY_DIR / "servers.json")
    shutil.copy2(Path(__file__).resolve(), DEPLOY_DIR / "workspace_mcp.py")
    dst_mcp = DEPLOY_DIR / "mcp"
    src_mcp = PLUGIN_ROOT / "mcp"
    if dst_mcp.exists():
        try:
            shutil.rmtree(dst_mcp)
            shutil.copytree(src_mcp, dst_mcp)
        except OSError:
            # Cursor/Claude may lock MCP files — merge copy instead of delete.
            shutil.copytree(src_mcp, dst_mcp, dirs_exist_ok=True)
    else:
        shutil.copytree(src_mcp, dst_mcp)
    print(f"deployed -> {DEPLOY_DIR}")
    if args.cursor_skills:
        src = PLUGIN_ROOT / "skills"
        CURSOR_SKILLS.mkdir(parents=True, exist_ok=True)
        n = 0
        for skill in sorted(p for p in src.iterdir() if p.is_dir() and p.name.startswith(SKILL_PREFIX)):
            dst = CURSOR_SKILLS / skill.name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(skill, dst)
            n += 1
        print(f"copied {n} skills -> {CURSOR_SKILLS}")


def cmd_list(_args) -> None:
    reg = load_registry()
    claude_u = claude_installed("user", None)
    cursor_u = read_json(CURSOR_MCP).get("mcpServers", {})
    codex_u = read_json(CODEX_MCP).get("mcpServers", {})
    print(f"{'server':12} {'local':18} {'risk':8} claude cursor codex")
    for k, s in reg["servers"].items():
        loc = s["local"]
        print(
            f"{k:12} {loc:18} {s['risk']:8} "
            f"{'yes' if loc in claude_u else '-':6} "
            f"{'yes' if loc in cursor_u else '-':6} "
            f"{'yes' if loc in codex_u else '-'}"
        )


def _hosts(h: str) -> list[str]:
    if h == "both":
        return ["claude", "cursor"]
    if h == "all-hosts":
        return ["claude", "cursor", "codex"]
    return [h]


def cmd_install(args, remove: bool = False) -> None:
    reg = load_registry()
    pdir = Path(args.project_dir).resolve() if args.scope == "project" else None
    failures = 0
    for key in resolve_servers(reg, args.servers):
        for host in _hosts(args.host):
            try:
                if host == "claude":
                    fn = claude_uninstall if remove else claude_install
                    print("OK  ", fn(reg, key, args.scope, pdir))
                elif host == "cursor":
                    path = (pdir / ".cursor" / "mcp.json") if args.scope == "project" and pdir else CURSOR_MCP
                    fn = json_host_uninstall if remove else json_host_install
                    print("OK  ", fn(path, reg, key, "cursor"))
                elif host == "codex":
                    fn = json_host_uninstall if remove else json_host_install
                    print("OK  ", fn(CODEX_MCP, reg, key, "codex"))
            except Exception as e:
                failures += 1
                print("FAIL", host, key, "-", e)
    if not remove:
        print(f"\nPalo env file: {palo_env_path()} ({'found' if palo_env_path().is_file() else 'missing'})")
        for key in resolve_servers(reg, args.servers):
            s = reg["servers"][key]
            req = s.get("required_env") or []
            st = _env_present(req)
            print(f"  {key}: " + ", ".join(f"{k}={'set' if st[k] else 'MISSING'}" for k in req))
        print("Restart Claude Code / reload Cursor MCP / restart Codex after install.")
    sys.exit(1 if failures else 0)


def cmd_status(args) -> None:
    reg = load_registry()
    targets = resolve_servers(reg, args.servers) if args.servers else list(reg["servers"])
    report: dict[str, Any] = {"palo_env": str(palo_env_path()), "palo_env_exists": palo_env_path().is_file(), "servers": {}}
    for key in targets:
        s = reg["servers"][key]
        req = list(s.get("required_env") or [])
        opt = list(s.get("optional_env") or [])
        row = {
            "local_name": s["local"],
            "runner": str(runner_js(key)),
            "required_env": _env_present(req),
            "optional_env": _env_present(opt),
            "claude": s["local"] in claude_installed("user", None),
            "cursor": s["local"] in read_json(CURSOR_MCP).get("mcpServers", {}),
            "codex": s["local"] in read_json(CODEX_MCP).get("mcpServers", {}),
        }
        if args.probe:
            node = shutil.which("node") or shutil.which("node.exe")
            row["node"] = bool(node)
            row["runner_exists"] = runner_js(key).is_file()
        report["servers"][key] = row
    print(json.dumps(report, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("deploy")
    p.add_argument("--cursor-skills", action="store_true")
    p.set_defaults(fn=cmd_deploy)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    for name, remove in (("install", False), ("uninstall", True)):
        p = sub.add_parser(name)
        p.add_argument("servers", nargs="+")
        p.add_argument("--host", choices=["claude", "cursor", "codex", "both", "all-hosts"], default="all-hosts")
        p.add_argument("--scope", choices=["user", "project"], default="user")
        p.add_argument("--project-dir")
        p.set_defaults(fn=lambda a, r=remove: cmd_install(a, r))
    p = sub.add_parser("status")
    p.add_argument("servers", nargs="*")
    p.add_argument("--probe", action="store_true")
    p.set_defaults(fn=cmd_status)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
