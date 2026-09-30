# amir_humanized — test cases

Run:

```text
python scripts/humanize.py selftest
```

| ID | Check | Expected |
|----|-------|----------|
| S1 | Skill directory exists at plugin `skills/amir_humanized` | Present |
| S2 | Command `commands/amir_humanized.md` exists | Present |
| S3 | Required skill files exist (`SKILL.md`, `rules.md`, `report_template.md`, `scripts/humanize.py`) | Present |
| S4 | SKILL frontmatter `name` equals `amir_humanized` and includes `argument-hint` | Pass |
| S5 | User junctions: `~/.cursor/skills/amir_humanized`, `~/.claude/skills/amir_humanized` | Resolve to plugin skill dir |
| S6 | Init rejects a missing file and creates no output | Pass |
| S7 | Project-root detection uses `--project-root` / git root, not the document directory | Pass |
| S8 | `.ai/reports/` is created automatically | Pass |
| S9 | Humanized document is written next to the source | Pass |
| S10 | Report is written only under `<PROJECT_ROOT>/.ai/reports/` | Pass |
| S11 | Headings, paragraphs, lists, and tables are extracted and preserved | Pass |
| S12 | Code / commands / URLs / IPs are classified immutable or preserved | Pass |
| S13 | Em dashes are removed from prose and left inside code | Pass |
| S14 | Original source file is unchanged after init and finalize | Pass |
| S15 | PDF source is never edited; sibling output is Markdown | Pass |
