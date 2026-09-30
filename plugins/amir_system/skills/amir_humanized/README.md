# amir_humanized

System-level document-humanization skill. Makes technical documentation read as
if an experienced engineer wrote it, using a minimum-change approach.

Part of the `amir_system` plugin (`/amir:amir_humanized`). Also installed as a
user-scope skill (`/amir_humanized`) for Cursor and Claude Code.

This skill is **not** tied to any project, product, or repository.

## Invocation

```text
/amir_humanized c:/test/test.docx
```

```text
/amir:amir_humanized c:/test/test.docx
```

Supported: `.docx`, `.md`, `.txt`. `.pdf` is extract-only (humanized sibling is
`<stem>_humanized.md`; the PDF is never edited).

## Outputs

Given `/amir_humanized c:/test/test.docx` and project root `c:/myproject`:

* Humanized document: `c:/test/test_humanized.docx`
* Report: `c:/myproject/.ai/reports/test_humanized_report.md`

The original file is never overwritten.

## Scripts

```text
python scripts/humanize.py init "<document_path>" --project-root "<project root>"
python scripts/humanize.py finalize "<document_path>" --project-root "<project root>" --changes "<changes.json>"
python scripts/humanize.py selftest
```

`init` validates paths, detects the project root, creates `.ai/reports/` if
needed, and extracts classified text blocks.

The agent applies the writing rules and writes `changes.json`.

`finalize` copies the source to a sibling `_humanized` file, applies only the
approved text replacements (DOCX is edited in place on that copy), compares
source vs output, and writes the report.

## Install (user scope)

```bat
cmd /c mklink /J "%USERPROFILE%\.cursor\skills\amir_humanized" "E:\PC3_Shared\Plugins\amir_marketplace\plugins\amir_system\skills\amir_humanized"
cmd /c mklink /J "%USERPROFILE%\.claude\skills\amir_humanized" "E:\PC3_Shared\Plugins\amir_marketplace\plugins\amir_system\skills\amir_humanized"
```

## Tests

```text
python scripts/humanize.py selftest
```

See `tests/test_cases.md`.
