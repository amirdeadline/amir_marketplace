---
name: amir_cursor_subagent
description: >-
  Use the Cursor AI agent installed on this PC as a subagent: runs one bounded task
  through the Cursor SDK on Composer 2.5 fast by default, or on any model id Cursor
  offers (--model, --param). Trigger on /amir_cursor_subagent, "use cursor", "use
  composer", "start composer", or when the user wants a cheap fast executor while
  Claude plans and verifies. Also /amir_cursor_subagent smoke test | ping | models.
argument-hint: "[--model <id>] [--param k=v] {prompt | smoke test | ping | models}"
---

# /amir_cursor_subagent [--model id] [--param k=v] {prompt}

Run `$ARGUMENTS` on the **local Cursor agent** (Cursor SDK bridge, started from the Cursor
install on this PC). Claude stays the orchestrator: it writes the brief, launches Cursor,
verifies the result with its own tools, and only then reports or launches the next task.

## Defaults and argument parsing

| Token in `$ARGUMENTS` | Meaning |
|---|---|
| none | model **`composer-2.5`** with **`fast=true`** (Cursor's own default variant) |
| `--model <id>` | any id from `models` (for example `claude-opus-5-5`, `grok-4.7`, `default` = Cursor Auto) |
| `--param k=v` (repeatable) | model parameter: `fast=true|false`, `effort=low|medium|high|xhigh|max`, `context=300k|1m` |
| `--no-fast` | Composer without the fast variant |
| `models` | list ids, parameters and default variants, then stop |
| `smoke test` | connectivity check, then stop |
| `ping` | identity check, then stop |
| `--cwd <path>` | repo root for the agent (default: current project root) |

Strip these tokens; what remains is the task. Empty task: ask for one or suggest `smoke test`.
`fast` is only defaulted on for `composer-*`; other models run with their own defaults unless
`--param` says otherwise.

## Scripts (all in `${CLAUDE_SKILL_DIR}/scripts`, one real copy in the marketplace)

- `run_cursor_subagent.ps1` — wrapper: `-Cwd`, `-TaskFile` | `-TaskText`, `-Model`, `-Param k=v`,
  `-NoFast`, `-Json`, `-Events <file>`, `-ListModels`. Never a parameter named `Prompt`.
- `cursor_subagent.py` — the delegate (python, cursor-sdk). JSONL agent store at
  `%USERPROFILE%\.amir\composer-store` (short path; the SDK default breaks Windows MAX_PATH).
- `cursor_subagent_env.ps1` — venv `%USERPROFILE%\.venvs\composer` + `CURSOR_API_KEY` lookup.
- `assets/brief_template.md` — the standalone-brief skeleton.

Launch (Bash tool, from the main session; `run_in_background: true` for anything over ~2 min):

```bash
SK="$USERPROFILE/.claude/skills/amir_cursor_subagent/scripts"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$SK/run_cursor_subagent.ps1" \
  -Cwd "<REPO_ROOT>" -TaskFile "<SCRATCHPAD>/taskN.txt" -Json \
  -Events "<SCRATCHPAD>/taskN_events.txt" > "<SCRATCHPAD>/taskN_out.json" 2> "<SCRATCHPAD>/taskN_err.txt"
```

Add `-Model <id>` / `-Param k=v` only when the user asked for a model. The JSON holds
`status`, `result`, `run_id`, `model`, `params`, `duration_ms`. Exit 0 finished, 1 setup problem,
2 the run itself failed (read the events file: it shows the real error, the SDK summary is vague).

## Procedure for a repo task (this is the loop that works)

1. **Bound it.** Project root, files it may touch, acceptance checks, what is out of scope.
   Vague, multi-system, secret-handling, live-infrastructure, or judgment-heavy work stays with
   Claude or a specialist agent; say so and offer to narrow it.
2. **Write a standalone brief** to a UTF-8 file in the scratchpad from `assets/brief_template.md`:
   goal, cwd, branch, the only files to read, exact steps, exact commands with expected results,
   the exact `git add <paths>` + message, hard constraints, reply format. The agent has no chat
   history and no memory between runs: everything it needs is in that file. For a plan with
   many tasks, one brief and one run per task; never "do tasks 3 to 9".
3. **Launch** with the wrapper (above). Background it when long; keep the main session free.
4. **Verify, do not trust.** After every run: `git status --short`, `git log --oneline -3`,
   `git diff` of the named files, rerun the brief's checks yourself, confirm nothing outside
   the allowed paths changed, line endings (`git ls-files --eol`), no secrets in the diff.
   A run that reports success with a dirty tree or a missing commit is a failed run.
5. **Fix forward or stop.** Small deviation: next brief tells the agent what to correct.
   Repeated failure or an out-of-scope change: stop, revert with the user's approval, report.
6. **Report** per run: files changed, checks and counts, commit hash, deviations, `run_id`,
   and anything left unverified.

## Smoke test, ping, models

- `smoke test`: brief = `Connectivity smoke test only. cwd: <REPO_ROOT>. Do not create, modify
  or delete files. Do not run git or installs. Reply with exactly one line: COMPOSER_SMOKE_OK`.
  Pass = exit 0, `status` finished, result contains `COMPOSER_SMOKE_OK`, `git status` unchanged.
- `ping`: brief = `Do not change files. Reply in one sentence: state that you are the Cursor
  agent and the model id you run on.`
- `models`: `run_cursor_subagent.ps1 -Cwd <REPO_ROOT> -ListModels`.

Always launch these; they are the user testing the path, not a chat question.

## Setup (once per PC)

```powershell
python -m venv "$env:USERPROFILE\.venvs\composer"
& "$env:USERPROFILE\.venvs\composer\Scripts\pip.exe" install cursor-sdk
```

`CURSOR_API_KEY` (Cursor Dashboard → Integrations) goes in
`%USERPROFILE%\.amir\secrets\cursor_api_key.env` as `CURSOR_API_KEY=...`, or a User env var,
or the shared `ai` workspace `.env`. Never paste it into chat, never print it, never commit it.
Cursor itself must be installed (the SDK launches its local bridge). Override the venv with
`CURSOR_SUBAGENT_VENV`, the store with `CURSOR_SDK_STORE_ROOT`.

## Troubleshooting (seen on this PC)

| Symptom | Cause / fix |
|---|---|
| `[internal] unable to open database file` in events | SDK default SQLite store path > 260 chars. The delegate uses the JSONL store at a short root; check `CURSOR_SDK_STORE_ROOT`. |
| `WinError 10038 ... not a socket` at startup | cursor-sdk 1.0.35 bridge discovery on Windows; the delegate patches it. If it still appears, the venv has a different SDK version. |
| "Cursor agent run failed" with no detail | Rerun with `-Events <file>` and read the last lines. |
| Task text arrives as the word `composer` | Someone passed `-Prompt`. Use `-TaskFile` / `-TaskText`. |
| `Author identity unknown` on commit | The agent's shell has no git identity. The brief tells it to use one-shot `GIT_AUTHOR_*` / `GIT_COMMITTER_*` env vars, never `git config`. |
| Agent says done, tree is dirty | Not done. Verify step 4; send a corrective brief. |

## Hard rules

- The agent gets only what the brief gives: no secrets, no live-lab or cloud operations unless
  the user explicitly asked for that specific run and the brief lists the exact commands.
- Never `git add -A` / `git add .` in a brief; never commit to `main`; never push unless asked.
- Claude verifies every run with its own tools before claiming anything is done.
- Cursor appends `Co-authored-by: Cursor <cursoragent@cursor.com>` to commits it makes; say so
  if the project cares about trailers.
