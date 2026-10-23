# amir_cursor_subagent

Claude Code (or Cursor) skill that uses the **Cursor AI agent installed on this PC** as a
subagent through the Cursor SDK. Default model `composer-2.5` with `fast=true`; any model id
Cursor lists can be chosen with `--model` and tuned with `--param`.

```
/amir_cursor_subagent {prompt}                       # composer-2.5 fast
/amir_cursor_subagent --model claude-opus-5-5 --param effort=high {prompt}
/amir_cursor_subagent smoke test | ping | models
```

Layout:

| Path | Role |
|---|---|
| `SKILL.md` | the skill (procedure, defaults, troubleshooting) |
| `scripts/run_cursor_subagent.ps1` | PowerShell wrapper (`-Cwd -TaskFile -Model -Param -Json -Events -ListModels`) |
| `scripts/cursor_subagent.py` | python delegate on `cursor-sdk` (JSONL store, Windows bridge patch, event log) |
| `scripts/cursor_subagent_env.ps1` | venv + `CURSOR_API_KEY` lookup (never prints the key) |
| `assets/brief_template.md` | standalone brief skeleton for one bounded task |

One real copy lives here; `scripts\install-user-skills.ps1 -Skills amir_cursor_subagent` creates
the junctions in `%USERPROFILE%\.claude\skills` and `%USERPROFILE%\.cursor\skills`.

Requires: Cursor installed, `python -m venv %USERPROFILE%\.venvs\composer` with `cursor-sdk`,
and `CURSOR_API_KEY` in `%USERPROFILE%\.amir\secrets\cursor_api_key.env` or a User env var.

Successor of `amir_subagent_composer` / `cursor-composer-delegate` (Composer-only, no model
choice, no event log).
