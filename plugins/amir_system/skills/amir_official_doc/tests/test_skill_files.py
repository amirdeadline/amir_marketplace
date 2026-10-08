"""Checks that both paired skills load the same way in Claude Code and Cursor.

Cursor limits description to 1024 characters and expects name == folder name; both tools prefer
SKILL.md under 500 lines; every supporting file the skill names must exist.
"""
import re
from pathlib import Path

import pytest

SKILLS_ROOT = Path(__file__).resolve().parents[2]
PAIR = ("amir_official_doc", "amir_prisma_sdwan")


def frontmatter(text: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, "SKILL.md must start with YAML frontmatter"
    fields, key = {}, None
    for line in match.group(1).splitlines():
        top = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if top:
            key, value = top.group(1), top.group(2).strip()
            fields[key] = "" if value in (">-", ">", "|") else value.strip('"')
        elif key and line.startswith("  "):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields


@pytest.mark.parametrize("skill", PAIR)
def test_frontmatter_is_valid_for_both_platforms(skill):
    text = (SKILLS_ROOT / skill / "SKILL.md").read_text(encoding="utf-8")
    fields = frontmatter(text)
    assert fields["name"] == skill
    assert 0 < len(fields["description"]) <= 1024
    assert fields["description"].startswith("Use when")
    assert len(text.splitlines()) < 500


@pytest.mark.parametrize("skill", PAIR)
def test_referenced_supporting_files_exist(skill):
    folder = SKILLS_ROOT / skill
    text = (folder / "SKILL.md").read_text(encoding="utf-8")
    refs = set(re.findall(r"`((?:references|scripts|templates)/[\w./-]+)`", text))
    assert refs, "expected the skill to reference its supporting files"
    assert [r for r in refs if not (folder / r).exists()] == []


def test_paired_skills_point_at_each_other():
    for skill, other in (PAIR, PAIR[::-1]):
        text = (SKILLS_ROOT / skill / "SKILL.md").read_text(encoding="utf-8")
        assert f"../{other}/SKILL.md" in text
