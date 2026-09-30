---
description: Humanize technical documentation (minimum-change) while preserving meaning, structure, and formatting
argument-hint: <document_path>
disable-model-invocation: true
---

# /amir:amir_humanized

Follow the skill at `skills/amir_humanized/SKILL.md` in this plugin (also
installed at user scope as `/amir_humanized` for Cursor and Claude Code).

Apply that skill now. Treat `$ARGUMENTS` as the document path (strip wrapping
quotes) plus optional `--output` / `--project-root`.

Humanize only prose that materially benefits. Never overwrite the source.
Write `<stem>_humanized.<ext>` next to the source and
`<PROJECT_ROOT>/.ai/reports/<stem>_humanized_report.md`. Return the short
console result from the skill, not the full report.
