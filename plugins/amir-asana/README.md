# amir-asana

Packed marketplace plugin for the Amir Asana connector (MCP + skills).

Source of truth: `../../asana/Amir_Asana_Claude`. Re-pack with:

```bash
node scripts/pack-amir-asana.js
```

## Setup

1. Ensure the source `.venv` exists (or create one in this packed folder):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
2. Credentials: `.env` with `ASANA_ACCESS_TOKEN=` (pack links source `.env` when present).
3. Install from **amir-marketplace** (Claude / Cursor / Codex).

## Cursor local

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.cursor\plugins\local" | Out-Null
cmd /c mklink /J "%USERPROFILE%\.cursor\plugins\local\amir-asana" "E:\PC3_Shared\Plugins\amir_marketplace\plugins\amir-asana"
```

Then Developer: Reload Window.
