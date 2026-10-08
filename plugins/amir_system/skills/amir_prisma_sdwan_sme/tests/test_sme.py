"""Tests for scripts/sme.py and scripts/sync_knowledge.py. Run: python -m pytest -q -p no:cacheprovider tests"""
import json
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import sme  # noqa: E402
import sync_knowledge  # noqa: E402


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture()
def research(tmp_path: Path) -> Path:
    root = tmp_path / "research"
    _write(root / "notes/02-network/08-routing.md", "\n".join([
        "# Routing: branch and data center models",
        "",
        "Domain: 2 | Applies to: Admin Guide May 2025 | Status: EVIDENCE REVIEWED",
        "",
        "## Explanation (plain words)",
        "The controller distributes Global prefixes as WAN paths.",
        "",
        "## Claims register",
        "| Claim | Label | Evidence | Source pointer |",
        "|---|---|---|---|",
        "| Branch peers are classic only | VERIFIED | DOC | SRC-000029 pp.370–371 |",
        "| /25 injection with no-advertise | UNVERIFIED (internal) | DOC | SRC-000091 |",
        "",
        "## Open questions",
        "- KG-079: official statement of the /25 injection.",
    ]))
    _write(root / "notes/04-security/01-zbfw.md", "# ZBFW and stacked security policies\n\nDomain: 4\n\nUnbound zone drops traffic.\n")
    _write(root / "scenarios/00_SCENARIO_INDEX.md", "# Scenario index\n| S09 | HA pair never fails over | 2, 8 |\n")
    _write(root / "scenarios/S09-ha-pair-never-fails-over.md", "# S09 — HA pair never fails over\n\nDirect cable is forbidden.\n")
    _write(root / "index/00_NOTE_INDEX.md", "# Index\n| Note | Scope |\n|---|---|\n| 02-network/08 | routing |\n")
    _write(root / "index/01_TERM_INDEX.md", "# Term index\n| Term | Notes |\n|---|---|\n| BGP peer types (classic / core / edge) | 02-network/08 |\n| Security zone, ZBFW | 04-security/01 |\n")
    _write(root / "index/02_ROUTER.md", "# Router\n| Intent | Open first | Then | Primary sources | Label ceiling today |\n|---|---|---|---|---|\n| Routing (BGP, asymmetry) | 02-network/08 | 10-design/01 | SRC-000029 | VERIFIED |\n| HA | 02-network/07 | — | SRC-000029 | VERIFIED |\n")
    _write(root / "03_SOURCE_CATALOG.md", "# Catalog\n| ID | Title | Rank |\n|---|---|---|\n| SRC-000029 | Prisma SD-WAN Administrator's Guide | 1 |\n")
    _write(root / "04_KNOWLEDGE_GAPS.md", "# Gaps\n| KG-079 | 2 / 02-network/08 | /25 injection official statement | read | PARTIAL |\n")
    _write(root / "05_UNRESOLVED_QUESTIONS.md", "# Questions\n| C13 | Branch gateway limits | KG-077, KG-136 |\n")
    _write(root / "06_SME_READINESS_ASSESSMENT.md", "# Readiness\nOverall R3.\n")
    return root


@pytest.fixture()
def knowledge(research: Path, tmp_path: Path) -> Path:
    target = tmp_path / "knowledge"
    assert sync_knowledge.sync(research, target, check_only=False) == 0
    return target


def test_sync_writes_manifest_with_hashes(knowledge: Path):
    meta = json.loads((knowledge / "MANIFEST.json").read_text(encoding="utf-8"))
    paths = {item["path"] for item in meta["files"]}
    assert "notes/02-network/08-routing.md" in paths
    assert "03_SOURCE_CATALOG.md" in paths
    assert meta["file_count"] == len(paths) == 11
    assert all(len(item["sha256"]) == 64 for item in meta["files"])


def test_sync_check_reports_drift_without_writing(research: Path, knowledge: Path):
    (research / "notes/02-network/08-routing.md").write_text("# Routing changed\n", encoding="utf-8")
    assert sync_knowledge.sync(research, knowledge, check_only=True) == 1
    assert "Routing: branch" in (knowledge / "notes/02-network/08-routing.md").read_text(encoding="utf-8")


def test_sync_removes_stale_target_files(research: Path, knowledge: Path):
    _write(knowledge / "notes/99-old.md", "# old\n")
    assert sync_knowledge.sync(research, knowledge, check_only=False) == 0
    assert not (knowledge / "notes/99-old.md").exists()


def test_verify_passes_then_detects_change(knowledge: Path, capsys):
    assert sme.cmd_verify(knowledge) == 0
    (knowledge / "notes/04-security/01-zbfw.md").write_text("# tampered\n", encoding="utf-8")
    assert sme.cmd_verify(knowledge) == 1
    assert "CHANGED  notes/04-security/01-zbfw.md" in capsys.readouterr().out


def test_resolve_knowledge_requires_index(tmp_path: Path):
    with pytest.raises(sme.KnowledgeNotFound):
        sme.resolve_knowledge(str(tmp_path))


def test_route_matches_all_words(knowledge: Path, capsys):
    assert sme.cmd_route(knowledge, ["routing", "asymmetry"]) == 0
    out = capsys.readouterr().out
    assert "02-network/08" in out and "| HA |" not in out
    assert sme.cmd_route(knowledge, ["nonexistent"]) == 1


def test_find_ranks_titles_first_and_limits(knowledge: Path, capsys):
    assert sme.cmd_find(knowledge, ["routing"], limit=2) == 0
    out = capsys.readouterr().out
    assert out.index("Title matches") < out.index("Line matches")
    assert "truncated" in out
    assert sme.cmd_find(knowledge, ["zzz"], limit=5) == 1


def test_note_resolution_and_section(knowledge: Path, capsys):
    assert sme.cmd_note(knowledge, "02-network/08", "Claims register") == 0
    out = capsys.readouterr().out
    assert "| Branch peers are classic only | VERIFIED" in out and "Explanation" not in out
    assert sme.cmd_note(knowledge, "does-not-exist", None) == 1
    assert sme.cmd_note(knowledge, "0", None) == 1  # ambiguous fragment lists candidates
    assert "notes match" in capsys.readouterr().out


def test_scenario_and_term_and_gap(knowledge: Path, capsys):
    assert sme.cmd_scenario(knowledge, "s09") == 0
    assert "Direct cable" in capsys.readouterr().out
    assert sme.cmd_scenario(knowledge, "S99") == 1
    assert sme.cmd_term(knowledge, ["zbfw"]) == 0
    assert "04-security/01" in capsys.readouterr().out
    assert sme.cmd_gap(knowledge, "kg-079") == 0
    out = capsys.readouterr().out
    assert "04_KNOWLEDGE_GAPS.md:2" in out and "notes/02-network/08-routing.md" in out
    assert sme.cmd_gap(knowledge, "KG-999") == 1
    assert sme.cmd_gap(knowledge, "bad") == 1


def test_src_catalog_only(knowledge: Path, capsys):
    assert sme.cmd_src(knowledge, {}, ["SRC-000029"], use_kb=False) == 0
    assert "Administrator's Guide" in capsys.readouterr().out
    assert sme.cmd_src(knowledge, {}, ["SRC-000999"], use_kb=False) == 1


def test_src_with_kb_but_no_helper(knowledge: Path, capsys, monkeypatch):
    monkeypatch.setattr(sme, "kbq_path", lambda config: None)
    assert sme.cmd_src(knowledge, {}, ["SRC-000029"], use_kb=True) == 1
    assert "kbq.py not found" in capsys.readouterr().out


def test_brief_runs(knowledge: Path, capsys):
    assert sme.cmd_brief(knowledge, {"research_root": "Z:/nowhere"}) == 0
    out = capsys.readouterr().out
    assert "Notes: 2" in out and "Scenarios: 1" in out and "absent on this machine" in out


def test_main_dispatch(knowledge: Path):
    assert sme.main(["--knowledge", str(knowledge), "term", "bgp"]) == 0
    assert sme.main(["--knowledge", str(knowledge / "missing"), "brief"]) == 2


def test_kbq_command_puts_root_before_subcommand(tmp_path: Path):
    kbq = tmp_path / "kbq.py"
    command = sme.kbq_command(kbq, {"kb_root": "E:/kb"}, ["SRC-000029", "SRC-000036"])
    assert command[1] == str(kbq)
    assert command.index("--root") < command.index("src")
    assert command[-2:] == ["SRC-000029", "SRC-000036"]
    assert "--root" not in sme.kbq_command(kbq, {}, ["SRC-000029"])
