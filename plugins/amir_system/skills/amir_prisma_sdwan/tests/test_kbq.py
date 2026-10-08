"""Tests for scripts/kbq.py (KB lookup helper). Run: python -m pytest -q tests"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import kbq  # noqa: E402

KB = "palo-alto-knowledge-base"


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture()
def kb_root(tmp_path: Path) -> Path:
    root = tmp_path / "kbroot"
    _write(root / KB / "PaloAlto.md", "# Palo Alto KB\n")
    _write(root / ".ai/prompts/kb_use.md", "# kb use\n")
    _write(root / KB / "knowledge-map.json", json.dumps({
        "products": {"Prisma SD-WAN": {"index": "prisma-sd-wan/README.md"}},
        "negative_routing_rules": ["Do not mix PAN-OS SD-WAN with Prisma SD-WAN."],
        "corpus_mirror": {"topic_routes": {"sdwan-paee-datapath": "palo-alto-knowledge-base/x/README.md"}},
        "dependency_graph": [{"from": "Prisma SD-WAN", "to": "Prisma Access", "purpose": "SASE onboarding"}],
    }))
    _write(root / "prisma_sdwan.md", "\n".join([
        "# container",
        "### Source PDF: prisma-sd-wan-administration",
        "Path policy selects paths.",
        "LQM measures loss, latency and jitter.",
        "### Source PDF: SDWANN best practice",
        "Use path policy stacks.",
    ]) + "\n")
    _write(root / KB / "prisma-sd-wan/troubleshooting/lqm.md", "LQM uplink loss steps\nshow lqm\n")
    registry = {
        "authority_scale": "1=official, 9=internal, 10=expert inference",
        "sources": [
            {"source_id": "SRC-000029", "title": "prisma-sd-wan-administration.pdf",
             "product": ["Prisma SD-WAN"], "source_type": "official_documentation",
             "publisher": "Palo Alto Networks", "canonical_url": "", "authority_rank": 1,
             "local_path": "embedded:prisma_sdwan.md", "retrieved_date": "2026-07-16",
             "publication_date": None, "last_updated_date": None, "document_version": "",
             "superseded_by": [], "notes": "Admin guide."},
            {"source_id": "SRC-000036", "title": "SDWANN best practice.pdf",
             "product": ["Prisma SD-WAN"], "source_type": "official_documentation",
             "publisher": "Palo Alto Networks", "canonical_url": "", "authority_rank": 1,
             "local_path": "embedded:prisma_sdwan.md", "retrieved_date": "2026-07-16",
             "publication_date": None, "last_updated_date": None, "document_version": "",
             "superseded_by": [],
             "notes": "Best practices. locate via '### Source PDF: SDWANN best practice'."},
            {"source_id": "SRC-000101", "title": "LQM Uplink Pkt Loss", "product": ["Prisma SD-WAN"],
             "source_type": "internal_document", "publisher": "PAEE internal", "canonical_url": "",
             "authority_rank": 9, "local_path": f"{KB}/prisma-sd-wan/troubleshooting/lqm.md",
             "retrieved_date": "2026-10-04", "publication_date": None, "last_updated_date": None,
             "document_version": "", "superseded_by": [], "notes": "PAEE internal."},
            {"source_id": "SRC-000061", "title": "Okta SAML note", "product": ["Cloud Identity Engine"],
             "source_type": "third_party", "publisher": "Okta", "canonical_url": "https://okta.example",
             "authority_rank": 8, "local_path": "", "retrieved_date": "2026-07-16",
             "publication_date": None, "last_updated_date": None, "document_version": "",
             "superseded_by": [], "notes": ""},
        ],
    }
    _write(root / KB / "source-registry.json", json.dumps(registry))
    _write(root / KB / "terminology.json", json.dumps({"terms": [
        {"canonical": "ION", "abbreviations": ["ION device"], "confused_with": ["PAN-OS firewall"],
         "notes": "Prisma SD-WAN branch appliance."}]}))
    pages = [
        {"id": "78890282", "title": "Path Selection Walk Through - Technical Notes", "product": "sd_wan",
         "type": "reference", "words": 900, "file": "confluence/sd_wan/78890282_Path_Selection.md",
         "headings": ["LQM", "Path policy"]},
        {"id": "111", "title": "GlobalProtect portal", "product": "prisma_access", "type": "howto",
         "words": 50, "file": "confluence/prisma_access/111_GP.md", "headings": []},
    ]
    _write(root / KB / "confluence-index/pages-index.jsonl", "\n".join(json.dumps(p) for p in pages) + "\n")
    _write(root / "confluence/sd_wan/78890282_Path_Selection.md", "# Path selection\n")
    return root


# ---- root resolution -------------------------------------------------------

def test_resolve_root_prefers_explicit_argument(kb_root, tmp_path):
    root, how = kbq.resolve_root(cli_root=str(kb_root), env={}, cwd=tmp_path, config_path=None)
    assert root == kb_root and how == "--root"


def test_resolve_root_uses_env_variable(kb_root, tmp_path):
    root, how = kbq.resolve_root(env={"PRISMA_DOCS_PATH": str(kb_root)}, cwd=tmp_path, config_path=None)
    assert root == kb_root and how == "PRISMA_DOCS_PATH"


def test_resolve_root_walks_up_from_cwd(kb_root):
    deep = kb_root / KB / "prisma-sd-wan" / "troubleshooting"
    root, how = kbq.resolve_root(env={}, cwd=deep, config_path=None)
    assert root == kb_root and how == "current folder"


def test_resolve_root_falls_back_to_config(kb_root, tmp_path):
    cfg = _write(tmp_path / "config.json", json.dumps({"kb_root": str(kb_root)}))
    elsewhere = tmp_path / "other"
    elsewhere.mkdir()
    root, how = kbq.resolve_root(env={}, cwd=elsewhere, config_path=cfg)
    assert root == kb_root and how == "config.json"


def test_resolve_root_skips_invalid_env_and_raises_when_nothing_found(tmp_path):
    with pytest.raises(kbq.KbNotFound):
        kbq.resolve_root(env={"PRISMA_DOCS_PATH": str(tmp_path / "nope")}, cwd=tmp_path, config_path=None)


# ---- registry lookups -----------------------------------------------------------

def test_rank_label_maps_authority_to_evidence_label():
    assert "CONFIRMED" in kbq.rank_label(1)
    assert "INTERNAL" in kbq.rank_label(9)
    assert "INFERENCE" in kbq.rank_label(10)
    assert "not defined" in kbq.rank_label(8)


def test_src_embedded_source_reports_container_line_range(kb_root):
    out = kbq.describe_sources(kb_root, ["SRC-000029"])
    assert "prisma_sdwan.md" in out
    assert "lines 2-4" in out
    assert "CONFIRMED" in out


def test_src_uses_locate_via_marker_from_notes(kb_root):
    out = kbq.describe_sources(kb_root, ["SRC-000036"])
    assert "lines 5-6" in out


def test_src_file_source_resolves_local_path(kb_root):
    out = kbq.describe_sources(kb_root, ["SRC-000101"])
    assert "lqm.md" in out and "exists" in out and "INTERNAL" in out


def test_src_unknown_id_is_reported_not_invented(kb_root):
    out = kbq.describe_sources(kb_root, ["SRC-000150"])
    assert "NOT IN REGISTRY" in out


def test_src_without_local_path_reports_external_url(kb_root):
    out = kbq.describe_sources(kb_root, ["SRC-000061"])
    assert "https://okta.example" in out and "not defined" in out


def test_find_sources_matches_all_words(kb_root):
    hits = kbq.find_sources(kbq.load_registry(kb_root), ["lqm", "loss"], limit=10)
    assert [h["source_id"] for h in hits] == ["SRC-000101"]


# ---- other lookups -------------------------------------------------------------

def test_search_pages_filters_by_product_and_reports_local_file(kb_root):
    out = kbq.search_pages(kb_root, ["path", "selection"], product="sd_wan", limit=5)
    assert "78890282" in out and "local file: yes" in out
    assert "GlobalProtect" not in out


def test_lookup_term_returns_confusions(kb_root):
    out = kbq.lookup_term(kb_root, "ion")
    assert "PAN-OS firewall" in out


def test_lookup_term_matches_whole_words_only(kb_root):
    terms = {"terms": [{"canonical": "Prisma Access", "notes": "mobile connection service"},
                       {"canonical": "ION", "notes": "branch appliance"}]}
    (kb_root / KB / "terminology.json").write_text(json.dumps(terms), encoding="utf-8")
    out = kbq.lookup_term(kb_root, "ion")
    assert "branch appliance" in out and "Prisma Access" not in out


def test_line_numbers_count_only_newlines(kb_root):
    container = kb_root / "prisma_sdwan.md"
    container.write_bytes(b"a\rb\x0cc\n### Source PDF: prisma-sd-wan-administration\nPath policy x\n")
    src = kbq._sources_by_id(kbq.load_registry(kb_root))["SRC-000029"]
    assert kbq.locate_embedded(kb_root, src)[0][1:] == (2, 3)
    assert "  3: Path policy x" in kbq.grep_source(kb_root, "SRC-000029", "path policy", context=0)


def test_grep_skips_table_of_contents_lines(kb_root):
    container = kb_root / "prisma_sdwan.md"
    container.write_text("### Source PDF: prisma-sd-wan-administration\n"
                         "Add a Path Policy Rule ........................ 448\n"
                         "The ION evaluates the path policy rules.\n", encoding="utf-8")
    out = kbq.grep_source(kb_root, "SRC-000029", "path policy", context=0)
    assert "448" not in out and "evaluates the path policy" in out


def test_grep_source_searches_only_inside_that_source(kb_root):
    out = kbq.grep_source(kb_root, "SRC-000029", "path policy", context=0, limit=10)
    assert "Path policy selects paths." in out
    assert "Use path policy stacks." not in out  # belongs to SRC-000036


def test_brief_lists_entry_points_and_negative_rules(kb_root):
    out = kbq.brief(kb_root)
    assert "kb_use.md" in out and "PAN-OS SD-WAN" in out and "sdwan-paee-datapath" in out


def test_check_map_reports_missing_paths(kb_root, tmp_path):
    topic_map = _write(tmp_path / "map.md", "\n".join([
        f"- `{KB}/prisma-sd-wan/troubleshooting/lqm.md`",
        f"- `{KB}/does/not/exist.md`",
        "- `confluence/sd_wan/78890282_*`",
        "- `confluence/sd_wan/<id>_*` placeholder example",
    ]))
    missing = kbq.check_map(kb_root, topic_map)
    assert missing == [f"{KB}/does/not/exist.md"]


def test_cli_root_command_exits_2_when_kb_missing(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SKILL_DIR / "scripts" / "kbq.py"), "--root", str(tmp_path / "missing"), "root"],
        capture_output=True, text=True, cwd=tmp_path, env={"SYSTEMROOT": "C:\\Windows"},
    )
    assert proc.returncode == 2
    assert "KB root not found" in proc.stderr
