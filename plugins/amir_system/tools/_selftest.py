"""Self-test runner for the amir tooling (pytest-free): python _selftest.py

Covers: manifest schema accept/reject, every resolver activation-block rule, lockfile
round-trip + drift, renderer dry-run/idempotency/stale-cleanup/fast-path/mcp-merge on a
temporary project, and validator duplicate-command detection.
"""
from __future__ import annotations

import copy
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import catalog as catalog_mod  # noqa: E402
import lockfile  # noqa: E402
import manifest as manifest_mod  # noqa: E402
import portfolio  # noqa: E402
import registry as registry_mod  # noqa: E402
import renderer  # noqa: E402
import validator  # noqa: E402
from util import AmirError, GENERATED_HEADER, GENERATED_MARKER_KEY, default_catalog_root, dump_json, require_yaml, write_text  # noqa: E402

yaml = require_yaml()
REAL_CATALOG_ROOT = default_catalog_root()


# ---------------------------------------------------------------- helpers

def mk_comp(cid: str, plugin: str = "amir_project", **overrides) -> dict:
    component = {
        "id": cid, "plugin": plugin, "version": "1.0.0",
        "scope": "user" if plugin == "amir_system" else "project",
        "description": f"synthetic component {cid}", "official_source": "internal",
        "license": "test", "supported_hosts": ["claude-code", "cursor"],
        "supported_operating_systems": ["windows", "macos", "linux"],
        "installation_mode": "user-plugin" if plugin == "amir_system" else "project-plugin-or-render",
        "dependencies": [], "optional_dependencies": [], "conflicts_with": [],
        "required_executables": [], "required_credentials": [],
        "network_access": "none", "secret_access": "none", "filesystem_access": "project",
        "write_capabilities": [], "destructive_capabilities": [], "resource_requirements": {},
        "health_check": "python --version", "uninstall_method": "deselect",
        "commands": [], "skills": [], "mcp_servers": [],
    }
    component.update(overrides)
    return component


def mk_catalog(*components) -> dict:
    return {"schema_version": 1, "catalog_version": "1.0.0", "generated_at": "2026-07-24",
            "components": list(components)}


HOSTS_BOTH = {"claude-code": {"enabled": True, "version": None},
              "cursor": {"enabled": True, "version": None}}
WHICH_NONE = lambda name: None  # noqa: E731
WHICH_ALL = lambda name: f"C:/fake/{name}.exe"  # noqa: E731


def rules_of(result, rule):
    return [i for i in result.issues if i.rule == rule]


def good_manifest(root: str, components=("fakegrp",)) -> dict:
    return {
        "schema_version": 2,
        "project": {"id": "selftest", "name": "Selftest", "description": "self-test project",
                    "root": root, "created_at": "2026-07-24T00:00:00Z", "onboarded": False},
        "hosts": {"cursor": {"enabled": True}, "claude_code": {"enabled": True}},
        "plugins": {"amir_project": {"enabled": True, "components": list(components)}},
        "system_capabilities": {"asana": {"allowed": False}, "playwright": {"allowed": False}},
        "project_tools": {
            "graphify": {"enabled": False, "output_directory": "graphify-out",
                         "update_policy": "manual", "include": [], "exclude": [],
                         "commit_generated_graph": False},
            "serena": {"enabled": False},
            "context7": {"enabled": False, "mode": "mcp"},
            "semgrep": {"enabled": False, "integration": "mcp",
                        "policy": {"scan_changed_files": True, "scan_before_commit": False,
                                   "block_on": ["critical", "high"], "scan_secrets": True,
                                   "scan_dependencies": False}},
            "langfuse": {"enabled": False, "mode": "disabled"},
            "openhands": {"enabled": False,
                          "sandbox": {"project_mount": "read_write", "home_mount": False,
                                      "privileged": False, "network": "disabled",
                                      "credentials": "none"}},
            "git_worktrees": {"enabled": False},
            "swe_bench": {"enabled": False},
            "terminal_bench": {"enabled": False},
        },
        "permissions": {
            "network": {"default": "deny", "allowed_components": []},
            "secrets": {"default": "deny", "allowed_references": []},
            "destructive_actions": {"require_confirmation": True},
        },
        "documentation": {"enabled": True, "files": {"status": ".ai/status.md"}},
        "generated_artifacts": {"commit_graphify_output": False,
                                "commit_playwright_artifacts": False,
                                "commit_benchmark_results": False},
    }


def make_fake_catalog_root(base: Path, extra_components=()) -> tuple[Path, dict]:
    """A synthetic marketplace checkout with two amir_project groups + one system rule.

    Also writes catalog/catalog.json and copies the real schemas so amirctl's CLI paths
    (which load + schema-validate the catalog) work against this root.
    """
    root = base / "catalog_repo"
    write_text(root / "plugins" / "amir_project" / "commands" / "fakegrp" / "fake_cmd.md",
               "---\ndescription: fake command\n---\n\n# fake_cmd\nbody\n")
    write_text(root / "plugins" / "amir_project" / "commands" / "othergrp" / "other_cmd.md",
               "---\ndescription: other command\n---\n\n# other_cmd\nbody\n")
    write_text(root / "plugins" / "amir_project" / "skills" / "fake_skill" / "SKILL.md",
               "---\nname: fake_skill\n---\nskill body\n")
    write_text(root / "plugins" / "amir_project" / "scripts" / "fakegrp" / "run.py",
               "print('hello')\n")
    write_text(root / "plugins" / "amir_project" / ".claude-plugin" / "plugin.json",
               dump_json({"name": "amir", "version": "0.0.1",
                          "mcpServers": {"fakesrv": {"command": "node", "args": ["x.js"]}}}))
    write_text(root / "plugins" / "amir_system" / "rules" / "test-rule.mdc",
               "---\ndescription: test rule\nalwaysApply: true\n---\nrule body\n")
    cat = mk_catalog(
        mk_comp("fakegrp", commands=["fake_cmd"], skills=["fake_skill"]),
        mk_comp("othergrp", commands=["other_cmd"], mcp_servers=["fakesrv"]),
        *extra_components,
    )
    write_text(root / "catalog" / "catalog.json", dump_json(cat))
    for schema in ("component-metadata.schema.json", "project-manifest.schema.json",
                   "components-lock.schema.json"):
        write_text(root / "schemas" / schema,
                   (REAL_CATALOG_ROOT / "schemas" / schema).read_text(encoding="utf-8"))
    return root, cat


def make_project(base: Path, manifest_data: dict) -> Path:
    project = base / "project"
    write_text(project / ".amir" / "project.yaml",
               yaml.safe_dump(manifest_data, sort_keys=True))
    return project


# ---------------------------------------------------------------- schema tests

def test_manifest_schema_accepts_good():
    data = good_manifest("C:/tmp/selftest")
    errors = manifest_mod.validate_manifest(data, REAL_CATALOG_ROOT)
    assert errors == [], f"good manifest rejected: {errors}"


def test_manifest_schema_rejects_wrong_schema_version():
    data = good_manifest("C:/tmp/selftest")
    data["schema_version"] = 1
    errors = manifest_mod.validate_manifest(data, REAL_CATALOG_ROOT)
    assert errors and any("schema_version" in e for e in errors), errors


def test_manifest_schema_rejects_unknown_top_level_key():
    data = good_manifest("C:/tmp/selftest")
    data["unexpected_key"] = True
    errors = manifest_mod.validate_manifest(data, REAL_CATALOG_ROOT)
    assert errors and any("unexpected_key" in e for e in errors), errors


def test_manifest_schema_rejects_bad_semgrep_severity():
    data = good_manifest("C:/tmp/selftest")
    data["project_tools"]["semgrep"]["policy"]["block_on"] = ["catastrophic"]
    errors = manifest_mod.validate_manifest(data, REAL_CATALOG_ROOT)
    assert errors and any("catastrophic" in e for e in errors), errors


def test_manifest_yaml_error_reports_line():
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        write_text(project / ".amir" / "project.yaml", "schema_version: 2\nproject: [unclosed\n")
        try:
            manifest_mod.load_manifest(project)
            raise AssertionError("expected AmirError for broken YAML")
        except Exception as exc:
            assert "line" in str(exc), str(exc)


# ---------------------------------------------------------------- resolver rules

def test_resolver_clean_pass_and_order():
    cat = mk_catalog(mk_comp("a"), mk_comp("b", dependencies=["a"]))
    result = catalog_mod.resolve(cat, ["b", "a"], HOSTS_BOTH, None, env={}, which=WHICH_ALL,
                                 os_name="windows")
    assert result.ok, result.issues
    assert result.components == ["a", "b"], result.components


def test_resolver_blocks_unknown_component():
    result = catalog_mod.resolve(mk_catalog(mk_comp("a")), ["nope"], HOSTS_BOTH, None,
                                 env={}, which=WHICH_ALL, os_name="windows")
    assert not result.ok and rules_of(result, "unknown-component")


def test_resolver_blocks_missing_dependency_with_chain():
    cat = mk_catalog(mk_comp("a", dependencies=["b"]), mk_comp("b"))
    result = catalog_mod.resolve(cat, ["a"], HOSTS_BOTH, None, env={}, which=WHICH_ALL,
                                 os_name="windows")
    issues = rules_of(result, "missing-dependency")
    assert issues and "a -> b" in issues[0].message, result.issues


def test_resolver_blocks_transitive_missing_dependency():
    cat = mk_catalog(mk_comp("a", dependencies=["b"]), mk_comp("b", dependencies=["c"]), mk_comp("c"))
    result = catalog_mod.resolve(cat, ["a", "b"], HOSTS_BOTH, None, env={}, which=WHICH_ALL,
                                 os_name="windows")
    issues = rules_of(result, "missing-dependency")
    assert issues and any("a -> b -> c" in i.message for i in issues), result.issues


def test_resolver_blocks_missing_executable_dependency():
    cat = mk_catalog(mk_comp("a", dependencies=["git"]))
    result = catalog_mod.resolve(cat, ["a"], HOSTS_BOTH, None, env={}, which=WHICH_NONE,
                                 os_name="windows")
    issues = rules_of(result, "missing-dependency")
    assert issues and "git" in issues[0].message, result.issues


def test_resolver_blocks_missing_required_executable():
    cat = mk_catalog(mk_comp("a", required_executables=["notreal"]))
    result = catalog_mod.resolve(cat, ["a"], HOSTS_BOTH, None, env={}, which=WHICH_NONE,
                                 os_name="windows")
    assert rules_of(result, "missing-executable"), result.issues


def test_resolver_blocks_unsupported_host():
    cat = mk_catalog(mk_comp("a", supported_hosts=["cursor"]))
    result = catalog_mod.resolve(cat, ["a"], HOSTS_BOTH, None, env={}, which=WHICH_ALL,
                                 os_name="windows")
    assert rules_of(result, "unsupported-host"), result.issues


def test_resolver_blocks_unsupported_os():
    cat = mk_catalog(mk_comp("a", supported_operating_systems=["linux"]))
    result = catalog_mod.resolve(cat, ["a"], HOSTS_BOTH, None, env={}, which=WHICH_ALL,
                                 os_name="windows")
    assert rules_of(result, "unsupported-os"), result.issues


def test_resolver_blocks_missing_credential_by_presence_only():
    cat = mk_catalog(mk_comp("a", required_credentials=["FAKE_TOKEN"]))
    blocked = catalog_mod.resolve(cat, ["a"], HOSTS_BOTH, None, env={}, which=WHICH_ALL,
                                  os_name="windows")
    assert rules_of(blocked, "missing-credential"), blocked.issues
    passed = catalog_mod.resolve(cat, ["a"], HOSTS_BOTH, None, env={"FAKE_TOKEN": "x"},
                                 which=WHICH_ALL, os_name="windows")
    assert passed.ok, passed.issues
    assert all("x" not in i.message for i in blocked.issues)  # value never appears


def test_resolver_blocks_rejected_network_permission():
    cat = mk_catalog(mk_comp("a", network_access="required"))
    permissions = {"network": {"default": "deny", "allowed_components": []},
                   "secrets": {"default": "deny", "allowed_references": []}}
    result = catalog_mod.resolve(cat, ["a"], HOSTS_BOTH, permissions, env={}, which=WHICH_ALL,
                                 os_name="windows")
    assert rules_of(result, "permission-rejected"), result.issues
    permissions_ok = {"network": {"default": "deny", "allowed_components": ["a"]},
                      "secrets": {"default": "deny", "allowed_references": []}}
    assert catalog_mod.resolve(cat, ["a"], HOSTS_BOTH, permissions_ok, env={}, which=WHICH_ALL,
                               os_name="windows").ok


def test_resolver_blocks_rejected_secret_permission():
    cat = mk_catalog(mk_comp("a", secret_access="required", required_credentials=["FAKE_TOKEN"]))
    permissions = {"network": {"default": "deny", "allowed_components": []},
                   "secrets": {"default": "deny", "allowed_references": []}}
    result = catalog_mod.resolve(cat, ["a"], HOSTS_BOTH, permissions, env={"FAKE_TOKEN": "x"},
                                 which=WHICH_ALL, os_name="windows")
    assert rules_of(result, "permission-rejected"), result.issues


def test_resolver_blocks_version_incompatibility():
    cat = mk_catalog(mk_comp("a", host_version_constraints={"claude-code": {"min": "9.9.9"}}))
    hosts = {"claude-code": {"enabled": True, "version": "1.0.0"},
             "cursor": {"enabled": False, "version": None}}
    result = catalog_mod.resolve(cat, ["a"], hosts, None, env={}, which=WHICH_ALL,
                                 os_name="windows")
    assert rules_of(result, "version-incompatible"), result.issues


def test_resolver_blocks_conflicts():
    cat = mk_catalog(mk_comp("a", conflicts_with=["b"]), mk_comp("b"))
    result = catalog_mod.resolve(cat, ["a", "b"], HOSTS_BOTH, None, env={}, which=WHICH_ALL,
                                 os_name="windows")
    assert rules_of(result, "conflict"), result.issues


def test_resolver_blocks_circular_dependencies():
    cat = mk_catalog(mk_comp("a", dependencies=["b"]), mk_comp("b", dependencies=["a"]))
    result = catalog_mod.resolve(cat, ["a", "b"], HOSTS_BOTH, None, env={}, which=WHICH_ALL,
                                 os_name="windows")
    assert rules_of(result, "circular-dependency"), result.issues


def test_resolver_real_catalog_swebench_needs_docker_group():
    cat = catalog_mod.load_catalog(REAL_CATALOG_ROOT)
    result = catalog_mod.resolve(cat, ["swebench"], HOSTS_BOTH, None, env={}, which=WHICH_ALL,
                                 os_name="windows")
    issues = rules_of(result, "missing-dependency")
    assert issues and "docker" in issues[0].message, result.issues


# ---------------------------------------------------------------- selection mapping

def test_selected_component_ids_mapping():
    data = good_manifest("C:/tmp/x", components=("harness",))
    data["project_tools"]["git_worktrees"]["enabled"] = True
    data["project_tools"]["swe_bench"]["enabled"] = True
    data["system_capabilities"]["asana"]["allowed"] = True
    selected = manifest_mod.selected_component_ids(data)
    assert selected == ["asana", "harness", "swebench", "worktrees"], selected


# ---------------------------------------------------------------- lockfile

def test_lockfile_roundtrip_and_drift():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        root, cat = make_fake_catalog_root(base)
        lock = lockfile.build_lock(root, cat, ["fakegrp"])
        assert set(lock["components"]) == {"fakegrp"}
        files = lock["components"]["fakegrp"]["files"]
        assert len(files) == 3, files  # command + skill + script
        assert lockfile.validate_lock(lock, REAL_CATALOG_ROOT) == []
        assert lockfile.verify_lock(root, cat, lock) == {}
        cmd = root / "plugins" / "amir_project" / "commands" / "fakegrp" / "fake_cmd.md"
        cmd.write_text(cmd.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
        (root / "plugins" / "amir_project" / "scripts" / "fakegrp" / "run.py").unlink()
        write_text(root / "plugins" / "amir_project" / "scripts" / "fakegrp" / "new.txt", "x\n")
        drift = lockfile.verify_lock(root, cat, lock)
        assert len(drift["fakegrp"]["changed"]) == 1
        assert len(drift["fakegrp"]["missing"]) == 1
        assert len(drift["fakegrp"]["added"]) == 1


# ---------------------------------------------------------------- renderer

def _snapshot(project: Path) -> dict:
    return {p.relative_to(project).as_posix(): p.read_bytes()
            for p in sorted(project.rglob("*")) if p.is_file()}


def test_renderer_dry_run_writes_nothing():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        root, cat = make_fake_catalog_root(base)
        project = make_project(base, good_manifest(str(base / "project")))
        before = _snapshot(project)
        plan, actions = renderer.render(project, good_manifest(str(project)), cat, root,
                                        dry_run=True)
        assert any(a.op == "create" for a in actions), actions
        assert _snapshot(project) == before, "dry-run must not write anything"


def test_renderer_apply_idempotent_and_stale_cleanup():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        root, cat = make_fake_catalog_root(base)
        data = good_manifest(str(base / "project"))
        project = make_project(base, data)
        # pre-existing user + stale amir mcp entries must be merged correctly
        write_text(project / ".cursor" / "mcp.json", dump_json({"mcpServers": {
            "user-server": {"command": "foo"},
            "stale-amir": {"command": "bar", GENERATED_MARKER_KEY: "old"}}}))
        plan, actions = renderer.render(project, data, cat, root, dry_run=False)
        cursor_cmd = project / ".cursor" / "commands" / "amir_fake_cmd.md"
        assert cursor_cmd.is_file()
        text = cursor_cmd.read_text(encoding="utf-8")
        assert GENERATED_HEADER in text and text.startswith("---"), "header must not break frontmatter"
        market = project / ".amir" / "generated" / "claude" / "marketplace"
        assert (market / ".claude-plugin" / "marketplace.json").is_file()
        assert "amir-project-selftest" in (market / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        assert (project / ".cursor" / "rules" / "amir_test_rule.mdc").is_file()
        mcp = (project / ".cursor" / "mcp.json").read_text(encoding="utf-8")
        assert "user-server" in mcp and "stale-amir" not in mcp
        first = _snapshot(project)
        plan2, actions2 = renderer.render(project, data, cat, root, dry_run=False)
        assert all(a.op == "keep" for a in actions2), [a for a in actions2 if a.op != "keep"]
        assert _snapshot(project) == first, "re-render must be byte-identical"
        # switch selection -> old files removed, new files created, mcp entry added
        data2 = copy.deepcopy(data)
        data2["plugins"]["amir_project"]["components"] = ["othergrp"]
        renderer.render(project, data2, cat, root, dry_run=False)
        assert not cursor_cmd.exists(), "stale generated cursor command must be deleted"
        assert (project / ".cursor" / "commands" / "amir_other_cmd.md").is_file()
        mcp2 = (project / ".cursor" / "mcp.json").read_text(encoding="utf-8")
        assert "fakesrv" in mcp2 and "user-server" in mcp2


def test_renderer_full_selection_fast_path():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        root, cat = make_fake_catalog_root(base)
        data = good_manifest(str(base / "project"), components=("fakegrp", "othergrp"))
        project = make_project(base, data)
        plan, _actions = renderer.render(project, data, cat, root, dry_run=False)
        assert plan.fast_path
        marker = project / ".amir" / "generated" / "claude" / renderer.FAST_PATH_MARKER
        assert marker.is_file()
        assert "claude plugin install amir_project@amir-marketplace" in marker.read_text(encoding="utf-8")
        assert not (project / ".amir" / "generated" / "claude" / "marketplace").exists()


# ---------------------------------------------------------------- CLI gating (amirctl)

def run_cli(argv) -> tuple[int, str, str]:
    import contextlib
    import io

    import amirctl  # noqa: PLC0415

    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = amirctl.main(argv)
    return rc, out.getvalue(), err.getvalue()


def test_cli_generate_refuses_blocked_selection_no_writes():
    """DEFECT 1: generate must run the resolver on the effective selection and refuse."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        blocked = mk_comp("blockedgrp", required_executables=["amir_selftest_missing_exe"])
        root, _cat = make_fake_catalog_root(base, extra_components=(blocked,))
        data = good_manifest(str(base / "project"), components=("blockedgrp",))
        project = make_project(base, data)
        rc, _out, err = run_cli(["--project", str(project), "--catalog", str(root), "generate"])
        assert rc != 0, "generate must refuse a blocked selection"
        assert "BLOCKED [missing-executable]" in err, err
        assert "no files written" in err, err
        assert not (project / ".cursor").exists(), "no partial writes on refusal"
        assert not (project / ".amir" / "generated").exists()


def test_cli_generate_dry_run_shows_blocks():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        blocked = mk_comp("blockedgrp", required_executables=["amir_selftest_missing_exe"])
        root, _cat = make_fake_catalog_root(base, extra_components=(blocked,))
        project = make_project(base, good_manifest(str(base / "project"), components=("blockedgrp",)))
        rc, _out, err = run_cli(["--project", str(project), "--catalog", str(root),
                                 "generate", "--dry-run"])
        assert rc != 0 and "BLOCKED [missing-executable]" in err, (rc, err)


def test_cli_generate_gates_project_tools_mapped_components():
    """DEFECT 1: project_tools-enabled components (e.g. serena) go through the resolver too."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        serena = mk_comp("serena", required_executables=["amir_selftest_missing_uv"])
        root, _cat = make_fake_catalog_root(base, extra_components=(serena,))
        data = good_manifest(str(base / "project"), components=())
        data["project_tools"]["serena"]["enabled"] = True
        project = make_project(base, data)
        rc, _out, err = run_cli(["--project", str(project), "--catalog", str(root), "generate"])
        assert rc != 0, "project_tools-mapped component must be resolution-gated"
        assert "'serena'" in err and "BLOCKED [missing-executable]" in err, err


def test_cli_generate_gates_denied_network_permission():
    """DEFECT 1: manifest permissions are the granted-permissions input to the resolver."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        netgrp = mk_comp("netgrp", network_access="required")
        root, _cat = make_fake_catalog_root(base, extra_components=(netgrp,))
        data = good_manifest(str(base / "project"), components=("netgrp",))
        project = make_project(base, data)
        rc, _out, err = run_cli(["--project", str(project), "--catalog", str(root), "generate"])
        assert rc != 0 and "BLOCKED [permission-rejected]" in err, (rc, err)
        # granting network to the component unblocks it
        data["permissions"]["network"]["allowed_components"] = ["netgrp"]
        make_project(base, data)
        rc2, out2, _err2 = run_cli(["--project", str(project), "--catalog", str(root), "generate"])
        assert rc2 == 0, out2


def test_cli_generate_and_lock_refuse_invalid_manifest():
    """DEFECT 2: generate/lock validate the manifest schema first and refuse without writing."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        root, _cat = make_fake_catalog_root(base)
        data = good_manifest(str(base / "project"))
        data["unknown_toplevel_key"] = True
        project = make_project(base, data)
        for command in (["generate"], ["generate", "--dry-run"], ["lock"], ["repair"]):
            rc, _out, err = run_cli(["--project", str(project), "--catalog", str(root), *command])
            assert rc != 0, f"{command} must refuse an invalid manifest"
            assert "manifest failed schema validation" in err, (command, err)
        assert not (project / ".cursor").exists()
        assert not (project / ".amir" / "components.lock.json").exists()


def test_cli_validate_exits_nonzero_on_error():
    """DEFECT 2 regression guard: any ERROR row must make validate exit nonzero."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        root, _cat = make_fake_catalog_root(base)
        data = good_manifest(str(base / "project"))
        data["unknown_toplevel_key"] = True
        project = make_project(base, data)
        rc, out, _err = run_cli(["--project", str(project), "--catalog", str(root), "validate"])
        assert rc != 0 and "ERROR" in out, (rc, out)


def test_cli_generate_hints_missing_lock_then_quiet():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        root, _cat = make_fake_catalog_root(base)
        project = make_project(base, good_manifest(str(base / "project")))
        args = ["--project", str(project), "--catalog", str(root)]
        rc, out, _err = run_cli([*args, "generate"])
        assert rc == 0 and "hint:" in out and "amirctl lock" in out, out
        rc_lock, _out, _err = run_cli([*args, "lock"])
        assert rc_lock == 0
        rc2, out2, _err = run_cli([*args, "generate"])
        assert rc2 == 0 and "hint:" not in out2, out2


# ---------------------------------------------------------------- validator

def test_validator_detects_duplicate_commands():
    cat = mk_catalog(mk_comp("a", commands=["foo", "bar"]), mk_comp("b", commands=["foo"]))
    duplicates = validator.find_duplicate_commands(cat)
    assert duplicates == {"foo": ["a", "b"]}, duplicates


def test_validator_real_catalog_has_no_duplicates():
    cat = catalog_mod.load_catalog(REAL_CATALOG_ROOT)
    assert validator.find_duplicate_commands(cat) == {}


# ---------------------------------------------------------------- registry (unified YAML)

def mk_local_graph(node_ids, edges=()) -> dict:
    return {"directed": False, "multigraph": False, "graph": {},
            "nodes": [{"id": nid, "label": nid} for nid in node_ids],
            "links": [{"source": a, "target": b, "relation": "uses"} for a, b in edges],
            "hyperedges": []}


def make_portfolio_project(base: Path, pid: str, folder: str | None = None,
                           graph_nodes=None, graph_edges=(), graphify: bool = True) -> Path:
    project = base / (folder or pid)
    data = copy.deepcopy(good_manifest(str(project)))
    data["project"].update({"id": pid, "name": pid, "root": str(project)})
    data["plugins"]["amir_project"]["components"] = []
    data["project_tools"]["graphify"]["enabled"] = graphify
    write_text(project / ".amir" / "project.yaml", yaml.safe_dump(data, sort_keys=True,
                                                                 allow_unicode=True))
    for fname in ("project.md", "status.md", "risks.md"):
        write_text(project / ".ai" / fname, f"# {fname}\ncontent for {pid}\n")
    if graph_nodes is not None:
        write_text(project / "graphify-out" / "graph.json",
                   dump_json(mk_local_graph(graph_nodes, graph_edges)))
    return project


PORTFOLIO_YAML = """schema_version: 1
project:
  id: {pid}
  name: {pid}
  lifecycle: active
  priority: high
  health: at-risk
progress:
  confirmed_percent: 40
  estimated_percent: 60
  current_phase: phase-2
references:
  asana:
    enabled: true
    project_gid: "12345"
technology:
  languages: [python]
"""


def test_registry_yaml_roundtrip_and_null_honesty():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        project = make_portfolio_project(base, "rt-proj", graph_nodes=["n1"])
        entry = registry_mod.entry_from_sources(project)
        # no portfolio.yaml -> progress/lifecycle stay null, health defaults to unknown
        assert entry["lifecycle"] is None and entry["confirmed_progress"] is None
        assert entry["health"] == "unknown" and entry["last_status_update"] is not None
        assert entry["graph_enabled"] is True and entry["last_graph_update"] is None
        registry_mod.save_registry(registry_mod.upsert_project(
            registry_mod.load_registry(home), entry), home)
        loaded = registry_mod.load_registry(home)
        assert loaded["schema_version"] == 2 and loaded["projects"] == [entry], loaded
        assert registry_mod.registry_path(home).name == "projects.yaml"
        # with portfolio.yaml -> fields populate from the source, still schema-valid
        write_text(project / ".amir" / "portfolio.yaml", PORTFOLIO_YAML.format(pid="rt-proj"))
        entry2 = registry_mod.entry_from_sources(project)
        assert (entry2["lifecycle"], entry2["priority"], entry2["health"]) == \
            ("active", "high", "at-risk")
        assert (entry2["confirmed_progress"], entry2["estimated_progress"]) == (40, 60)
        assert entry2["current_phase"] == "phase-2" and entry2["asana_reference"] == "12345"
        registry = registry_mod.upsert_project(loaded, entry2)
        assert registry_mod.validate_registry_data(registry, REAL_CATALOG_ROOT) == []


def test_registry_migrates_legacy_json():
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "home"
        legacy = {"schema_version": 1, "projects": [{
            "id": "oldproj", "name": "Old", "root": "C:/nowhere/oldproj",
            "type": "created", "cursor_enabled": True, "claude_enabled": True,
            "last_validation": None, "last_opened": "2026-01-01T00:00:00Z",
            "manifest_path": "C:/nowhere/oldproj/.amir/project.yaml",
            "enabled_component_ids": ["harness"]}]}
        write_text(registry_mod.legacy_registry_path(home), dump_json(legacy))
        loaded = registry_mod.load_registry(home)
        assert [p["id"] for p in loaded["projects"]] == ["oldproj"]
        entry = loaded["projects"][0]
        assert entry["claude_code_enabled"] is True and entry["cursor_enabled"] is True
        assert entry["manifest"] == "C:/nowhere/oldproj/.amir/project.yaml"
        assert entry["confirmed_progress"] is None  # nothing fabricated
        assert registry_mod.registry_path(home).is_file()
        assert not registry_mod.legacy_registry_path(home).exists()
        migrated = registry_mod.legacy_registry_path(home).with_name("projects.json.migrated")
        assert migrated.is_file(), "legacy file must be kept with .migrated suffix"


def test_registry_refuses_duplicate_ids():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        p1 = make_portfolio_project(base, "dupe-id", folder="first")
        p2 = make_portfolio_project(base, "dupe-id", folder="second")
        registry = registry_mod.upsert_project(
            {"schema_version": 2, "projects": []}, registry_mod.entry_from_sources(p1))
        try:
            registry_mod.upsert_project(registry, registry_mod.entry_from_sources(p2))
            raise AssertionError("duplicate id at a different root must be refused")
        except AmirError as exc:
            assert "duplicate project id" in str(exc)
        # same id at the SAME root is a refresh, not a duplicate
        registry2 = registry_mod.upsert_project(registry, registry_mod.entry_from_sources(p1))
        assert len(registry2["projects"]) == 1


def test_registry_history_snapshot_per_mutation():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        project = make_portfolio_project(base, "hist-proj")
        entry = registry_mod.entry_from_sources(project)
        registry_mod.save_registry(registry_mod.upsert_project(
            registry_mod.load_registry(home), entry), home)
        registry_mod.save_registry(registry_mod.remove_project(
            registry_mod.load_registry(home), "hist-proj"), home)
        snapshots = list(registry_mod.history_dir(home).glob("*-projects.yaml"))
        assert len(snapshots) == 2, snapshots


def test_registry_lock_blocks_concurrent_save():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        project = make_portfolio_project(base, "lock-proj")
        entry = registry_mod.entry_from_sources(project)
        registry = registry_mod.upsert_project(registry_mod.load_registry(home), entry)
        lock = registry_mod.lock_path(home)
        write_text(lock, "{}")
        try:
            registry_mod.save_registry(registry, home)
            raise AssertionError("save must refuse while a fresh lock is held")
        except AmirError as exc:
            assert "locked" in str(exc)
        import os as _os
        stale = 1000 + registry_mod.LOCK_STALE_SECONDS
        _os.utime(lock, (lock.stat().st_atime - stale, lock.stat().st_mtime - stale))
        registry_mod.save_registry(registry, home)  # stale lock is broken and taken over
        assert registry_mod.registry_path(home).is_file()


# ---------------------------------------------------------------- portfolio engine

def _global_node_ids(home: Path) -> list[str]:
    return sorted(str(n["id"]) for n in portfolio.load_global(home)["nodes"])


def test_portfolio_add_idempotent_single_namespace():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        project = make_portfolio_project(base, "p1", graph_nodes=["a", "b"],
                                         graph_edges=[("a", "b")])
        first = portfolio.add(project, home)
        assert first["graph_merged"] and first["node_count"] == 2
        second = portfolio.add(project, home)  # re-add replaces the namespace, no dupes
        assert second["graph_merged"] and second["node_count"] == 2
        assert _global_node_ids(home) == ["p1::a", "p1::b"]
        graph = portfolio.load_global(home)
        assert len(graph["links"]) == 1
        assert (graph["links"][0]["source"], graph["links"][0]["target"]) == ("p1::a", "p1::b")
        metadata = portfolio.load_metadata(home)
        assert list(metadata["projects"]) == ["p1"]
        assert metadata["projects"]["p1"]["node_count"] == 2
        entry = registry_mod.find_entry(registry_mod.load_registry(home), "p1")
        assert entry["last_graph_update"] is not None


def test_portfolio_add_without_graph_is_honest():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        enabled = make_portfolio_project(base, "nograph", graph_nodes=None, graphify=True)
        report = portfolio.add(enabled, home)
        assert report["registered"] and not report["graph_merged"]
        assert "no local graph" in report["reason"], report
        disabled = make_portfolio_project(base, "gfy-off", graphify=False)
        report2 = portfolio.add(disabled, home)
        assert not report2["graph_merged"] and "not enabled" in report2["reason"]
        assert _global_node_ids(home) == []
        assert len(registry_mod.load_registry(home)["projects"]) == 2


def test_portfolio_namespace_collision_prevention():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        portfolio.add(make_portfolio_project(base, "p1", graph_nodes=["shared"]), home)
        portfolio.add(make_portfolio_project(base, "p2", graph_nodes=["shared"]), home)
        assert _global_node_ids(home) == ["p1::shared", "p2::shared"]
        codes = [i["code"] for i in portfolio.validate(home, REAL_CATALOG_ROOT)]
        assert "duplicate-node" not in codes, codes


def test_portfolio_remove_preserves_files_and_other_namespaces():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        p1 = make_portfolio_project(base, "p1", graph_nodes=["a"])
        p2 = make_portfolio_project(base, "p2", graph_nodes=["x", "y"])
        portfolio.add(p1, home)
        portfolio.add(p2, home)
        report = portfolio.remove("p2", home)
        assert report["graph_removed"] and report["registry_removed"]
        assert (p2 / ".amir" / "project.yaml").is_file(), "project sources must be untouched"
        assert (p2 / "graphify-out" / "graph.json").is_file(), "local graph preserved by default"
        assert _global_node_ids(home) == ["p1::a"], "other namespaces must survive"
        assert [p["id"] for p in registry_mod.load_registry(home)["projects"]] == ["p1"]
        archived = list(registry_mod.history_dir(home).glob("removed-p2-*.yaml"))
        assert archived, "removed entry must be archived to project-history"
        report2 = portfolio.remove("p1", home, remove_local_graph=True)
        assert report2["local_graph_removed"]
        assert not (p1 / "graphify-out" / "graph.json").exists()
        assert (p1 / ".amir" / "project.yaml").is_file()


def _set_mtime(path: Path, epoch: float) -> None:
    import os as _os
    _os.utime(path, (epoch, epoch))


def _forbidden_runner(_root):
    raise AssertionError("graphify runner must not be invoked when the graph is fresh")


def test_portfolio_update_distinguishes_metadata_vs_graph():
    import time
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        project = make_portfolio_project(base, "p1", graph_nodes=["a"])
        now = time.time()
        for path in project.rglob("*"):
            if path.is_file():
                _set_mtime(path, now - 100)
        _set_mtime(project / "graphify-out" / "graph.json", now - 50)
        portfolio.add(project, home)
        fresh_report = portfolio.update("p1", home, graphify_runner=_forbidden_runner)
        assert fresh_report["status"] == "no-change" and not fresh_report["graph_refreshed"]
        # metadata-only change: portfolio.yaml appears, but graph stays fresh
        write_text(project / ".amir" / "portfolio.yaml", PORTFOLIO_YAML.format(pid="p1"))
        _set_mtime(project / ".amir" / "portfolio.yaml", now - 90)
        meta_report = portfolio.update("p1", home, graphify_runner=_forbidden_runner)
        assert meta_report["status"] == "metadata-refreshed", meta_report
        assert meta_report["registry_refreshed"] and not meta_report["graph_refreshed"]
        assert "lifecycle" in meta_report["registry_changes"]
        # source newer than graph -> stale -> runner regenerates -> graph refresh reported
        write_text(project / "newfile.py", "print('hi')\n")
        def fake_runner(root):
            write_text(Path(root) / "graphify-out" / "graph.json",
                       dump_json(mk_local_graph(["a", "b", "c"])))
            return True, "regenerated"
        graph_report = portfolio.update("p1", home, graphify_runner=fake_runner)
        assert graph_report["status"] == "graph-refreshed", graph_report
        assert graph_report["graph_refreshed"]
        assert graph_report["graph_stale_reason"] == "source-newer"
        assert _global_node_ids(home) == ["p1::a", "p1::b", "p1::c"]
        # failed regeneration keeps the previous global graph
        write_text(project / "newer.py", "x = 1\n")
        fail_report = portfolio.update("p1", home,
                                       graphify_runner=lambda root: (False, "boom"))
        assert fail_report["status"] == "error" and "boom" in fail_report["error"]
        assert _global_node_ids(home) == ["p1::a", "p1::b", "p1::c"], \
            "failed update must retain the previous valid global graph"


def test_portfolio_update_all_partial_failure_and_lock():
    import shutil as _shutil
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        portfolio.add(make_portfolio_project(base, "p1", graph_nodes=["a"]), home)
        p2 = make_portfolio_project(base, "p2", graph_nodes=["x"])
        portfolio.add(p2, home)
        _shutil.rmtree(p2)
        result = portfolio.update_all(home, graphify_runner=lambda root: (False, "unavailable"))
        assert result["status"] == "partial", result
        assert result["failed"] == 1 and result["total"] == 2
        errors = [r for r in result["results"] if r["status"] == "error"]
        assert errors and "root missing" in errors[0]["error"]
        # a fresh portfolio lock blocks a concurrent update_all
        write_text(portfolio.portfolio_lock_path(home), "{}")
        try:
            portfolio.update_all(home)
            raise AssertionError("update_all must refuse while the portfolio lock is held")
        except AmirError as exc:
            assert "locked" in str(exc)
        lock = portfolio.portfolio_lock_path(home)
        stale = 1000 + portfolio.PORTFOLIO_LOCK_STALE_SECONDS
        _set_mtime(lock, lock.stat().st_mtime - stale)
        result2 = portfolio.update_all(home, graphify_runner=lambda root: (False, "unavailable"))
        assert result2["status"] == "partial"  # stale lock broken; run proceeds
        assert not lock.exists(), "lock must be released afterwards"


def test_portfolio_stale_detection_mtime():
    import time
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        project = make_portfolio_project(base, "p1", graph_nodes=["a"])
        graph = project / "graphify-out" / "graph.json"
        now = time.time()
        for path in project.rglob("*"):
            if path.is_file():
                _set_mtime(path, now - 100)
        _set_mtime(graph, now - 50)
        assert portfolio.graph_staleness(project, graph, None) == (False, None)
        _set_mtime(project / "code.py" if (project / "code.py").is_file()
                   else project / ".ai" / "status.md", now - 10)
        assert portfolio.graph_staleness(project, graph, None) == (True, "source-newer")
        assert portfolio.graph_staleness(project, project / "graphify-out" / "missing.json",
                                         None) == (True, "missing")


def test_portfolio_secret_scan_flags_planted_token():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        fake_token = "ghp_" + "a" * 36  # planted, synthetic
        project = make_portfolio_project(base, "p1", graph_nodes=["safe"])
        write_text(project / "graphify-out" / "graph.json",
                   dump_json(mk_local_graph(["safe", f"leaky {fake_token}"])))
        portfolio.add(project, home)
        issues = portfolio.validate(home, REAL_CATALOG_ROOT)
        leaks = [i for i in issues if i["code"] == "secret-leak"]
        assert leaks, f"planted token must be flagged: {issues}"
        assert all(fake_token not in i["message"] for i in leaks), \
            "the secret value itself must never be echoed"
        # global graph still intact (scan is report-only)
        assert len(portfolio.load_global(home)["nodes"]) == 2


def test_portfolio_validate_detects_graph_inconsistencies():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        portfolio.add(make_portfolio_project(base, "p1", graph_nodes=["a", "b"]), home)
        metadata = portfolio.load_metadata(home)
        metadata["projects"]["p1"]["node_count"] = 99  # tamper
        write_text(portfolio.metadata_path(home), dump_json(metadata))
        graph = portfolio.load_global(home)
        graph["nodes"].append({"id": "ghost::x", "label": "orphan"})
        write_text(portfolio.global_graph_path(home), dump_json(graph))
        codes = [i["code"] for i in portfolio.validate(home, REAL_CATALOG_ROOT)]
        assert "namespace-count-mismatch" in codes, codes
        assert "orphaned-namespace" in codes, codes


def test_portfolio_rebuild_and_backups():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        p1 = make_portfolio_project(base, "p1", graph_nodes=["a"])
        portfolio.add(p1, home)
        portfolio.add(make_portfolio_project(base, "p2", graph_nodes=["x", "y"]), home)
        write_text(portfolio.global_graph_path(home), dump_json(portfolio.empty_graph()))
        result = portfolio.rebuild(home)
        assert result["node_count"] == 3 and result["edge_count"] == 0
        assert _global_node_ids(home) == ["p1::a", "p2::x", "p2::y"]
        assert sorted(portfolio.load_metadata(home)["projects"]) == ["p1", "p2"]
        for _ in range(7):  # backup rotation caps at BACKUP_KEEP
            portfolio.add(p1, home)
        backups = list(portfolio.backups_dir(home).glob("global-graph-*.json"))
        assert len(backups) <= portfolio.BACKUP_KEEP, backups


def test_portfolio_unicode_and_spaces_in_path():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        home = base / "home"
        project = make_portfolio_project(base, "unicode-proj", folder="pröj  spåce dir",
                                         graph_nodes=["nöde one", "n2"],
                                         graph_edges=[("nöde one", "n2")])
        report = portfolio.add(project, home)
        assert report["graph_merged"] and report["node_count"] == 2
        assert "unicode-proj::nöde one" in _global_node_ids(home)
        entry = registry_mod.find_entry(registry_mod.load_registry(home), "unicode-proj")
        assert "pröj  spåce dir" in entry["root"]
        update_report = portfolio.update(str(project), home,
                                         graphify_runner=lambda root: (False, "off"))
        assert update_report["status"] in ("no-change", "metadata-refreshed", "graph-refreshed")
        remove_report = portfolio.remove("unicode-proj", home)
        assert remove_report["graph_removed"]
        assert _global_node_ids(home) == []


# ---------------------------------------------------------------- runner

def main() -> int:
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    passed, failed = 0, 0
    for name, fn in tests:
        try:
            fn()
        except Exception:
            failed += 1
            print(f"FAIL {name}")
            traceback.print_exc()
        else:
            passed += 1
            print(f"PASS {name}")
    print(f"\n{passed + failed} tests: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
