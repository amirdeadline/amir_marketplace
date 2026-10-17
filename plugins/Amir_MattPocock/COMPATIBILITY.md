# Compatibility matrix (evidence-based)

Verified on **Windows 11** with:

- `skills` CLI **1.7.2** (`npx skills@latest`)
- Node **v24.18.0**
- Codex CLI **0.144.3** (installed; skill discovery not executed in CI)
- Hermes **0.0.0.0** at `C:\Users\amir\AppData\Local\hermes\bin\hermes.cmd` (installed; skill discovery not executed in automated test)
- Claude Code CLI present (`claude --help`)
- Cursor session (agent detected as `cursor-cli` by skills CLI)

Upstream: `https://github.com/mattpocock/skills` (38 installable skills listed 2026-10-17).

## Agent skill locations (project-local)

| Agent | Path | Mechanism (skills CLI 1.7.2) |
|---|---|---|
| Cursor | `.agents/skills/<name>/` | Canonical copy |
| Codex | `.agents/skills/<name>/` | Same canonical tree |
| Claude Code | `.claude/skills/<name>/` | Symlink/junction to canonical |
| Hermes Agent | `.hermes/skills/<name>/` | Symlink/junction to canonical |

Hermes CLI flag `--skills` exists; native discovery of `.hermes/skills` was **NOT TESTED** in this environment (no non-interactive `hermes chat` skill listing run).

## Feature matrix

| Feature | Cursor | Claude Code | Codex | Hermes |
|---|---|---|---|---|
| Project-local installation | **PASS** | **PASS** (symlink) | **PASS** | **PASS** (symlink) |
| Skill discovery (files on disk) | **PASS** | **PASS** | **PASS** | **NOT TESTED** |
| Slash-command invocation | **NOT TESTED** | **NOT TESTED** | **NOT TESTED** | **NOT TESTED** |
| Installation verified (Selected, 13 skills) | **PASS** (Pester) | **PASS** (symlink present) | **PASS** (same tree) | **PASS** (symlink present) |

### Notes

- **Slash commands**: Installer skill names use underscores (`amir_install_mattpocock`). Cursor's skill authoring guide recommends hyphens in `name`; underscore commands may still work but were **NOT TESTED** in the Cursor UI.
- **Hermes agent id**: Use `hermes-agent` with the skills CLI (`hermes` is invalid).
- **Symlinks on Windows**: Default mode is symlink; junction/copy fallback is implemented in bootstrap for installer skills. Use `-ForceCopy` on `install-mattpocock.ps1` if symlink creation fails.
- **Plugin vs skills.sh**: Matt Pocock also ships Claude/Codex **plugins**; this installer uses **skills.sh / skills CLI** only, per task requirements.
- **Global install**: Intentionally **unsupported** (no `-g` flag used).

## Exit codes (`install-mattpocock.ps1`)

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Verification failed (missing SKILL.md) |
| 2 | Requested skill missing upstream |
| 3 | Skipped conflicts only |
