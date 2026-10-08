"""Tests for scripts/mddoc.py (numbering, structure, style and evidence checks).

Run: python -m pytest -q -p no:cacheprovider tests
"""
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import mddoc  # noqa: E402

MDDOC = SKILL_DIR / "scripts" / "mddoc.py"


def doc(text: str) -> str:
    return textwrap.dedent(text).lstrip("\n")


def codes(findings, severity=None):
    return sorted({f.code for f in findings if severity is None or f.severity == severity})


CLEAN = doc("""
    # Branch Health Guide

    | Field | Value |
    |---|---|
    | Version | 0.1 |

    ## 1. Introduction

    This guide explains how to check branch health with Link Quality Monitoring (LQM).

    ### 1.1 Purpose

    It gives operators one repeatable check for each circuit.

    ## 2. Circuit Health

    LQM measures loss on each path. See [Purpose](#11-purpose).

    ```text
    ## not a heading — inside code
    ```
    """)


# ---- numbering ------------------------------------------------------------------

def test_number_assigns_hierarchical_numbers():
    text = doc("""
        # Title
        ## Introduction
        ### Purpose
        ### Scope
        ## Health
        ### ION Health
        #### CPU Utilization
        """)
    out, _ = mddoc.renumber(text)
    assert [l for l in out.splitlines() if l.startswith("#")] == [
        "# Title", "## 1. Introduction", "### 1.1 Purpose", "### 1.2 Scope",
        "## 2. Health", "### 2.1 ION Health", "#### 2.1.1 CPU Utilization"]


def test_number_replaces_stale_numbers_but_keeps_title_numbers():
    text = doc("""
        # Title
        ## 3. Introduction
        ### 7.2 Purpose
        ## 802.1Q Trunking
        ## 2026 Roadmap
        """)
    out, _ = mddoc.renumber(text)
    assert "## 1. Introduction" in out and "### 1.1 Purpose" in out
    assert "## 2. 802.1Q Trunking" in out and "## 3. 2026 Roadmap" in out


def test_number_letters_appendices():
    text = doc("""
        # Title
        ## Scope
        ## Appendix: Sources
        ### Registry
        ## Appendix Glossary
        """)
    out, _ = mddoc.renumber(text)
    assert "## 1. Scope" in out
    assert "## Appendix A. Sources" in out and "### A.1 Registry" in out
    assert "## Appendix B. Glossary" in out


def test_number_ignores_headings_inside_code_fences():
    text = doc("""
        # Title
        ~~~markdown
        ## Not a heading
        ~~~
        ## Real
        """)
    out, _ = mddoc.renumber(text)
    assert "## Not a heading" in out and "## 1. Real" in out


def test_number_rewrites_internal_links_after_insertion():
    text = doc("""
        # Title
        ## 1. New Section
        See [scope](#1-scope).
        ## 1. Scope
        """)
    out, link_map = mddoc.renumber(text)
    assert "## 2. Scope" in out and "[scope](#2-scope)" in out
    assert link_map == {"1-scope": "2-scope"}


def test_number_is_idempotent():
    once, _ = mddoc.renumber(CLEAN)
    twice, _ = mddoc.renumber(once)
    assert once == twice == CLEAN


def test_explicit_heading_ids_are_kept_and_count_as_anchors(tmp_path):
    text = "# T\n\n## Intro {#intro}\n\nSee [intro](#intro).\n\n## RBAC {#rbac-(x)}\n\n[r](#rbac-\\(x\\))\n"
    out, _ = mddoc.renumber(text)
    assert "## 1. Intro {#intro}" in out
    assert "E006" not in codes(mddoc.check(out, tmp_path / "d.md"))


def test_slug_matches_github_and_amir_md_style():
    slug = mddoc.slugger()
    assert slug("2.1 Circuit Health") == "21-circuit-health"
    assert slug("Appendix A. Sources") == "appendix-a-sources"
    assert slug("2.1 Circuit Health") == "21-circuit-health-1"


def test_cli_number_check_mode_reports_without_writing(tmp_path):
    path = tmp_path / "d.md"
    path.write_text("# T\n## Intro\n", encoding="utf-8")
    proc = subprocess.run([sys.executable, str(MDDOC), "number", str(path), "--check"],
                          capture_output=True, text=True)
    assert proc.returncode == 1 and path.read_text(encoding="utf-8") == "# T\n## Intro\n"
    subprocess.run([sys.executable, str(MDDOC), "number", str(path)], check=True, capture_output=True)
    assert "## 1. Intro" in path.read_text(encoding="utf-8")


# ---- structure checks -------------------------------------------------------------

def test_clean_document_has_no_errors_or_warnings(tmp_path):
    findings = mddoc.check(CLEAN, tmp_path / "d.md")
    assert [f for f in findings if f.severity in ("ERROR", "WARN")] == []


def test_exactly_one_h1_required(tmp_path):
    assert "E001" in codes(mddoc.check("## 1. A\n\ntext\n", tmp_path / "d.md"))
    assert "E001" in codes(mddoc.check("# A\n\n# B\n", tmp_path / "d.md"))


def test_heading_level_jump_is_error(tmp_path):
    text = "# T\n\n## 1. A\n\ntext\n\n#### 1.0.1 Deep\n\ntext\n"
    assert "E002" in codes(mddoc.check(text, tmp_path / "d.md"))


def test_wrong_numbering_is_error(tmp_path):
    text = "# T\n\n## 1. A\n\ntext\n\n## 3. B\n\ntext\n"
    findings = mddoc.check(text, tmp_path / "d.md")
    assert "E003" in codes(findings)
    assert any("## 2. B" in f.message for f in findings)


def test_unclosed_fence_is_error(tmp_path):
    assert "E004" in codes(mddoc.check("# T\n\n```\ncode\n", tmp_path / "d.md"))


def test_table_column_mismatch_is_error(tmp_path):
    text = "# T\n\n| a | b |\n|---|---|\n| 1 | 2 | 3 |\n| `x\\|y` | 4 |\n"
    findings = mddoc.check(text, tmp_path / "d.md")
    assert [f.line for f in findings if f.code == "E005"] == [5]


def test_broken_anchor_and_file_links_are_errors(tmp_path):
    (tmp_path / "img").mkdir()
    (tmp_path / "img" / "ok.png").write_bytes(b"x")
    text = doc("""
        # T

        ## 1. A

        [x](#missing) [y](#1-a) ![ok](img/ok.png) ![bad](img/none.png) [web](https://x.y)
        """)
    found = [(f.code, f.message) for f in mddoc.check(text, tmp_path / "d.md") if f.code in ("E006", "E007")]
    assert len(found) == 2
    assert "missing" in found[0][1] and "none.png" in found[1][1]


def test_style_warnings_skip_code(tmp_path):
    text = doc("""
        # T

        ## 1. A

        It is important to note that the ION is robust — mostly.

        `inline — code` stays quiet.
        """)
    findings = mddoc.check(text, tmp_path / "d.md")
    assert [f.line for f in findings if f.code == "W101"] == [5]
    assert {f.line for f in findings if f.code == "W102"} == {5}


def test_empty_and_large_sections_warn(tmp_path):
    big = " ".join(["word"] * 50)
    text = f"# T\n\n## 1. Empty\n\n## 2. Big\n\n{big}\n"
    findings = mddoc.check(text, tmp_path / "d.md", max_section_words=40)
    assert "W103" in codes(findings) and "W104" in codes(findings)


def test_undefined_acronym_warns_but_defined_or_glossary_does_not(tmp_path):
    text = doc("""
        # T

        ## 1. A

        The ION reports LQM data. Each WAN path has a Service Level Agreement (SLA). The SLA is checked.

        ## Appendix A. Glossary

        | Term | Meaning |
        |---|---|
        | ION | Prisma SD-WAN branch device |
        """)
    findings = [f for f in mddoc.check(text, tmp_path / "d.md") if f.code == "W105"]
    flagged = " ".join(f.message for f in findings)
    assert "LQM" in flagged and "WAN" in flagged
    assert "SLA" not in flagged and "ION" not in flagged


def test_acronym_defined_inside_a_longer_parenthesis(tmp_path):
    text = "# T\n\n## 1. A\n\nOpen it in Visual Studio Code (VS Code). Then use VS Code again.\n"
    assert "W105" not in codes(mddoc.check(text, tmp_path / "d.md"))


def test_only_glossary_tables_define_acronyms(tmp_path):
    text = doc("""
        # T

        ## 1. Checks

        The ION check is listed below.

        | Device | Check |
        |---|---|
        | ION | CPU |
        """)
    flagged = " ".join(f.message for f in mddoc.check(text, tmp_path / "d.md") if f.code == "W105")
    assert "ION" in flagged and "CPU" not in flagged


# ---- evidence checks ------------------------------------------------------------------

@pytest.fixture()
def kb(tmp_path):
    root = tmp_path / "kb"
    reg = root / "palo-alto-knowledge-base" / "source-registry.json"
    reg.parent.mkdir(parents=True)
    reg.write_text(json.dumps({"sources": [
        {"source_id": "SRC-000029", "authority_rank": 1, "title": "admin guide"},
        {"source_id": "SRC-000101", "authority_rank": 9, "title": "LQM internal"},
    ]}), encoding="utf-8")
    (root / "palo-alto-knowledge-base" / "real.md").write_text("x", encoding="utf-8")
    return reg


EVIDENCE_DOC = doc("""
    # T

    ## 1. Introduction

    Background for the reader.

    ## 2. Circuit Health

    Overview of circuit checks for the reader to follow.

    ### 2.1 Packet Loss

    Loss is measured per path by the device and shown in the portal views.
    """)


def evidence(rows: str, non_technical: str = "- Introduction") -> str:
    return doc(f"""
        # Evidence register: T

        ## Non-technical sections

        {non_technical}

        ## Claims

        | ID | Section | Claim | Label | Sources | Notes |
        |---|---|---|---|---|---|
        """) + textwrap.dedent(rows).strip() + "\n"


def run_evidence(tmp_path, register_text, registry, body=EVIDENCE_DOC):
    return mddoc.check(body, tmp_path / "d.md", evidence_text=register_text, registry_path=registry)


GOOD_ROWS = """
    | C-001 | Circuit Health | Circuits are checked | CONFIRMED | SRC-000029 | |
    | C-002 | Circuit Health > Packet Loss | Loss per path | INTERNAL | SRC-000101; `palo-alto-knowledge-base/real.md` | |
    """


def test_valid_evidence_register_passes(tmp_path, kb):
    findings = run_evidence(tmp_path, evidence(GOOD_ROWS), kb)
    assert [f for f in findings if f.severity in ("ERROR", "WARN")] == []


def test_unknown_src_id_in_register_or_body_is_error(tmp_path, kb):
    rows = GOOD_ROWS + "| C-003 | Packet Loss | x | CONFIRMED | SRC-000150 | |\n"
    body = EVIDENCE_DOC + "\nSee SRC-000999.\n"
    findings = run_evidence(tmp_path, evidence(rows), kb, body=body)
    messages = " ".join(f.message for f in findings if f.code == "E008")
    assert "SRC-000150" in messages and "SRC-000999" in messages


def test_register_section_not_in_document_is_error(tmp_path, kb):
    rows = GOOD_ROWS + "| C-003 | Jitter | x | INFERENCE | SRC-000029 | |\n"
    assert "E009" in codes(run_evidence(tmp_path, evidence(rows), kb))


def test_invalid_label_is_error(tmp_path, kb):
    rows = GOOD_ROWS + "| C-003 | Packet Loss | x | PROBABLY | SRC-000029 | |\n"
    assert "E010" in codes(run_evidence(tmp_path, evidence(rows), kb))


def test_confirmed_without_source_is_error(tmp_path, kb):
    rows = GOOD_ROWS + "| C-003 | Packet Loss | x | CONFIRMED | | |\n"
    assert "E011" in codes(run_evidence(tmp_path, evidence(rows), kb))


def test_user_supplied_source_counts_as_source_and_is_not_a_path(tmp_path, kb):
    rows = GOOD_ROWS + "| C-003 | Packet Loss | x | INTERNAL | user: notes in the request, 2026-10-04 | |\n"
    findings = run_evidence(tmp_path, evidence(rows), kb)
    assert "E011" not in codes(findings) and "E012" not in codes(findings)


def test_confirmed_backed_only_by_internal_sources_warns(tmp_path, kb):
    rows = GOOD_ROWS + "| C-003 | Packet Loss | x | CONFIRMED | SRC-000101 | |\n"
    assert "W110" in codes(run_evidence(tmp_path, evidence(rows), kb))


def test_missing_source_path_is_error(tmp_path, kb):
    rows = GOOD_ROWS + "| C-003 | Packet Loss | x | INTERNAL | `palo-alto-knowledge-base/nope.md` | |\n"
    assert "E012" in codes(run_evidence(tmp_path, evidence(rows), kb))


def test_section_with_prose_but_no_evidence_warns_unless_non_technical(tmp_path, kb):
    rows = "| C-001 | Circuit Health | Circuits are checked | CONFIRMED | SRC-000029 | |\n"
    findings = run_evidence(tmp_path, evidence(rows), kb)
    assert [f.message for f in findings if f.code == "W107"] == ["section '2.1 Packet Loss' has prose but no evidence row"]


def test_unknown_rows_are_listed_as_info(tmp_path, kb):
    rows = GOOD_ROWS + "| C-003 | Packet Loss | default threshold | UNKNOWN | | ask owner |\n"
    findings = run_evidence(tmp_path, evidence(rows), kb)
    assert any(f.code == "I201" and "default threshold" in f.message for f in findings)


# ---- outline --------------------------------------------------------------------------

def test_outline_lists_headings_with_word_counts():
    out = mddoc.outline(CLEAN)
    assert "1. Introduction" in out and "  1.1 Purpose" in out
    assert "words" in out
