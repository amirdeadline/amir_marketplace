---
description: Evidence-based multi-phase review of technical design documents (HLD/LLD/as-built/Prisma SASE); no forced findings
argument-hint: <document path> [--knowledge-base path] [--references path] [--document-type auto] [--review-depth standard|deep|targeted] [--output path]
---

# /amir:amir_doc_review

Follow the skill at `skills/amir_doc_review/SKILL.md` in this plugin (also installable at
user scope as `/amir_doc_review` for Cursor and Claude Code).

Apply that skill now. Treat `$ARGUMENTS` as the document path plus optional flags
(`--knowledge-base`, `--references`, `--requirements`, `--document-type`,
`--product-version`, `--management-platform`, `--internet-research`, `--review-depth`,
`--technical-only`, `--editorial-only`, `--output`, `--max-parallel-agents`, `--resume`,
`--strict-evidence`, `--include-optional-improvements`).

Orchestrate multi-phase review with bounded fresh sub-agents, independent finding
validation, and a structured report. Do not invent findings. An excellent document may
correctly produce zero required corrections. Report the absolute path of any report file
written.
