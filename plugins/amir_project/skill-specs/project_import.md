# project_import

## Command

`/project_import {path} {prompt}`

## Purpose

Wrap an **existing** repository or codebase as an amir project. Review what already exists before discovery; create amir structure adjacent to or inside the repo per human choice. Distinct from greenfield `/project_create`.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `{path}` | Yes | Filesystem path to existing repository or project root |
| `{prompt}` | Yes | Human intent: what to achieve with this codebase (extend, refactor, document, ship, etc.) |
| Layout choice | Human | Whether `ai/` lives inside `{path}` or in a sibling wrapper folder |

## Behavior

1. Verify `{path}` exists and is readable; emit **PROBLEM** if not.
2. Run **repository review** first (read-only): inventory languages, entry points, tests, CI, docs, git history summary, and obvious risks. Do not modify source yet.
3. Detect existing `ai/` tree or prior amir state; if present, offer `/resume_build` or `/project_doctor` instead of duplicate init.
4. Ask human to confirm layout: **wrap in place** (`{path}/ai/`) vs **adjacent project folder** linking to `{path}` as source root.
5. Build question inventory informed by review findings (gaps vs `{prompt}`, not generic greenfield questions).
6. Triage and ask batches per `core/question-format.md` and `core/interaction-style.md`.
7. Draft `ai/project-goal.md` and `project.md` reflecting **current state + target outcome** (as-is architecture section required).
8. On human approval, run `node tools/state.js <root> init` only if state absent; otherwise reconcile via `/project_doctor`.
9. Record import metadata in `ai/state/decisions.json` (source path, layout choice, review summary id).
10. Instantiate missing templates from plugin `templates/` without clobbering tracked source files.
11. Append `project_import` to `ai/state/activity.jsonl`; regenerate views.
12. Recommend `/design` or `/resume_build` based on existing maturity.

## Core modules referenced

- Follow `core/workspace-rules.md`
- Follow `core/question-format.md`
- Follow `core/interaction-style.md`
- Follow `core/message-contract.md`
- Follow `core/no-drift-rules.md` (existing code is baseline truth until goal says otherwise)
- Follow `core/honesty-rules.md`
- Follow `core/security-rules.md` (do not copy secrets during review)

## State files read/written

| File | Access |
|------|--------|
| `{path}/**` | Read (review) |
| `ai/project-goal.md` | Write |
| `project.md` | Write |
| `ai/state/*.json` | Write (init or reconcile) |
| `ai/state/activity.jsonl` | Append |
| `ai/views/*.md` | Write (via render) |

## Outputs

- amir project bound to existing repository
- `project.md` with as-is / to-be summary
- `ai/project-goal.md` approved for import context
- Initialized or reconciled state JSON
- Import decision record with layout choice

## Failure/abort behavior

- Abort if `{path}` missing or permission denied.
- Abort if human declines layout choice; do not guess wrap vs adjacent.
- Do not run `init` over non-empty `ai/state/` without explicit human approval and backup note in decisions.
- Stop on unresolved Blocking questions about ownership, deployment target, or license constraints.
- If repository contains committed secrets, emit **PROBLEM**, recommend rotation before proceeding.
