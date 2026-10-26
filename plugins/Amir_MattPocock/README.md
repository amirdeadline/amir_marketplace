# Amir_MattPocock (amir marketplace plugin)

Install Matt Pocock's [agent skills](https://github.com/mattpocock/skills) **into the current project** using shared PowerShell installers:

| Skill | Command |
|---|---|
| Curated 13 engineering skills | `/amir_install_mattpocock` |
| All upstream skills (dynamic discovery) | `/amir_install_mattpocock_all` |

## Install plugin

**Claude Code**

```text
claude plugin marketplace add amirdeadline/amir_marketplace
claude plugin install Amir_MattPocock@amir-marketplace --scope user
```

**Cursor** — junction to this plugin directory under `%USERPROFILE%\.cursor\plugins\local\Amir_MattPocock`, then reload.

## Run installers (any host)

From the project root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:CLAUDE_PLUGIN_ROOT\scripts\install-mattpocock.ps1" -Mode Selected
```

On Cursor, substitute `$env:CURSOR_PLUGIN_ROOT` when set.

See `COMPATIBILITY.md` in this folder for agent paths and verification notes.
