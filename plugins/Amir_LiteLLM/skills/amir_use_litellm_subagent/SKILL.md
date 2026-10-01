---
name: amir_use_litellm_subagent
description: >-
  Delegates work to Claude Code via Palo LiteLLM (palo venv credentials, litellm
  launcher). Probes the proxy first; plays a sound and alerts the user if LiteLLM
  fails or does not respond. Use for /amir_use_litellm_subagent or when the user
  asks for a LiteLLM subagent from Cursor.
disable-model-invocation: true
---

# amir_use_litellm_subagent

Delegate from **Cursor** to **Claude Code** running on the **Palo LiteLLM proxy**. Credentials live in the **palo** workspace (`.env` / `env.cmd`); never ask for or print `ANTHROPIC_API_KEY`.

This is **not** Cursor's built-in Task subagent (that does not use LiteLLM unless Cursor itself is wired to the proxy).

**Prerequisite:** Install [workspaces-venv](https://github.com/amirdeadline/workspaces-venv) (`install.py`) so `litellm`, palo venv, and usage logging exist. Deploy this plugin with `litellm_mcp.py deploy --cursor-skills` to copy this skill to `~/.cursor/skills/`.

## When this skill applies

User invokes **`/amir_use_litellm_subagent`** or asks to run a **LiteLLM subagent** with palo tokens.

Extract the **task** from the message (everything after the command name).

## Required workflow

1. **Probe LiteLLM** (mandatory before any delegation):
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.cursor\skills\amir_use_litellm_subagent\scripts\probe-litellm.ps1"
   ```

2. **If probe exit code ≠ 0** — stop immediately:
   - Run failure notification:
     ```powershell
     powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.cursor\skills\amir_use_litellm_subagent\scripts\notify-litellm-failure.ps1" -Reason "<short reason from probe>"
     ```
   - Tell the user clearly: **LiteLLM session failed or is not responding**; subagent was **not** started. Mention VPN / palo / `litellm --models` as next checks.
   - Do **not** fall back to Cursor Task subagent unless the user explicitly asks.

3. **If probe succeeds** — run the subagent:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.cursor\skills\amir_use_litellm_subagent\scripts\run-litellm-subagent.ps1" -Task "<task>" -ProjectDir "<absolute project root>" -SubagentType "<generalPurpose|explore|code-reviewer|...>"
   ```
   - Default `-ProjectDir` to the Cursor workspace root.
   - Pick `-SubagentType` from the task (exploration → `explore`, review → `code-reviewer`, else `generalPurpose`).

4. **Return** the script stdout as the subagent report. If run script exits non-zero, notification already ran — summarize the failure for the user.

5. **Usage (mandatory display)** — `run-litellm-subagent.ps1` logs and prints after each run:
   - Tokens for this run (from Claude transcript)
   - USD for this run (LiteLLM key spend delta)
   - **This week** rolling 7-day tokens + USD

   Shared log (append-only JSON Lines): `%WORKSPACES_ROOT%\logs\litellm-usage.jsonl`  
   Override: env `LITELLM_USAGE_LOG`.

   Show the script’s **LiteLLM usage this run … | This week …** lines to the user verbatim. If logging fails, say so but still return the subagent report.

   Full machine report (all projects + today/7d/30d):
   ```powershell
   litellm --usage
   ```

   Manual weekly summary:
   ```powershell
   python "$env:WORKSPACES_ROOT\scripts\log_litellm_usage.py" weekly
   ```

## LiteLLM interactive sessions (`litellm` Claude Code)

Each **Stop** hook (turn finished) also appends to the same JSONL and prints usage in the Claude terminal via `log-litellm-usage.ps1` under palo `.claude-code/hooks/`.

## Subagent type hints

| User intent | `-SubagentType` |
|-------------|-----------------|
| Search repo, map code | `explore` |
| Code review | `code-reviewer` |
| Default multi-step work | `generalPurpose` |

## Manual checks (user)

```powershell
palo
litellm --models
litellm --usage
litellm
```

## Security

- Never log or echo palo `.env` contents.
- Probe uses `litellm --models` only (no key in output).

## Scripts

| Script | Role |
|--------|------|
| `scripts/probe-litellm.ps1` | Health check |
| `scripts/notify-litellm-failure.ps1` | Random WAV + warning dialog |
| `scripts/run-litellm-subagent.ps1` | Probe + `claude --print` via `litellm` + usage log |
| `scripts/log_litellm_usage.py` | Fallback logger if workspaces scripts missing |
