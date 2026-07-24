# amir — Visual Cockpit (VS Code / Cursor)

Side panel cockpit for the amir multi-agent project-execution plugin: **Project**, **Agents**, and **Tasks**.

JSON under `ai/state/` is the only data source. Mutations go through `node tools/state.js` (never direct JSON writes from this extension).

## Install

### From VSIX (VS Code or Cursor)

```powershell
code --install-extension amir-0.1.0.vsix
# or Cursor:
cursor --install-extension amir-0.1.0.vsix
```

Build locally:

```powershell
cd amir_marketplace/extensions/amir
npm install
npm run compile
npm run package
```

### Settings

| Setting | Purpose |
|---------|---------|
| `amir.pluginRoot` | Absolute path to amir plugin (contains `tools/` + `schemas/`). Auto-detects marketplace `plugins/amir` or sibling `Amir/` when empty. |
| `amir.defaultHost` | `claude` \| `cursor` \| `codex` |
| `amir.hostCli.*.binary` / `argsTemplate` | Host CLI paths; `{promptPath}` in args |
| `amir.watchDebounceMs` | State watcher debounce (default 250) |
| `amir.staleAfterMinutes` | Stale heartbeat threshold (default 5) |
| `amir.startAll.staggerMs` | Start All spacing (default 2000) |

If `tools/state.js` cannot be resolved, mutation buttons are disabled with a tooltip.

## Host CLI setup

1. Install at least one agent CLI on PATH (`claude`, `cursor-agent`, or `codex`).
2. Set `amir.defaultHost` and binaries under `amir.hostCli.*`.
3. **Start Agent** regenerates `prompt.md` via `generate-prompt`, then sends the launch line into `amir: <agent-id>` terminal.

**NOT SUPPORTED** (host missing): Start Agent falls back to printing the prompt path; Approve/Add Agent still work if `tools/state` is available.

## Cursor divergences

| Topic | Note |
|-------|------|
| Marketplace | Cursor uses Open VSX / VSIX sideload — not the Microsoft Marketplace |
| Extension API | Cursor declares ~VS Code 1.105; this extension targets `^1.74.0` |
| Chat APIs | Not used (avoid Cursor Chat Participant activation crashes) |
| `/btw` | Command `amir.btw` is functional only when `vscode.env.appName` contains `Cursor` |
| File watchers | Use `RelativePattern` with `/` globs; works with `E:\…` workspace roots |

## Manual smoke script

1. Open fixture folder `src/test/fixtures/amir-project` (or a real amir project).
2. Click amir activity bar → Project shows phase, pending approval, activity.
3. Agents tree lists orchestrator / qa / workers; click focuses terminal `amir: <id>`.
4. Tasks: `T001` above pending; open detail; Finished group collapsed.
5. Approve pending approval → `tools/state approve` → status updates &lt;1s.
6. Open a non-amir folder → empty state with Create / Docs.
7. Window reload → terminals re-associate by name `amir: …`.

## Development

```powershell
npm install
npm run compile
npm test
npm run watch   # rebuild on change
```

Unit tests cover task sort, JSONL offset tailing (incl. 50MB smoke), Windows path joins, and a grep gate against direct `ai/state` writes.

## Architecture

- `StateStore` + `createFileSystemWatcher('ai/state/**')` (debounced)
- `ActivityTail` byte-offset JSONL reader
- `StateCli` spawns `node <pluginRoot>/tools/state.js`
- New CLI commands (in amir plugin): `add-agent`, `delete-agent`, `approve`, `reject`, `set-agent-state`, `reset-agent`, `generate-prompt`
