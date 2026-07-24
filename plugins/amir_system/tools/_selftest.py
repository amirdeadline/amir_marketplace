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
import renderer  # noqa: E402
import validator  # noqa: E402
from util import GENERATED_HEADER, GENERATED_MARKER_KEY, default_catalog_root, dump_json, require_yaml, write_text  # noqa: E402

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
        "documentation": {"enabled": True, "files": {"status": "ai/status.md"}},
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
