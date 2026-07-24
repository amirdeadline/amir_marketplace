# git_tree

## Command

`/git_tree`

## Purpose

Render the branch and commit graph for the project as human-readable text or Mermaid, including amir checkpoint tags (`amir/T*-complete`).

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Current amir project root |
| Format | Optional | `text` (default) or `mermaid` |
| Depth | Optional | Max commits to show (default 30) |
| Branch filter | Optional | Limit to named branch |

## Behavior

1. Verify git repository; if absent, offer `/git_setup` and stop.
2. Run `git branch -a --list` and collect local/remote branch tips.
3. Run `git tag -l 'amir/T*-complete'`; map tags to commit hashes via `git rev-parse`.
4. Cross-reference tags with `.ai/state/tasks.json` task ids where available (read-only); note tasks without tags or tags without tasks.
5. **Text format:** run `git log --oneline --graph --decorate -n <depth> [--all|<branch>]`; append tag legend table (tag → commit → task id).
6. **Mermaid format:** build `gitGraph` or commit DAG Mermaid from `git log --pretty=format:'%H|%P|%s|%D'` — include annotated tags on commits; follow Mermaid syntax rules (no spaces in commit ids; sanitize messages).
7. Present graph to human per `core/message-contract.md`; offer `/details` for full log if truncated.
8. Append read-only `git_tree` activity with format, depth, tag count.

## Core modules referenced

- Follow `core/message-contract.md`
- Follow `core/honesty-rules.md`
- Follow `core/workspace-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `.ai/state/tasks.json` | Read (task ↔ tag correlation) |
| `.ai/state/activity.jsonl` | Append |
| Git refs/tags | Read only |

## Outputs

- Branch/commit graph (text or Mermaid)
- Checkpoint tag table: `amir/T<id>-complete` → commit → task status
- Truncation note if depth limit applied

## Failure/abort behavior

- Abort if not a git repository.
- Do not invent commits or tags — VERIFIED `git` output only.
- If `git log` empty, report empty repo state.
- If Mermaid generation fails on complex history, fall back to text format and note degrade path.
