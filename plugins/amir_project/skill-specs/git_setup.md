# git_setup

## Command

`/git_setup`

## Purpose

Guide the human through initializing version control for an amir project: repository creation, `.gitignore` with secrets and workspace temp policies, initial commit, and optional GitHub remote — every decision via structured questions.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Project root | Implicit | Directory to initialize as git repo |
| Host git | Implicit | `git` available on PATH |
| GitHub remote | Optional | Human may add `origin` during setup |
| Human answers | Required | Responses to question batches per step |

## Behavior

1. Verify project root exists and contains `.ai/` or is empty/new amir project; if neither, ask per `core/question-format.md` whether to init here or choose another path (**Blocking**).
2. Run `git rev-parse --is-inside-work-tree`; if already a repo, present status summary and ask: continue setup (fix ignore, commit, remote) or abort — log choice in `.ai/state/decisions.json` if `.ai/` exists.
3. If not a repo, ask human to confirm `git init` at project root (**Material**); on approval run `git init`.
4. Draft `.gitignore` with required patterns:
   - Secrets: `.env`, `.env.*` (except `.env.example`), `**/credentials*`, `**/*secret*`, `**/*token*` (sensible globs per `core/security-rules.md`)
   - Dependencies/build: `node_modules/`, `dist/`, `build/`, `*.log`, OS junk (`.DS_Store`, `Thumbs.db`)
   - **amir temp policy:** `.ai/agents/*/logs/`, `.ai/agents/*/tmp/`, `.ai/agents/*/.cache/` — workspace evidence stays trackable; ephemeral temp excluded
   - Host-specific lines from `adapters/<host>/capabilities.md` when present
5. Present proposed `.gitignore` diff for human approval (**Material**); apply only after approval.
6. Ask initial commit scope (**Material**): typical `.ai/state/`, `.ai/project-goal.md`, `project.md`, `verify.sh`, tracked config — exclude secrets and temp paths.
7. Stage approved files; show `git status` summary; ask commit message or accept default `chore: initial amir project setup`.
8. Run `git add` for approved paths only; create initial commit.
9. Ask whether to add GitHub remote (**Minor** default: skip):
   - If yes: collect remote URL, verify with `git remote -v`, ask branch name (default `main`), set `origin`, optionally `git push -u origin <branch>` after human confirms credentials ready.
10. Append `git_setup` to `.ai/state/activity.jsonl` when `.ai/` exists; otherwise log to orchestrator notes if pre-project.
11. Emit short summary per `core/message-contract.md`: repo path, initial commit hash, remote status, next recommended command (`/project_create` or `/git_commit`).

## Core modules referenced

- Follow `core/question-format.md`
- Follow `core/interaction-style.md`
- Follow `core/message-contract.md`
- Follow `core/security-rules.md`
- Follow `core/workspace-rules.md`
- Follow `core/honesty-rules.md`

## State files read/written

| File | Access |
|------|--------|
| `.git/` | Write (init) |
| `.gitignore` | Write (after approval) |
| `.ai/state/decisions.json` | Write (setup choices) |
| `.ai/state/activity.jsonl` | Append |
| Git index/commits | Write (initial commit) |
| `adapters/<host>/capabilities.md` | Read (ignore extras) |

## Outputs

- Initialized git repository
- Approved `.gitignore`
- Initial commit with human-chosen scope
- Optional `origin` remote and first push
- Human-facing setup summary with commit hash

## Failure/abort behavior

- Abort `git init` if human declines root confirmation.
- Never stage `.env` or files matching secrets patterns without explicit documented false-positive approval.
- Abort commit if `git status` shows secrets-pattern files staged; remove and re-present plan.
- Abort remote push if authentication fails; report VERIFIED error output only.
- Do not run `git push --force` during setup.
- If `git` not found, emit **NOT DOABLE** per `core/honesty-rules.md` with install guidance.
